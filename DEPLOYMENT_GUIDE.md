# RAG Study Bot - Deployment Guide

## 🚀 Deploy to Streamlit Community Cloud (Recommended)

### Prerequisites
1. GitHub account
2. Groq API key (free at https://console.groq.com)
3. Pinecone API key (you already have this)
4. Your PDFs already uploaded to Pinecone (run `ingest.py` locally first)

### Step 1: Get Groq API Key (Free)

1. Go to https://console.groq.com
2. Sign up with Google/GitHub
3. Click "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)

### Step 2: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   cd "c:\Users\Ayush Singh\Desktop\rag-xchatbpt"
   git init
   git add .
   git commit -m "Initial commit - RAG Study Bot"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name it: `rag-study-bot`
   - Make it **Private** (to protect your API keys)
   - Don't initialize with README
   - Click "Create repository"

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/rag-study-bot.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Rename Files for Deployment

Rename the cloud-ready files:
```bash
move app.py app_local.py
move app_cloud.py app.py
move requirements.txt requirements_local.txt
move requirements_cloud.txt requirements.txt
```

### Step 4: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - **Repository**: `YOUR_USERNAME/rag-study-bot`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click "Advanced settings"
6. Add your secrets (environment variables):
   ```toml
   PINECONE_API_KEY = "your_pinecone_key"
   PINECONE_ENV = "us-east-1-aws"
   GROQ_API_KEY = "your_groq_key"
   ```
7. Click "Deploy!"

### Step 5: Wait for Deployment

- First deployment takes 5-10 minutes
- You'll get a URL like: `https://your-app.streamlit.app`
- Share this URL with anyone!

---

## 🐳 Alternative: Deploy with Docker (Self-Hosted)

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements_cloud.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app_cloud.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deploy:
```bash
docker build -t rag-study-bot .
docker run -p 8501:8501 --env-file .env rag-study-bot
```

---

## 🌐 Alternative: Deploy to Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run app_cloud.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Deploy:
   ```bash
   heroku create rag-study-bot
   heroku config:set PINECONE_API_KEY=your_key
   heroku config:set PINECONE_ENV=us-east-1-aws
   heroku config:set GROQ_API_KEY=your_key
   git push heroku main
   ```

---

## 🔧 Troubleshooting

### "Module not found" errors
- Make sure `requirements.txt` is correct
- Redeploy the app

### "No documents found"
- Run `ingest.py` locally first to upload PDFs to Pinecone
- Pinecone is cloud-based, so once uploaded, it works from anywhere

### API rate limits
- Groq free tier: 30 requests/minute
- Consider upgrading or switching to OpenAI

---

## 📊 Cost Estimate

**Streamlit Cloud Deployment:**
- Streamlit hosting: **FREE**
- Groq API: **FREE** (30 req/min)
- Pinecone: **FREE** tier (1 index, 100K vectors)

**Total: $0/month** 🎉

---

## 🔒 Security Notes

1. **Never commit `.env` file** (already in `.gitignore`)
2. **Use Streamlit secrets** for production
3. **Make GitHub repo private** if it contains sensitive data
4. **Rotate API keys** if accidentally exposed

---

## 📝 Post-Deployment

After deployment, test your app:
1. Visit your Streamlit Cloud URL
2. Ask a question from your study materials
3. Verify it retrieves relevant documents
4. Check the answer quality

Enjoy your deployed RAG Study Bot! 🚀
