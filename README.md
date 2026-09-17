# AI Support Ticket System

An AI-powered support ticket analytics and anomaly detection system built with Python.

## Features

- CSV-based support ticket ingestion
- Natural-language ticket queries
- REST API using FastAPI
- Interactive Streamlit UI
- Support ticket analytics using Pandas
- Long resolution-time anomaly detection
- Unresolved High/Critical ticket detection
- LLM integration layer using Ollama
- Automatic fallback to deterministic Python analytics when the LLM is unavailable

## Architecture

```text
support_tickets.csv
        |
        v
   Data Service
        |
        +--------------------+
        |                    |
        v                    v
 Query Service        Anomaly Service
        |                    |
        +---------+----------+
                  |
                  v
             FastAPI
                  |
          +-------+-------+
          |               |
          v               v
     Streamlit UI     REST API
          |
          v
       User