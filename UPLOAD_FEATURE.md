# 📤 File Upload Feature - User Guide

## What's New?

Your RAG Study Bot now supports **uploading new PDFs anytime** through the web interface! No need to run `ingest.py` manually anymore.

## ✨ New Features

### 1. **Sidebar File Uploader**
- Upload multiple PDF files at once
- Drag & drop support
- Real-time processing feedback

### 2. **Database Statistics Tab**
- View total number of document chunks
- Check database capacity
- Monitor index status

### 3. **Source Citations**
- See which documents were used to answer your question
- View relevant text snippets
- Verify information accuracy

## 🎯 How to Use

### Uploading New Documents

1. **Open the app** (local or deployed)
2. **Look at the sidebar** on the left
3. **Click "Browse files"** or drag & drop PDFs
4. **Select multiple PDFs** if needed
5. **Click "Process & Add to Database"**
6. **Wait for confirmation** (you'll see balloons! 🎈)

### Asking Questions

1. **Go to "Ask Questions" tab**
2. **Type your question** in the input box
3. **Wait for the answer** (10-20 seconds)
4. **Check sources** by expanding "View Sources"

### Checking Database

1. **Go to "Database Info" tab**
2. **View statistics** about your documents
3. **Click "Refresh Stats"** to update
4. **Read usage instructions**

## 📊 What Happens Behind the Scenes?

When you upload a PDF:

1. **File is saved temporarily**
2. **PDF is loaded and parsed**
3. **Text is split into chunks** (800 characters each)
4. **Embeddings are created** (vector representations)
5. **Vectors are uploaded to Pinecone**
6. **Temporary file is deleted**
7. **Success message is shown**

## 💡 Tips & Best Practices

### For Best Results:

- **Upload clear, text-based PDFs** (not scanned images)
- **Use descriptive filenames** (they appear in sources)
- **Upload related documents together**
- **Wait for processing to complete** before asking questions
- **Ask specific questions** for better answers

### Performance Tips:

- **Local (Ollama)**: No limits, but slower processing
- **Cloud (Groq)**: Faster, but has rate limits (30 req/min)
- **Batch uploads**: Upload multiple files at once
- **File size**: Larger files take longer to process

## 🔄 Differences: Local vs Cloud

### Local Version (`app.py` with Ollama)
- ✅ No API rate limits
- ✅ Complete privacy
- ✅ Works offline (after setup)
- ⚠️ Requires Ollama installed
- ⚠️ Slower on older computers

### Cloud Version (`app_cloud.py` with Groq)
- ✅ Fast processing
- ✅ No local setup needed
- ✅ Works from anywhere
- ⚠️ Requires internet
- ⚠️ Rate limits (30 requests/min)

## 🚨 Troubleshooting

### "Error processing files"
- **Check PDF format**: Must be text-based, not scanned images
- **Check file size**: Very large files (>50MB) may timeout
- **Check internet**: Pinecone requires connection

### "No relevant documents found"
- **Upload more documents**: Database might be empty
- **Try different questions**: Be more specific
- **Check processing**: Make sure upload completed successfully

### "Unable to generate answer"
- **Local**: Make sure Ollama is running (`ollama serve`)
- **Cloud**: Check Groq API key in `.env` or Streamlit secrets
- **Both**: Check internet connection for Pinecone

## 📝 Example Workflow

```
1. Start the app
   → streamlit run app.py

2. Upload PDFs
   → Sidebar → Browse → Select files → Process

3. Wait for confirmation
   → ✅ Successfully added X chunks from Y file(s)!

4. Ask a question
   → "What are the key concepts in chapter 3?"

5. Get answer with sources
   → Answer displayed with source citations

6. Upload more documents anytime
   → Repeat step 2-3 as needed
```

## 🎓 Advanced Usage

### Managing Your Database

- **Check capacity**: Database Info tab shows fullness
- **Monitor vectors**: Each chunk = 1 vector
- **Free tier limit**: Pinecone free tier = 100,000 vectors
- **Estimate**: 1 PDF page ≈ 2-4 vectors

### Optimizing Performance

- **Chunk size**: Default 800 chars (good for most cases)
- **Overlap**: 150 chars ensures context continuity
- **Retrieval**: Top 6 chunks retrieved, top 3 used for answer
- **Context limit**: 2000 chars max sent to LLM

## 🔐 Security Notes

- **PDFs are temporary**: Deleted after processing
- **Only metadata stored**: Pinecone stores text + source filename
- **No file retention**: App doesn't keep uploaded files
- **API keys protected**: Never exposed in UI

## 📚 What's Stored in Pinecone?

For each document chunk:
```json
{
  "id": "id-12345",
  "vector": [0.123, 0.456, ...],  // 768 dimensions
  "metadata": {
    "text": "The actual text content...",
    "source": "filename.pdf"
  }
}
```

## 🎉 Benefits

- **No manual ingestion**: Upload directly through UI
- **Incremental updates**: Add documents without reprocessing
- **Multi-user ready**: Multiple people can upload (if deployed)
- **Persistent storage**: Documents stay in Pinecone
- **Easy management**: See what's in your database

---

Enjoy your enhanced RAG Study Bot! 🚀
