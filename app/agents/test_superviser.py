from app.agents.supervisor import SupervisorAgent
from app.agents.rag_tool import RAGTool

# Fake LLM for deterministic testing
def fake_llm(prompt: str) -> str:
    return "knowledge_query"

class FakeRAG:
    def run(self, user_query, history, db):
        return {
            "answer": "FAKE_RAG_RESPONSE",
            "escalate_to_human": False,
            "context_docs": [],
        }

rag_tool = FakeRAG()
supervisor = SupervisorAgent(rag_tool=rag_tool, llm=fake_llm)

result = supervisor.handle(
    user_query="How do I reset my password?",
    history=[],
    db=None,
)

print(result)
