class QueryRewriter:
    def __init__(self, llm):
        self.llm = llm

    def rewrite(self, original_query: str) -> str:
        prompt = f"""
        Rewrite the following support question to be more specific,
        factual, and searchable in a knowledge base.

        Original question:
        {original_query}

        Rewritten question:
        """
        rewritten = self.llm(prompt).strip()
        return rewritten[:300]  # avoid runaway prompts
