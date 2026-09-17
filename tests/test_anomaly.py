from app.services.data_service import load_tickets
from app.services.anomaly_service import get_anomaly_summary


def test_anomaly_detection():
    df = load_tickets()
    result = get_anomaly_summary(df)

    assert result["long_resolution_count"] == 21
    assert result["old_unresolved_priority_count"] == 80
    assert result["total_anomaly_count"] == 101