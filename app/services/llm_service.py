import requests
import json

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def interpret_question(question: str):
    """
    Convert a natural-language question into a structured query intent.
    The actual numerical result is calculated by Python/Pandas.
    """

    prompt = f"""
You are an intent parser for a support ticket analytics system.

Convert the user's question into JSON.

Supported intents:
- count_tickets
- average_rating
- most_resolved_agent
- lowest_rating_agent
- average_resolution_time
- anomalies

Possible filters:
- status: Open, Resolved, Escalated
- priority: Low, Medium, High, Critical
- category: Technical, Billing, Account, etc.

Return ONLY valid JSON.

Examples:

Question: How many open tickets are there?
{{"intent":"count_tickets","status":"Open"}}

Question: How many critical tickets are unresolved?
{{"intent":"count_tickets","priority":"Critical","status":"unresolved"}}

Question: What is the average rating for Technical tickets?
{{"intent":"average_rating","category":"Technical"}}

Question: Which agent resolved the most tickets?
{{"intent":"most_resolved_agent"}}

Question: Which agent has the lowest average rating?
{{"intent":"lowest_rating_agent"}}

Question: What is the average resolution time?
{{"intent":"average_resolution_time"}}

Question: Any anomalies in resolution times?
{{"intent":"anomalies"}}

User question:
{question}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()
        text = data.get("response", "").strip()

        return json.loads(text)

    except Exception as e:
        return {
            "error": str(e),
            "intent": None,
        }