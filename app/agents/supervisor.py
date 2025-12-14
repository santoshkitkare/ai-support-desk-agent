# app/agents/supervisor.py

class SupervisorAgent:
    def __init__(self, rag_tool, llm):
        self.rag_tool = rag_tool
        self.llm = llm

    def classify_intent(self, query: str) -> str:
        prompt = f"""
        Classify intent as one of:
        - knowledge_query
        - small_talk
        - out_of_scope

        Query: {query}
        Return only the label.
        """
        return self.llm(prompt).strip().lower()

    def handle(self, user_query, history, db):
        intent = self.classify_intent(user_query)

        if intent == "knowledge_query":
            return self.rag_tool.run(user_query, history, db)

        if intent == "small_talk":
            return {
                "answer": "Hey! I’m here to help with support questions.",
                "escalate_to_human": False,
                "context_docs": [],
            }

        return {
            "answer": "This request is outside the supported scope.",
            "escalate_to_human": False,
            "context_docs": [],
        }
