# 📚 RAG Study Bot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions based on your study materials and past papers using AI.

## 🌟 Features

- 📄 **PDF Processing**: Upload and process multiple PDF documents
- 🔍 **Smart Search**: Uses vector similarity search to find relevant content
- 🤖 **AI-Powered Answers**: Generates accurate answers using LLMs
- 💾 **Cloud Storage**: Stores embeddings in Pinecone vector database
- 🎨 **Beautiful UI**: Clean Streamlit interface

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Vector DB**: Pinecone
- **Embeddings**: Sentence Transformers (all-mpnet-base-v2)
- **LLM**: Groq (Llama 3.1) / Ollama (local)
- **Framework**: LangChain

## 🚀 Quick Start

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rag-study-bot.git
   cd rag-study-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create `.env` file:
   ```
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENV=us-east-1-aws
   GROQ_API_KEY=your_groq_key
   ```

4. **Add your PDFs**:
   Place your study materials in the `papers/` folder

5. **Ingest documents**:
   ```bash
   python ingest.py
   ```

6. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## 📦 Project Structure

```
rag-xchatbpt/
├── app.py                 # Main Streamlit app (local with Ollama)
├── app_cloud.py          # Cloud-ready version (with Groq)
├── ingest.py             # PDF ingestion script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── papers/               # Your PDF documents
└── DEPLOYMENT_GUIDE.md   # Deployment instructions
```

## 🌐 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

**Quick Deploy to Streamlit Cloud:**
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets (API keys)
4. Deploy!

## 🔑 API Keys Required

1. **Pinecone**: https://www.pinecone.io (Free tier available)
2. **Groq**: https://console.groq.com (Free API)

## 📖 Usage

1. Upload your study materials (PDFs) to the `papers/` folder
2. Run `python ingest.py` to process and upload to Pinecone
3. Start the app with `streamlit run app.py`
4. Ask questions about your study materials!

## 🎯 Example Questions

- "What are the key concepts in [topic]?"
- "Explain [specific concept] from the notes"
- "What are the important formulas for [subject]?"
- "Summarize the chapter on [topic]"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for your studies!

## 🙏 Acknowledgments

- LangChain for the RAG framework
- Pinecone for vector storage
- Groq for fast LLM inference
- Streamlit for the amazing UI framework

---

Made by Ayush Singh for students
