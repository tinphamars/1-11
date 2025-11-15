# RAG Chatbot API

Intelligent chatbot API using **RAG (Retrieval-Augmented Generation)** technique to answer questions based on project documents accurately and efficiently.

## 🚀 Key Features
- 🧠 Automatic document processing from `documents/` folder
- 💬 Interactive chat with documents for Q&A
- 📄 Multi-format support: `.py`, `.md`, `.txt`, `.json`, `.yml`, `.docx`, `.pdf`
- 🐳 Easy deployment with Docker
- ⚡ Real-time processing with vector database

---

## ⚙️ Quick Start

### 1. Environment Configuration
Create `.env` file in root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.l
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_TYPE=openai

# Application Settings
DOCUMENTS_FOLDER=./documents
AUTO_LOAD_ON_STARTUP=true
RETRIEVAL_K=5
DEFAULT_TEMPERATURE=0.7
```

### 2. Run with Docker
```bash
docker compose up -d --build
```

### 3. Check Operation
Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💬 API Usage

### Chat with documents
```bash
POST http://localhost:8000/chat

{
  "message": "How do I install this project?",
  "temperature": 0.7
}
```

### Refresh documents
When adding/modifying files in `documents/`:

```bash
POST http://localhost:8000/documents/refresh
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------|
| GET | `/` | API information |
| GET | `/health` | System health check |
| POST | `/chat` | Chat with documents |
| POST | `/documents/refresh` | Refresh documents |
| GET | `/documents/status` | View database status |
| GET | `/documents/folder-info` | View folder information |
| DELETE | `/documents/clear` | Delete all documents |

Full API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Detailed Configuration

### OpenAI Setup
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.l
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_TYPE=openai
```

### Application Customization
```env
# Document folder path
DOCUMENTS_FOLDER=./documents

# Auto-load on startup
AUTO_LOAD_ON_STARTUP=true

# Number of relevant documents to retrieve
RETRIEVAL_K=5

# Model creativity (0.0 - 1.0)
DEFAULT_TEMPERATURE=0.7
```

---

## 🧩 Troubleshooting

### Common Connection Errors

| Error | Solution |
|------|------------|
| Wrong API Key | Check `OPENAI_API_KEY` |
| Incorrect URL | Verify `OPENAI_BASE_URL` |
| Network issues | Check network connection to endpoint |

### Check Logs
```bash
# View real-time logs
docker compose logs -f rag-chatbot-api

# View logs with timestamps
docker compose logs -t rag-chatbot-api
```

---

## 🗂️ Project Structure
```text
AI_ab/
├── app/                  # Main application code
├── documents/            # Document storage folder
├── chroma_db/            # Vector database (auto-created)
├── .env                  # Configuration file (create manually)
├── docker-compose.yml    # Docker compose configuration
└── Dockerfile            # Docker image build file
```

---

## ⚠️ Important Notes
- Documents are stored in **ChromaDB vector database**
- Chat history is saved in **memory** (lost when service restarts)
- For **production** use, replace memory storage with a real **database**
- Recommend **backing up important data** in `documents/` folder
