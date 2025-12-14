# app/agents/rag_tool.py

from app.services import chat_service

class RAGTool:
    def run(self, user_query, history, db):
        return chat_service.answer_with_rag(
            user_query=user_query,
            history=history,
            db=db,
        )
