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

from app.services.data_service import load_tickets
from app.services.query_service import answer_query_with_llm
from app.services.anomaly_service import (
    get_anomaly_summary,
    detect_anomalies,
)


app = FastAPI(
    title="AI Support Ticket System",
    description="AI-powered support ticket analysis and anomaly detection API",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    try:
        tickets = load_tickets()

        return {
            "status": "healthy",
            "dataset_loaded": True,
            "tickets_loaded": len(tickets),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.get("/anomalies")
def get_anomalies():
    try:
        tickets = load_tickets()

        summary = get_anomaly_summary(tickets)
        anomalies = detect_anomalies(tickets)

        return {
            "summary": summary,
            "long_resolution_anomalies": (
                anomalies["long_resolution_time"]
                .to_dict(orient="records")
            ),
            "old_unresolved_priority_anomalies": (
                anomalies["old_unresolved_priority"]
                .to_dict(orient="records")
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.post("/query")
def query_tickets(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        return answer_query_with_llm(question)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )