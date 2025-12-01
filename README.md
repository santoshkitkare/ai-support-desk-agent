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
