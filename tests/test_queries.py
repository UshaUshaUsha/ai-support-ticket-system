from app.services.data_service import load_tickets
from app.services.query_service import (
    count_tickets,
    average_customer_rating,
    agent_with_most_resolved_tickets,
)


def test_open_ticket_count():
    df = load_tickets()
    assert count_tickets(df, status="Open") == 111


def test_technical_average_rating():
    df = load_tickets()
    result = average_customer_rating(df, category="Technical")
    assert round(result, 2) == 3.74


def test_most_resolved_agent():
    df = load_tickets()
    result = agent_with_most_resolved_tickets(df)
    assert result["agent_id"] == "AGT-09"