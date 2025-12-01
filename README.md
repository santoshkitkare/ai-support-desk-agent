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
Client → FastAPI → LLM Request Handler → GPT/Claude
      ↓
Embedding Engine
      ↓
FAISS Index
      ↓
Knowledge Base (PDF/CSV/DOCX)

### 📂 Project Structure
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

### 📩 Contact
For enterprise deployment or integration requests, feel free to connect.
