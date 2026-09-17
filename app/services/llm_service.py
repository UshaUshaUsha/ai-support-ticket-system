import json
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


def classify_query(query: str) -> dict:
    """
    Use the local LLM to understand the user's natural-language query
    and convert it into a structured intent.
    """

    prompt = f"""
You are an intent classifier for an AI support ticket analytics system.

The available intents are:

1. open_ticket_count
2. resolved_ticket_count
3. critical_ticket_count
4. average_technical_rating
5. agent_most_resolved
6. anomaly_detection
7. unsupported

Return ONLY valid JSON.

The JSON format must be:

{{
    "intent": "one_of_the_intents_above"
}}

User question:
{query}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        result = response.json()

        llm_response = result.get("response", "{}")

        parsed = json.loads(llm_response)

        intent = parsed.get("intent", "unsupported")

        return {
            "intent": intent,
            "source": "llm",
        }

    except Exception as exc:
        return {
            "intent": "unsupported",
            "source": "fallback",
            "error": str(exc),
        }


if __name__ == "__main__":
    test_questions = [
        "How many tickets are currently open?",
        "How many tickets are resolved?",
        "What is the average customer rating for Technical tickets?",
        "Which agent resolved the most tickets?",
        "Are there any anomalies?",
    ]

    for question in test_questions:
        print("\nQuestion:", question)
        print("Result:", classify_query(question))