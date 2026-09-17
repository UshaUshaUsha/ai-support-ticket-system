from app.services.data_service import load_tickets
from app.services.anomaly_service import get_anomaly_summary


def test_anomaly_detection():
    df = load_tickets()
    result = get_anomaly_summary(df)

    assert result["total_long_resolution_anomalies"] == 21
    assert result["total_old_high_priority_anomalies"] == 80
    assert result["total_anomalies"] == 101