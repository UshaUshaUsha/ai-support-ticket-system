import pandas as pd
from pathlib import Path


# Find the project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Path to the support tickets CSV file
DATA_PATH = BASE_DIR / "data" / "support_tickets.csv"


REQUIRED_COLUMNS = [
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
]


def load_tickets():
    """
    Load and validate support ticket data from the CSV file.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Support ticket dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Validate columns
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Convert date column
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "response_time_hrs",
        "resolution_time_hrs",
        "customer_rating",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


if __name__ == "__main__":
    tickets = load_tickets()

    print("Dataset loaded successfully!")
    print("Number of tickets:", len(tickets))

    print("\nColumns:")
    print(tickets.columns.tolist())

    print("\nData types:")
    print(tickets.dtypes)

    print("\nMissing values:")
    print(tickets.isna().sum())

    print("\nFirst 5 tickets:")
    print(tickets.head())