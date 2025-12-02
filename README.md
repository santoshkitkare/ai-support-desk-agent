# AI Support Desk Agent (LLM Powered Customer Support Automation)

### 🚀 Overview
The AI Support Desk Agent reduces customer support workload by providing instant, context-aware responses using company knowledge base documents (PDF, DOCX, CSV, FAQ pages).  
It acts as a first-line support system and can escalate to a human agent when required.

### 💡 Key Features
- GPT/Claude powered conversational AI
- Upload internal documents as knowledge base
- Vector search using FAISS for context-aware answers
- Fallback "Escalate to Human" mode
- Chat history & memory retention
- API-first design — can be plugged into websites, CRMs, or support platforms

### 🧠 Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| LLM | GPT / Claude |
| Embeddings | OpenAI / SentenceTransformers |
| Vector DB | FAISS |
| Deployment | AWS (ECS / EC2) + Docker |

### 🏗 Architecture
```
Client → Streamlit UI ← Upload docs / Chat / Dashboard
      ↓
      ↓  REST API
      ↓
FastAPI Backend
      ↓
      ↓
Embedding Engine
      ↓
      ↓
FAISS Index
      ↓
      ↓
Knowledge Base (PDF/CSV/DOCX)
      ↓
      ↓
      ↓
Conversation DB <-- For chat history & analytics
```

### 🚀 Features

| Module                             | Status |
| ---------------------------------- | ------ |
| Document upload (PDF/DOCX/CSV/TXT) | ✅     |
| Text extraction & chunking         | ✅     |
| HuggingFace embeddings             | ✅     |
| FAISS similarity search            | ✅     |
| LLM answer generation (OpenAI)     | ✅     |
| Conversation history               | ✅     |
| Analytics dashboard                | ✅     |
| Escalation to human flag           | 🔜     |
| Auth / Multi-tenant SaaS           | 🔜     |


### 🧰 Tech Stack

| Layer              | Tech                                 |
| ------------------ | ------------------------------------ |
| Frontend           | Streamlit                            |
| Backend            | FastAPI                              |
| LLM                | OpenAI + HuggingFace embeddings      |
| Vector DB          | FAISS                                |
| Persistence        | SQLite / PostgreSQL (both supported) |
| Containerization   | Docker (optional)                    |
| Deployment options | AWS EC2 / Streamlit Cloud / Dockers  |


### 📂 Project Structure
```
ai-support-agent/
┣ app/
┃ ┣ routers/
┃ ┣ services/
┃ ┣ utils/
┃ ┗ main.py
┣ data/
┣ Dockerfile
┣ requirements.txt
┗ README.md
```


### 📌 How It Works
1. User uploads company documents
2. Documents are chunked + converted to embeddings
3. User enters a support query
4. System searches FAISS for relevant context
5. GPT/Claude generates an accurate, cited answer

### 🧪 Sample Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-docs/` | Upload support knowledge base |
| POST | `/chat/` | Chat with support agent |
| GET | `/history/` | Retrieve conversation history |

### 🚀 Deployment
docker build -t ai-support-agent .
docker run -p 8000:8000 ai-support-agent

For AWS deployment: ECS + Load Balancer + ECR + CloudWatch.
---

### 🤝 Ideal Use Cases
- Customer support automation
- HR / IT helpdesk
- SaaS in-product support agents
- Enterprise documentation Q&A

⚙️ Local Setup
1️⃣ Clone the repository
```
git clone https://github.com/<your_user>/ai-support-desk-agent.git
cd ai-support-desk-agent
```
2️⃣ Create virtual environment
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
3️⃣ Install dependencies
```
pip install -r requirements.txt
```

4️⃣ Add environment variables
Create .env in project root:
```
OPENAI_API_KEY=xxxxxxxxxxxx
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```
5️⃣ Start the backend
```
uvicorn app.main:app --reload
```

6️⃣ Start the UI
```
streamlit run frontend/app.py
```
### 🧪 API Reference
| Method | Endpoint                      | Description                                     |
| ------ | ----------------------------- | ----------------------------------------------- |
| `POST` | `/docs/upload`                | Upload and index documents                      |
| `POST` | `/chat`                       | LLM chat with RAG                               |
| `GET`  | `/analytics/summary`          | Stats: conversations / escalations / resolution |
| `GET`  | `/analytics/trending-queries` | Last 5 queries                                  |

### Open Swagger docs:
```
http://localhost:8000/docs
```

### 🤝 Contributing

PRs and feature requests are welcome. Feel free to fork the repo and improve it.

### ⭐ Future Enhancements (roadmap)
* Slack / Email escalation when LLM flags “escalate_to_human”
* Authentication + multi-tenant support
* Admin panel for knowledge-base management
* Billing tiers for SaaS customers

### 📄 License
MIT — free to use and modify.

### 🧑‍💻 Author
Built with ❤️ by Santosh Itkare

### 📩 Contact
For enterprise deployment or integration requests, feel free to connect.
