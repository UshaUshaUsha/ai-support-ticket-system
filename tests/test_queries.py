from app.services.data_service import load_tickets
from app.services.query_service import (
    get_open_ticket_count,
    get_resolved_ticket_count,
    get_ticket_count_by_priority,
    get_average_customer_rating,
    get_agent_with_most_resolved_tickets,
)


def test_open_ticket_count():
    df = load_tickets()
    assert get_open_ticket_count(df) == 111


def test_resolved_ticket_count():
    df = load_tickets()
    assert get_resolved_ticket_count(df) == 327


def test_critical_ticket_count():
    df = load_tickets()
    assert get_ticket_count_by_priority(df, "Critical") == 55


def test_technical_average_rating():
    df = load_tickets()
    assert get_average_customer_rating(df, "Technical") == 3.74


def test_agent_with_most_resolved_tickets():
    df = load_tickets()
    result = get_agent_with_most_resolved_tickets(df)

    assert result["agent_id"] == "AGT-09"
    assert result["resolved_ticket_count"] == 37