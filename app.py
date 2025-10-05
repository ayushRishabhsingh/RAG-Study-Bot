import os
import streamlit as st
import requests
from dotenv import load_dotenv
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone
import tempfile

# Load environment variables
load_dotenv()

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="RAG Study Bot", page_icon="📚", layout="wide")

# Sidebar for file upload
with st.sidebar:
    st.header("📤 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload your study materials and past papers"
    )
    
    if uploaded_files:
        if st.button("Process & Add to Database", type="primary"):
            with st.spinner("Processing PDFs..."):
                process_uploaded_files(uploaded_files)
    
    st.markdown("---")
    st.subheader("⚙️ Settings")
    st.info("Using Ollama (Local LLM)\nNo API limits!")

st.title("📚 RAG Study Bot")
st.write("Ask questions about your notes and past papers!")

# Tabs for different sections
tab1, tab2 = st.tabs(["💬 Ask Questions", "📊 Database Info"])

with tab1:
    query = st.text_input("Enter your question:", key="query_input")

# ---------------- Pinecone & LangChain ----------------
pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENV"]  # ← make sure this matches your index
)

INDEX_NAME = "rag-chatbot"
index = pc.Index(INDEX_NAME)

embeddings = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 6})

# Ollama local API setup
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# ---------------- Helper Functions ----------------
def process_uploaded_files(uploaded_files):
    """Process uploaded PDF files and add to Pinecone"""
    try:
        all_chunks = []
        
        for uploaded_file in uploaded_files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            
            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
            chunks = splitter.split_documents(docs)
            
            # Add source filename to metadata
            for chunk in chunks:
                chunk.metadata['source'] = uploaded_file.name
            
            all_chunks.extend(chunks)
            
            # Clean up temp file
            os.unlink(tmp_path)
        
        # Get current vector count for unique IDs
        stats = index.describe_index_stats()
        current_count = stats.total_vector_count
        
        # Create embeddings and upsert to Pinecone
        batch = []
        for i, chunk in enumerate(all_chunks):
            vec = embeddings.embed_query(chunk.page_content)
            meta = {
                "text": chunk.page_content,
                "source": chunk.metadata.get("source", "unknown")
            }
            batch.append((f"id-{current_count + i}", vec, meta))
            
            if len(batch) >= 64:
                index.upsert(vectors=batch)
                batch = []
        
        if batch:
            index.upsert(vectors=batch)
        
        st.success(f"✅ Successfully added {len(all_chunks)} chunks from {len(uploaded_files)} file(s)!")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")

def get_database_stats():
    """Get statistics about the Pinecone database"""
    try:
        stats = index.describe_index_stats()
        return stats
    except Exception as e:
        return None

# ---------------- Query & Display ----------------
    if query:
        with st.spinner("Searching your notes... 🔍"):
            # Retrieve relevant documents
            docs = retriever.get_relevant_documents(query)
            
            # Show what was retrieved
            st.info(f"📚 Found {len(docs)} relevant document chunks")
            
            if len(docs) == 0:
                st.warning("⚠️ No relevant documents found. Please upload PDFs using the sidebar.")
                st.stop()
            
            # Combine context from retrieved documents (limit to top 3)
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
            
            # Truncate context if too long
            if len(context) > 2000:
                context = context[:2000] + "..."
            
            # Generate answer using Ollama
            try:
                prompt = f"""Answer this question based on the context provided.

Context: {context}

Question: {query}

Answer:"""
                
                # Try different model name formats
                models_to_try = ["llama3.2:latest", "gemma3:4b", "llama3.2", "llama2"]
                
                answer = None
                for model_name in models_to_try:
                    payload = {
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.5,
                            "num_predict": 256,
                            "num_ctx": 2048
                        }
                    }
                    
                    response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("response", "No answer generated.")
                        st.success(f"✅ Using model: {model_name}")
                        break
                    elif response.status_code == 404:
                        continue
                    else:
                        st.error(f"Ollama Error: {response.status_code}")
                        break
                
                if answer is None:
                    st.error(f"❌ None of these models found: {', '.join(models_to_try)}")
                    st.info("Run `ollama list` in terminal to see available models")
                    answer = "No compatible model found. Please check your Ollama installation."
            except requests.exceptions.Timeout:
                st.error("⏱️ Ollama took too long to respond.")
                answer = "Request timed out. Consider using a smaller/faster model."
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Ollama. Please make sure Ollama is running.")
                answer = "**Setup Required:** Please install and start Ollama."
            except Exception as e:
                st.error(f"Error: {str(e)}")
                answer = "Unable to generate answer. Please check Ollama setup."
            
        st.markdown(f"**Answer:** {answer}")
        
        # Show sources
        with st.expander("📄 View Sources"):
            for i, doc in enumerate(docs[:3], 1):
                st.markdown(f"**Source {i}:** {doc.metadata.get('source', 'Unknown')}")
                st.text(doc.page_content[:300] + "...")
                st.divider()

# Database Info Tab
with tab2:
    st.header("📊 Database Statistics")
    
    if st.button("Refresh Stats", type="secondary"):
        st.rerun()
    
    stats = get_database_stats()
    
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Vectors", f"{stats.total_vector_count:,}")
        
        with col2:
            st.metric("Dimension", stats.dimension)
        
        with col3:
            st.metric("Index Fullness", f"{stats.index_fullness:.2%}")
        
        st.info("💡 Each vector represents a chunk of text from your study materials.")
    else:
        st.error("Unable to fetch database statistics.")
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 How to Use")
    st.markdown("""
    1. **Upload PDFs**: Use the sidebar to upload your study materials
    2. **Process Files**: Click 'Process & Add to Database' to add them
    3. **Ask Questions**: Go to the 'Ask Questions' tab and type your query
    4. **Get Answers**: The AI will search your documents and provide answers
    
    **Tips:**
    - Upload multiple files at once for faster processing
    - Ask specific questions for better answers
    - Check the sources to verify the information
    """)
