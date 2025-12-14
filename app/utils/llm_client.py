from openai import OpenAI
from app.services.config import settings

# Create client once (important for performance)
_client = None
if settings.OPENAI_API_KEY:
    _client = OpenAI(api_key=settings.OPENAI_API_KEY)


def call_llm(prompt: str) -> str:
    """
    Generic LLM call utility.
    Used by:
    - SupervisorAgent (intent classification)
    - QueryRewriter
    - Future lightweight agents

    This should NOT be used for RAG answers.
    """

    if _client is None:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Cannot call LLM."
        )

    response = _client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Follow instructions precisely.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.0,   # deterministic for agents
    )

    return response.choices[0].message.content.strip()
