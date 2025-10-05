import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from groq import Groq
import tempfile

# Load environment variables
load_dotenv()

# ---------------- Initialize Services ----------------
@st.cache_resource
def init_services():
    """Initialize Pinecone, embeddings, and Groq client"""
    pc = Pinecone(
        api_key=os.environ["PINECONE_API_KEY"],
        environment=os.environ["PINECONE_ENV"]
    )
    
    embeddings = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    return pc, embeddings, client

pc, embeddings, client = init_services()

INDEX_NAME = "rag-chatbot"
index = pc.Index(INDEX_NAME)
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 6})

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

st.title("📚 RAG Study Bot")
st.write("Ask questions about your notes and past papers!")

# Tabs for different sections
tab1, tab2 = st.tabs(["💬 Ask Questions", "📊 Database Info"])

with tab1:
    query = st.text_input("Enter your question:", key="query_input")

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
            
            # Generate answer using Groq
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant. Answer questions based on the provided context from study materials and past papers."},
                        {"role": "user", "content": f"""Context from study materials:
{context}

Question: {query}

Please provide a clear and concise answer based on the context above."""}
                    ],
                    temperature=0.7,
                    max_tokens=512
                )
                answer = response.choices[0].message.content
                st.success("✅ Answer generated successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                answer = "Unable to generate answer. Please check your Groq API key."
            
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
        
        # Show namespaces if any
        if hasattr(stats, 'namespaces') and stats.namespaces:
            st.subheader("Namespaces")
            for ns, ns_stats in stats.namespaces.items():
                st.write(f"- **{ns}**: {ns_stats.vector_count:,} vectors")
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
