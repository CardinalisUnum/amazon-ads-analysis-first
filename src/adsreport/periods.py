"""Mature German report weeks after full attribution and latency intervals."""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo


def latest_mature_week(now: datetime, attribution_days: int, latency_days: int) -> date:
    if now.utcoffset() is None:
        raise ValueError("Maturity check requires an aware timestamp.")
    if attribution_days < 0 or latency_days < 0:
        raise ValueError("Maturity intervals cannot be negative.")
    zone = ZoneInfo("Europe/Berlin")
    local = now.astimezone(zone)
    monday = local.date() - timedelta(days=local.weekday() + 7)
    while True:
        end = datetime.combine(
            monday + timedelta(days=7), time.min, tzinfo=zone
        ).astimezone(UTC)
        if now.astimezone(UTC) >= end + timedelta(days=attribution_days + latency_days):
            return monday
        monday -= timedelta(days=7)
