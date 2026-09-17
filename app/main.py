# # But how do you know what each file is for?

# Think of the project as different responsibilities:

# Folder/File	                           What we use it for
# data/	                                   Dataset
# support_tickets.csv	                   Your support-ticket data
# app/	                                   Main Python backend
# main.py	                               FastAPI application/API endpoints
# config.py	                               Configuration and environment variables
# models/schemas.py	                       Pydantic data/request/response structures
# services/data_service.py	               Load and work with CSV data
# services/query_service.py	               Answer ticket-related questions
# services/anomaly_service.py	           Detect unusual/anomalous tickets
# services/llm_service.py	               Gemini/LLM integration
# utils/helpers.py	                       Reusable helper functions
# ui/streamlit_app.py	                   User interface
# tests/	                               Automated tests
# test_api.py	                           Test API
# test_anomaly.py	                       Test anomaly detection
# test_queries.py	                       Test query functionality
# requirements.txt	                       Python packages
# .env.example	                           Shows required environment variables
# README.md	                               Explains the project and how to run it

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.llm_service import interpret_question

from app.services.data_service import load_tickets
from app.services.query_service import (
    count_tickets,
    average_customer_rating,
    agent_with_most_resolved_tickets,
    agent_with_lowest_average_rating,
    average_resolution_time,
)
from app.services.anomaly_service import (
    get_anomaly_summary,
    detect_all_anomalies,
)


app = FastAPI(
    title="AI Support Ticket System",
    description="AI-powered support ticket analysis and anomaly detection API",
    version="1.0.0",
)


# Load dataset once when the API starts
tickets = load_tickets()


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "tickets_loaded": len(tickets),
    }


@app.get("/anomalies")
def get_anomalies():
    results = detect_all_anomalies(tickets)

    return {
        "summary": get_anomaly_summary(tickets),
        "long_resolution_anomalies": (
            results["long_resolution_anomalies"]
            .to_dict(orient="records")
        ),
        "old_high_priority_anomalies": (
            results["old_high_priority_anomalies"]
            .to_dict(orient="records")
        ),
    }


@app.post("/query")
def query_tickets(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Try LLM interpretation first
    llm_result = interpret_question(question)

    # If Ollama is available, use its structured intent
    if llm_result.get("intent"):
        intent = llm_result["intent"]

        if intent == "count_tickets":
            status = llm_result.get("status")
            priority = llm_result.get("priority")

            if status == "unresolved":
                result = count_tickets(
                    tickets,
                    priority=priority
                )
                result = len(
                    tickets[
                        (tickets["priority"] == priority)
                        & (tickets["status"] != "Resolved")
                    ]
                )

            else:
                result = count_tickets(
                    tickets,
                    status=status,
                    priority=priority
                )

            return {
                "question": question,
                "answer": f"There are {result} matching tickets.",
                "result": result,
                "source": "LLM + Python"
            }

        if intent == "average_rating":
            category = llm_result.get("category")

            result = average_customer_rating(
                tickets,
                category=category
            )

            return {
                "question": question,
                "answer": f"The average customer rating is {result:.2f}.",
                "result": result,
                "source": "LLM + Python"
            }

        if intent == "most_resolved_agent":
            result = agent_with_most_resolved_tickets(tickets)

            return {
                "question": question,
                "answer": (
                    f"Agent {result['agent_id']} resolved "
                    f"{result['resolved_ticket_count']} tickets."
                ),
                "result": result,
                "source": "LLM + Python"
            }

        if intent == "lowest_rating_agent":
            result = agent_with_lowest_average_rating(tickets)

            return {
                "question": question,
                "answer": (
                    f"Agent {result['agent_id']} has the lowest "
                    f"average rating of {result['average_rating']:.2f}."
                ),
                "result": result,
                "source": "LLM + Python"
            }

        if intent == "average_resolution_time":
            result = average_resolution_time(tickets)

            return {
                "question": question,
                "answer": (
                    f"The average resolution time is "
                    f"{result:.2f} hours."
                ),
                "result": result,
                "source": "LLM + Python"
            }

        if intent == "anomalies":
            summary = get_anomaly_summary(tickets)

            return {
                "question": question,
                "answer": (
                    f"I found {summary['total_anomalies']} anomalies: "
                    f"{summary['total_long_resolution_anomalies']} "
                    f"long-resolution anomalies and "
                    f"{summary['total_old_high_priority_anomalies']} "
                    f"old high-priority tickets."
                ),
                "result": summary,
                "source": "LLM + Python"
            }

    # Fallback to deterministic processing if LLM is unavailable
    question_lower = question.lower()

    if "how many" in question_lower and "open" in question_lower:
        result = count_tickets(tickets, status="Open")

        return {
            "question": question,
            "answer": f"There are {result} open tickets.",
            "result": result,
            "source": "Python fallback"
        }

    if "critical" in question_lower and (
        "unresolved" in question_lower or "open" in question_lower
    ):
        result = len(
            tickets[
                (tickets["priority"] == "Critical")
                & (tickets["status"] != "Resolved")
            ]
        )

        return {
            "question": question,
            "answer": (
                f"There are {result} unresolved Critical tickets."
            ),
            "result": result,
            "source": "Python fallback"
        }

    if "average" in question_lower and "rating" in question_lower:
        category = None

        if "technical" in question_lower:
            category = "Technical"

        result = average_customer_rating(
            tickets,
            category=category
        )

        return {
            "question": question,
            "answer": (
                f"The average customer rating is {result:.2f}."
            ),
            "result": result,
            "source": "Python fallback"
        }

    if "most" in question_lower and "resolved" in question_lower:
        result = agent_with_most_resolved_tickets(tickets)

        return {
            "question": question,
            "answer": (
                f"Agent {result['agent_id']} resolved "
                f"{result['resolved_ticket_count']} tickets."
            ),
            "result": result,
            "source": "Python fallback"
        }

    if "lowest" in question_lower and "rating" in question_lower:
        result = agent_with_lowest_average_rating(tickets)

        return {
            "question": question,
            "answer": (
                f"Agent {result['agent_id']} has the lowest "
                f"average rating of {result['average_rating']:.2f}."
            ),
            "result": result,
            "source": "Python fallback"
        }

    if "average" in question_lower and "resolution" in question_lower:
        result = average_resolution_time(tickets)

        return {
            "question": question,
            "answer": (
                f"The average resolution time is {result:.2f} hours."
            ),
            "result": result,
            "source": "Python fallback"
        }

    if "anomal" in question_lower:
        summary = get_anomaly_summary(tickets)

        return {
            "question": question,
            "answer": (
                f"I found {summary['total_anomalies']} anomalies."
            ),
            "result": summary,
            "source": "Python fallback"
        }

    return {
        "question": question,
        "answer": (
            "I could not determine the requested analysis."
        ),
        "result": None,
        "source": "Python fallback"
    }