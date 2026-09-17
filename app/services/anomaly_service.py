import pandas as pd

from app.services.data_service import load_tickets


def detect_long_resolution_anomalies(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Detect unusually long resolution times using the IQR method.
    """

    resolved_times = df["resolution_time_hrs"].dropna()

    if resolved_times.empty:
        return pd.DataFrame()

    q1 = resolved_times.quantile(0.25)
    q3 = resolved_times.quantile(0.75)

    iqr = q3 - q1

    upper_limit = q3 + (1.5 * iqr)

    anomalies = df[
        df["resolution_time_hrs"] > upper_limit
    ].copy()

    anomalies["anomaly_type"] = "Long resolution time"
    anomalies["severity"] = "Medium"
    anomalies["threshold_hrs"] = round(float(upper_limit), 2)

    return anomalies


def detect_old_high_priority_tickets(
    df: pd.DataFrame,
    age_hours: float = 24,
) -> pd.DataFrame:
    """
    Detect unresolved High/Critical tickets older than 24 hours.

    Because this dataset is historical, ticket age is calculated
    relative to the latest timestamp available in the dataset.
    """

    latest_date = df["created_at"].max()

    result = df[
        (df["priority"].isin(["High", "Critical"]))
        & (df["status"] != "Resolved")
    ].copy()

    if result.empty:
        return result

    result["ticket_age_hrs"] = (
        latest_date - result["created_at"]
    ).dt.total_seconds() / 3600

    anomalies = result[
        result["ticket_age_hrs"] > age_hours
    ].copy()

    anomalies["anomaly_type"] = (
        "Unresolved high-priority ticket older than 24 hours"
    )

    # Critical tickets are treated as higher severity
    anomalies["severity"] = anomalies["priority"].map(
        {
            "Critical": "Critical",
            "High": "High",
        }
    )

    return anomalies


def detect_all_anomalies(
    df: pd.DataFrame,
) -> dict:
    """
    Run all anomaly detection rules.
    """

    long_resolution = detect_long_resolution_anomalies(df)

    old_high_priority = detect_old_high_priority_tickets(df)

    return {
        "long_resolution_anomalies": long_resolution,
        "old_high_priority_anomalies": old_high_priority,
    }


def get_anomaly_summary(
    df: pd.DataFrame,
) -> dict:
    """
    Return a simple summary of detected anomalies.
    """

    results = detect_all_anomalies(df)

    long_resolution = results[
        "long_resolution_anomalies"
    ]

    old_high_priority = results[
        "old_high_priority_anomalies"
    ]

    return {
        "total_long_resolution_anomalies": len(
            long_resolution
        ),
        "total_old_high_priority_anomalies": len(
            old_high_priority
        ),
        "total_anomalies": (
            len(long_resolution)
            + len(old_high_priority)
        ),
    }


if __name__ == "__main__":

    tickets = load_tickets()

    print("\n--- Anomaly Detection Test ---")

    summary = get_anomaly_summary(tickets)

    print("\nAnomaly Summary:")

    for key, value in summary.items():
        print(f"{key}: {value}")

    results = detect_all_anomalies(tickets)

    long_resolution = results[
        "long_resolution_anomalies"
    ]

    old_high_priority = results[
        "old_high_priority_anomalies"
    ]

    if not long_resolution.empty:

        print("\nLong Resolution Anomalies:")

        print(
            long_resolution[
                [
                    "ticket_id",
                    "priority",
                    "status",
                    "resolution_time_hrs",
                    "threshold_hrs",
                    "severity",
                ]
            ].head(10)
        )

    if not old_high_priority.empty:

        print(
            "\nOld High-Priority Unresolved Tickets:"
        )

        print(
            old_high_priority[
                [
                    "ticket_id",
                    "priority",
                    "status",
                    "ticket_age_hrs",
                    "severity",
                ]
            ].head(10)
        )