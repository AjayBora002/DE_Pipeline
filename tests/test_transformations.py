from datetime import datetime

def calculate_duration(start_str, end_str):
    fmt = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(start_str, fmt)
    end = datetime.strptime(end_str, fmt)
    duration = (end - start).total_seconds() / 60
    if duration <= 0 or duration > 1440:
        return None
    return duration

def test_normal_duration():
    assert calculate_duration("2026-01-01 10:00:00", "2026-01-01 10:30:00") == 30.0

def test_rejects_negative_duration():
    assert calculate_duration("2026-01-01 10:30:00", "2026-01-01 10:00:00") is None

def test_rejects_excessive_duration():
    assert calculate_duration("2026-01-01 00:00:00", "2026-01-03 00:00:00") is None

def test_zero_duration_rejected():
    assert calculate_duration("2026-01-01 10:00:00", "2026-01-01 10:00:00") is None