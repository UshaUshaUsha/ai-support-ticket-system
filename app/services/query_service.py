import pandas as pd
from app.services.data_service import load_tickets
def count_tickets(
    df: pd.DataFrame,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
) -> int:
    """
    Count tickets using optional filters.
    """

    result = df.copy()

    if status:
        result = result[result["status"].str.lower() == status.lower()]

    if priority:
        result = result[result["priority"].str.lower() == priority.lower()]

    if category:
        result = result[result["category"].str.lower() == category.lower()]

    return len(result)


def average_customer_rating(
    df: pd.DataFrame,
    category: str | None = None,
) -> float | None:
    """
    Calculate average customer rating.
    """

    result = df.copy()

    if category:
        result = result[
            result["category"].str.lower() == category.lower()
        ]

    ratings = result["customer_rating"].dropna()

    if ratings.empty:
        return None

    return round(float(ratings.mean()), 2)


def agent_with_most_resolved_tickets(
    df: pd.DataFrame,
) -> dict | None:
    """
    Find the agent who resolved the most tickets.
    """

    resolved = df[
        df["status"].str.lower() == "resolved"
    ]

    if resolved.empty:
        return None

    counts = (
        resolved
        .groupby("agent_id")
        .size()
        .sort_values(ascending=False)
    )

    agent_id = counts.index[0]
    ticket_count = int(counts.iloc[0])

    return {
        "agent_id": agent_id,
        "resolved_ticket_count": ticket_count,
    }


def agent_with_lowest_average_rating(
    df: pd.DataFrame,
) -> dict | None:
    """
    Find the agent with the lowest average customer rating.
    """

    ratings = df.dropna(subset=["customer_rating"])

    if ratings.empty:
        return None

    agent_ratings = (
        ratings
        .groupby("agent_id")["customer_rating"]
        .mean()
        .sort_values()
    )

    agent_id = agent_ratings.index[0]
    average_rating = round(float(agent_ratings.iloc[0]), 2)

    return {
        "agent_id": agent_id,
        "average_rating": average_rating,
    }


def critical_unresolved_tickets(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return all Critical tickets that are not resolved.
    """

    result = df[
        (df["priority"].str.lower() == "critical")
        & (df["status"].str.lower() != "resolved")
    ]

    return result.copy()


def average_resolution_time(
    df: pd.DataFrame,
    category: str | None = None,
) -> float | None:
    """
    Calculate the average resolution time for resolved tickets.
    """

    result = df[
        df["resolution_time_hrs"].notna()
    ].copy()

    if category:
        result = result[
            result["category"].str.lower() == category.lower()
        ]

    if result.empty:
        return None

    return round(
        float(result["resolution_time_hrs"].mean()),
        2,
    )


if __name__ == "__main__":

    # Load the dataset
    tickets = load_tickets()

    print("\n--- Query Service Test ---")

    # 1. Count open tickets
    open_count = count_tickets(
        tickets,
        status="Open",
    )

    print("\nOpen tickets:", open_count)

    # 2. Count critical unresolved tickets
    critical_count = count_tickets(
        tickets,
        priority="Critical",
        status="Open",
    )

    print(
        "Critical + Open tickets:",
        critical_count,
    )

    # 3. Average Technical customer rating
    technical_rating = average_customer_rating(
        tickets,
        category="Technical",
    )

    print(
        "Average Technical rating:",
        technical_rating,
    )

    # 4. Agent with most resolved tickets
    top_agent = agent_with_most_resolved_tickets(
        tickets
    )

    print(
        "Agent with most resolved tickets:",
        top_agent,
    )

    # 5. Agent with lowest rating
    lowest_agent = agent_with_lowest_average_rating(
        tickets
    )

    print(
        "Agent with lowest average rating:",
        lowest_agent,
    )

    # 6. Average resolution time
    avg_resolution = average_resolution_time(
        tickets
    )

    print(
        "Average resolution time:",
        avg_resolution,
        "hours",
    )