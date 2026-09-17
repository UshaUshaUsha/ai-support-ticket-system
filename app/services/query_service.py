import pandas as pd
from app.services.llm_service import classify_query
from app.services.data_service import load_tickets


def get_open_ticket_count(df: pd.DataFrame) -> int:
    """Return the number of currently open tickets."""
    return int((df["status"].str.lower() == "open").sum())


def get_resolved_ticket_count(df: pd.DataFrame) -> int:
    """Return the number of resolved tickets."""
    return int((df["status"].str.lower() == "resolved").sum())


def get_average_customer_rating(
    df: pd.DataFrame,
    category: str | None = None
) -> float | None:
    """Return the average customer rating, optionally filtered by category."""

    filtered_df = df.copy()

    if category:
        filtered_df = filtered_df[
            filtered_df["category"].str.lower() == category.lower()
        ]

    ratings = filtered_df["customer_rating"].dropna()

    if ratings.empty:
        return None

    return round(float(ratings.mean()), 2)


def get_ticket_count_by_priority(
    df: pd.DataFrame,
    priority: str
) -> int:
    """Return the number of tickets for a given priority."""

    return int(
        (
            df["priority"].str.lower()
            == priority.lower()
        ).sum()
    )


def get_resolved_tickets_by_agent(
    df: pd.DataFrame
) -> pd.Series:
    """Return the number of resolved tickets for each agent."""

    resolved_df = df[
        df["status"].str.lower() == "resolved"
    ]

    return resolved_df.groupby("agent_id").size().sort_values(
        ascending=False
    )


def get_agent_with_most_resolved_tickets(
    df: pd.DataFrame
) -> dict | None:
    """Return the agent who resolved the most tickets."""

    agent_counts = get_resolved_tickets_by_agent(df)

    if agent_counts.empty:
        return None

    agent_id = agent_counts.index[0]
    count = int(agent_counts.iloc[0])

    return {
        "agent_id": agent_id,
        "resolved_ticket_count": count,
    }


def answer_query(query: str) -> dict:
    """
    Handle basic supported natural-language queries.

    The LLM will later be responsible for understanding more
    complex natural-language questions and routing them here.
    """

    df = load_tickets()

    query_lower = query.lower().strip()

    # Open tickets
    if "how many" in query_lower and "open" in query_lower:
        count = get_open_ticket_count(df)

        return {
            "question": query,
            "answer": f"There are {count} currently open tickets.",
            "value": count,
        }

    # Resolved tickets
    if "how many" in query_lower and "resolved" in query_lower:
        count = get_resolved_ticket_count(df)

        return {
            "question": query,
            "answer": f"There are {count} resolved tickets.",
            "value": count,
        }

    # Critical tickets
    if "how many" in query_lower and "critical" in query_lower:
        count = get_ticket_count_by_priority(
            df,
            "Critical"
        )

        return {
            "question": query,
            "answer": f"There are {count} critical tickets.",
            "value": count,
        }

    # Average rating for Technical tickets
    if (
        "average" in query_lower
        and "rating" in query_lower
        and "technical" in query_lower
    ):
        rating = get_average_customer_rating(
            df,
            "Technical"
        )

        if rating is None:
            answer = "There is no customer rating data for Technical tickets."
        else:
            answer = (
                f"The average customer rating for Technical "
                f"tickets is {rating}."
            )

        return {
            "question": query,
            "answer": answer,
            "value": rating,
        }

    # Agent with most resolved tickets
    if (
        "agent" in query_lower
        and "resolved" in query_lower
        and (
            "most" in query_lower
            or "highest" in query_lower
        )
    ):
        result = get_agent_with_most_resolved_tickets(df)

        if result is None:
            answer = "No resolved tickets were found."
        else:
            answer = (
                f"{result['agent_id']} has resolved "
                f"{result['resolved_ticket_count']} tickets."
            )

        return {
            "question": query,
            "answer": answer,
            "value": result,
        }

    return {
        "question": query,
        "answer": (
            "I don't currently support this query. "
            "The LLM query layer will handle additional "
            "natural-language questions."
        ),
        "value": None,
    }
def answer_query_with_llm(query: str) -> dict:
    """
    Use the LLM to understand the user's question,
    then use Python/Pandas to calculate the actual answer.
    """
    classification = classify_query(query)
    # If the local LLM is unavailable, use deterministic Python fallback
    if classification.get("source") == "fallback":
        result = answer_query(query)
        return {
            "question": query,
            "intent": "rule_based_fallback",
            "answer": result["answer"],
            "result": result.get("value"),
            "source": "Python fallback",
        }

    intent = classification.get("intent")
    df = load_tickets()
    if intent == "open_ticket_count":
        count = get_open_ticket_count(df)
        return {
            "question": query,
            "intent": intent,
            "answer": f"There are {count} currently open tickets.",
            "value": count,
        }
    if intent == "resolved_ticket_count":
        count = get_resolved_ticket_count(df)
        return {
            "question": query,
            "intent": intent,
            "answer": f"There are {count} resolved tickets.",
            "value": count,
        }
    if intent == "critical_ticket_count":
        count = get_ticket_count_by_priority(df, "Critical")
        return {
            "question": query,
            "intent": intent,
            "answer": f"There are {count} critical tickets.",
            "value": count,
        }
    if intent == "average_technical_rating":
        rating = get_average_customer_rating(df, "Technical")
        if rating is None:
            answer = "There is no customer rating data for Technical tickets."
        else:
             answer = (
                f"The average customer rating for Technical "
                f"tickets is {rating}."
            )
        return {
            "question": query,
            "intent": intent,
            "answer": answer,
            "value": rating,
        }
    if intent == "agent_most_resolved":
        result = get_agent_with_most_resolved_tickets(df)
        if result is None:
            answer = "No resolved tickets were found."
        else:
            answer = (
                f"{result['agent_id']} has resolved "
                f"{result['resolved_ticket_count']} tickets."
            )
        return {
            "question": query,
            "intent": intent,
            "answer": answer,
            "value": result,
        }
    if intent == "anomaly_detection":
        from app.services.anomaly_service import get_anomaly_summary
        summary = get_anomaly_summary(df)

        return {
            "question": query,
            "intent": intent,
            "answer": (
                f"I found {summary['total_anomaly_count']} anomalies: "
                f"{summary['long_resolution_count']} unusually long "
                f"resolution times and "
                f"{summary['old_unresolved_priority_count']} "
                f"old unresolved High/Critical tickets."
            ),
            "value": summary,
        }
    return {
        "question": query,
        "intent": "unsupported",
        "answer": (
            "I couldn't determine a supported query type. "
            "Please ask about ticket counts, ratings, agents, "
            "or anomalies."
        ),
        "value": None,
    }

if __name__ == "__main__":
    test_queries = [
        "How many tickets are currently open?",
        "How many tickets are resolved?",
        "What is the average customer rating for Technical category tickets?",
        "Which agent resolved the most tickets?",
        "Are there any anomalies in the support tickets?",
    ]

    for question in test_queries:
        print("\nQuestion:", question)

        result = answer_query_with_llm(question)

        print("Intent:", result["intent"])
        print("Answer:", result["answer"])

