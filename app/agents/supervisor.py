
# app/agents/supervisor.py

class SupervisorAgent:
    CONFIDENCE_THRESHOLD = 0.65

    def __init__(self, rag_tool, llm, rewriter):
        self.rag_tool = rag_tool
        self.llm = llm
        self.rewriter = rewriter

    def handle(self, user_query, history, db):
        # ---- Step 1: Intent classification ----
        intent = self._classify_intent(user_query)

        if intent == "small_talk":
            return {
                "answer": "Hey! I’m here to help with support-related questions.",
                "escalate_to_human": False,
                "context_docs": [],
            }

        if intent == "out_of_scope":
            return {
                "answer": "This request is outside the supported scope.",
                "escalate_to_human": False,
                "context_docs": [],
            }

        # ---- Step 2: RAG Attempt #1 ----
        first = self.rag_tool.run(user_query, history, db)

        if self._is_confident(first):
            return first
        
        print("Retrying...")

        # ---- Step 3: Retry with rewritten query ----
        rewritten = self.rewriter.rewrite(user_query)
        second = self.rag_tool.run(rewritten, history, db)

        # ---- Step 4: Pick best answer ----
        return self._pick_best(first, second)

    # ---------------- Helpers ----------------

    def _classify_intent(self, query: str) -> str:
        prompt = f"""
        Classify the intent of the following user query as ONE of:
        - knowledge_query
        - small_talk
        - out_of_scope

        Query:
        {query}

        Return only the label.
        """
        return self.llm(prompt).strip().lower()

    def _is_confident(self, result: dict) -> bool:
        if result.get("escalate_to_human"):
            return False
        return result.get("confidence", 0.0) >= self.CONFIDENCE_THRESHOLD

    def _pick_best(self, first: dict, second: dict) -> dict:
        return second if second.get("confidence", 0) > first.get("confidence", 0) else first
    


# MAX_RETRIES = 1          # Phase 2 = single retry
# CONFIDENCE_THRESHOLD = 0.65

# class SupervisorAgent:
#     def __init__(self, rag_tool, llm, rewriter):
#         self.rag_tool = rag_tool
#         self.llm = llm
#         self.rewriter = rewriter

#     def classify_intent(self, query: str) -> str:
#         prompt = f"""
#         Classify intent as one of:
#         - knowledge_query
#         - small_talk
#         - out_of_scope

#         Query: {query}
#         Return only the label.
#         """
#         return self.llm(prompt).strip().lower()

#     def handle(self, user_query, history, db):
#         intent = self.classify_intent(user_query)

#         if intent == "knowledge_query":
#             result = self.rag_tool.run(user_query, history, db)
#             print(f"Result 1 : {result}")
#             if self._is_confident(result):
#                 print(f"Returning Result 1 : {result}")
#                 return result

#             print(f"Retrying...")
#             # ---- Retry Logic ----
#             rewritten_query = self.rewriter.rewrite(user_query)
#             print(f"Rewritten Query: {rewritten_query}")

#             retry_result = self.rag_tool.run(rewritten_query, history, db)
#             print(f"Retry Result  : {result}")
            
#             # ---- Pick Best Answer ----
#             return self._pick_best(result, retry_result)

#         if intent == "small_talk":
#             return {
#                 "answer": "Hey! I’m here to help with support questions.",
#                 "escalate_to_human": False,
#                 "context_docs": [],
#             }

#         return {
#             "answer": "This request is outside the supported scope.",
#             "escalate_to_human": False,
#             "context_docs": [],
#         }

#     def _is_confident(self, result: dict) -> bool:
#         if result.get("escalate_to_human"):
#             return False
#         return result.get("confidence", 0.0) >= 0.65

#     def _pick_best(self, first: dict, second: dict) -> dict:
#         # Prefer higher confidence
#         print("Checking Result confidence...")
#         if second.get("confidence", 0) > first.get("confidence", 0):
#             print("Return second")
#             return second
#         print("Return second")
#         return first