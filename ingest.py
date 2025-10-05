import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# -------------------------------------------------------------------
# 1) Load PDFs
# -------------------------------------------------------------------
docs = []
folder_path = "./papers"
for file_name in os.listdir(folder_path):
    if file_name.endswith(".pdf"):
        pdf_path = os.path.join(folder_path, file_name)
        print(f"📄 Loading {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        docs.extend(loader.load())

# -------------------------------------------------------------------
# 2) Chunk documents
# -------------------------------------------------------------------
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
chunks = splitter.split_documents(docs)

# -------------------------------------------------------------------
# 3) Embeddings
# -------------------------------------------------------------------
sbert = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
def embed_texts(texts):
    return sbert.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# -------------------------------------------------------------------
# 4) Init Pinecone v3 client
# -------------------------------------------------------------------
pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENV"]  # ← make sure this matches your index
)


INDEX_NAME = "rag-chatbot"
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # adjust region if needed
    )

index = pc.Index(INDEX_NAME)

# -------------------------------------------------------------------
# 5) Upsert embeddings
# -------------------------------------------------------------------
batch = []
for i, doc in enumerate(chunks):
    vec = embed_texts([doc.page_content])[0]
    # Store the actual text content in metadata so it can be retrieved
    meta = {
        "text": doc.page_content,
        "source": doc.metadata.get("source", "unknown")
    }
    batch.append((f"id-{i}", vec.tolist(), meta))
    if len(batch) >= 64:
        index.upsert(vectors=batch)
        batch = []
if batch:
    index.upsert(vectors=batch)

print(f"✅ Uploaded {len(chunks)} chunks to Pinecone index '{INDEX_NAME}'")
