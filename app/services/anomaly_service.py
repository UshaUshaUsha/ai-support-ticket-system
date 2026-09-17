
import pandas as pd

from app.services.data_service import load_tickets


def detect_long_resolution_times(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Detect tickets with unusually long resolution times.

    Uses the IQR method:
    Upper threshold = Q3 + 1.5 * IQR
    """

    resolved_df = df[
        df["resolution_time_hrs"].notna()
    ].copy()

    if resolved_df.empty:
        return resolved_df

    q1 = resolved_df["resolution_time_hrs"].quantile(0.25)
    q3 = resolved_df["resolution_time_hrs"].quantile(0.75)

    iqr = q3 - q1
    upper_threshold = q3 + (1.5 * iqr)

    anomalies = resolved_df[
        resolved_df["resolution_time_hrs"] > upper_threshold
    ].copy()

    anomalies["anomaly_type"] = "Unusually long resolution time"
    anomalies["anomaly_threshold_hrs"] = upper_threshold

    return anomalies


def detect_old_unresolved_priority_tickets(
    df: pd.DataFrame,
    hours: int = 24
) -> pd.DataFrame:
    """
    Detect unresolved High/Critical tickets that are older
    than the specified number of hours.

    The assessment specifically gives 24 hours as an example.
    """

    current_time = df["created_at"].max()

    unresolved = df[
        df["status"].str.lower().isin(["open", "escalated"])
    ].copy()

    unresolved["ticket_age_hours"] = (
        current_time - unresolved["created_at"]
    ).dt.total_seconds() / 3600

    anomalies = unresolved[
        unresolved["priority"].str.lower().isin(
            ["high", "critical"]
        )
        & (unresolved["ticket_age_hours"] > hours)
    ].copy()

    anomalies["anomaly_type"] = (
        f"Unresolved High/Critical ticket older than {hours} hours"
    )

    return anomalies


def detect_anomalies(
    df: pd.DataFrame
) -> dict:
    """
    Run all anomaly detection checks.
    """

    long_resolution = detect_long_resolution_times(df)

    old_unresolved = detect_old_unresolved_priority_tickets(df)

    return {
        "long_resolution_time": long_resolution,
        "old_unresolved_priority": old_unresolved,
    }


def get_anomaly_summary(
    df: pd.DataFrame
) -> dict:
    """
    Return a JSON-friendly summary of detected anomalies.
    """

    anomalies = detect_anomalies(df)

    long_resolution = anomalies["long_resolution_time"]
    old_unresolved = anomalies["old_unresolved_priority"]

    return {
        "long_resolution_count": len(long_resolution),
        "old_unresolved_priority_count": len(old_unresolved),
        "total_anomaly_count": (
            len(long_resolution)
            + len(old_unresolved)
        ),
    }


if __name__ == "__main__":
    tickets = load_tickets()

    summary = get_anomaly_summary(tickets)

    print("Anomaly Detection Results")
    print("-" * 30)

    print(
        "Unusually long resolution tickets:",
        summary["long_resolution_count"]
    )

    print(
        "Unresolved High/Critical tickets older than 24 hours:",
        summary["old_unresolved_priority_count"]
    )

    print(
        "Total anomalies:",
        summary["total_anomaly_count"]
    )

    anomalies = detect_anomalies(tickets)

    if not anomalies["long_resolution_time"].empty:
        print("\nLong Resolution Examples:")
        print(
            anomalies["long_resolution_time"][
                [
                    "ticket_id",
                    "priority",
                    "resolution_time_hrs",
                    "anomaly_type",
                ]
            ].head(10).to_string(index=False)
        )

    if not anomalies["old_unresolved_priority"].empty:
        print("\nOld Unresolved High/Critical Examples:")
        print(
            anomalies["old_unresolved_priority"][
                [
                    "ticket_id",
                    "priority",
                    "status",
                    "ticket_age_hours",
                    "anomaly_type",
                ]
            ].head(10).to_string(index=False)
        )

#Your dataset is from January 2024, while your computer's current date is September 2026. Therefore, using:
#pd.Timestamp.now()

