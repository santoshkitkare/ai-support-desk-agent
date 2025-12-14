import re

class GuardrailAgent:
    def __init__(self, llm):
        self.llm = llm

    def check(self, user_query: str) -> dict:
        """
        Returns:
        {
          "allowed": bool,
          "reason": str | None
        }
        """

        # ---- Rule-based checks (fast path) ----
        if self._detect_prompt_injection(user_query):
            return {
                "allowed": False,
                "reason": "Prompt injection attempt detected.",
            }

        if self._detect_pii(user_query):
            return {
                "allowed": False,
                "reason": "Sensitive personal information detected.",
            }

        if self._detect_unsafe_instruction(user_query):
            return {
                "allowed": False,
                "reason": "Unsafe or disallowed instruction detected.",
            }

        # ---- Optional LLM-based check (slow path) ----
        if self._llm_guardrail_check(user_query):
            return {
                "allowed": False,
                "reason": "Query violates safety or policy constraints.",
            }

        return {"allowed": True, "reason": None}

    # ---------------- Rule-based detectors ----------------

    def _detect_prompt_injection(self, text: str) -> bool:
        patterns = [
            r"ignore previous instructions",
            r"disregard the above",
            r"system prompt",
            r"you are now",
            r"act as",
        ]
        text_lower = text.lower()
        return any(p in text_lower for p in patterns)

    def _detect_pii(self, text: str) -> bool:
        pii_patterns = [
            r"\b\d{12}\b",                      # Aadhaar-like
            r"\b\d{3}-\d{2}-\d{4}\b",            # SSN
            r"\b\d{10}\b",                       # phone
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # email
        ]
        return any(re.search(p, text) for p in pii_patterns)

    def _detect_unsafe_instruction(self, text: str) -> bool:
        unsafe_keywords = [
            "hack",
            "bypass security",
            "exploit",
            "steal credentials",
            "malware",
        ]
        text_lower = text.lower()
        return any(k in text_lower for k in unsafe_keywords)

    # ---------------- LLM-based safety check ----------------

    def _llm_guardrail_check(self, query: str) -> bool:
        prompt = f"""
        You are a safety classifier.
        Determine whether the following user input violates safety,
        policy, or ethical guidelines.

        Respond ONLY with:
        - ALLOW
        - BLOCK

        User input:
        {query}
        """
        decision = self.llm(prompt).strip().upper()
        return decision == "BLOCK"
