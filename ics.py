"""ICS (RFC 5545) generation for selected event series.

Usage:
    from ics import build_ics
    text = build_ics(["ssl-season-6", "ssl-mx5-cup-2026"])

Each selected series becomes one or more VEVENTs:
    - recurring series (rrule)  -> single VEVENT with DTSTART / DURATION / RRULE
    - one-off series (dates)    -> one VEVENT per date

The generated calendar is emitted with CRLF line endings and proper
text escaping so it is accepted by major calendar clients (Google,
Outlook, Apple, Thunderbird).
"""

from datetime import datetime, timezone

from series import SERIES, get_series

# Domain suffix used to build unique, stable event IDs.
UID_DOMAIN = "ssl-simracing.example"

_CRLF = "\r\n"


def _escape(text: str) -> str:
    """Escape a text property value per RFC 5545 section 3.3.11."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    """Fold long content lines to 75 octets per RFC 5545 section 3.1.

    First line carries 75 octets; continuation lines start with a space
    (which counts toward the limit) and carry 74 payload octets.
    Multi-byte UTF-8 characters are never split across a fold.
    """
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line

    parts: list[bytes] = []
    start = 0
    while start < len(encoded):
        room = 75 if not parts else 74
        end = min(start + room, len(encoded))
        # Back off so we don't cut a multi-byte character in half.
        while end < len(encoded) and (encoded[end] & 0xC0) == 0x80:
            end -= 1
        payload = encoded[start:end]
        if parts:
            payload = b" " + payload
        parts.append(payload)
        start = end
    return _CRLF.join(p.decode("utf-8") for p in parts)


def _format_dt(dt: datetime) -> str:
    """Format a naive local datetime as an RFC 5545 DATE-TIME (floating)."""
    return dt.strftime("%Y%m%dT%H%M%S")


def _vevent(uid: str, summary: str, dtstart: datetime, duration: int,
            description: str, location: str | None,
            rrule: str | None = None, count: int | None = None) -> str:
    """Build one VEVENT block (without line folding applied yet)."""
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        "DTSTAMP:" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        f"DTSTART:{_format_dt(dtstart)}",
        f"DURATION:PT{duration}M",
        f"SUMMARY:{_escape(summary)}",
    ]
    if rrule:
        rule = rrule if not count else f"{rrule};COUNT={count}"
        lines.append(f"RRULE:{rule}")
    if description:
        lines.append(f"DESCRIPTION:{_escape(description)}")
    if location:
        lines.append(f"LOCATION:{_escape(location)}")
    lines.append("END:VEVENT")
    return _CRLF.join(lines)


def _series_events(series: dict) -> list[str]:
    """Build the VEVENT blocks for a single series."""
    duration = int(series.get("duration", 60))
    summary = series["name"]
    description = series.get("description", "")
    location = series.get("location")
    events: list[str] = []

    if "dates" in series:
        for raw in series["dates"]:
            dt = datetime.fromisoformat(raw)
            uid = f"{series['id']}-{dt.strftime('%Y%m%dT%H%M%S')}@{UID_DOMAIN}"
            events.append(_vevent(uid, summary, dt, duration, description, location))
    else:
        dt = datetime.fromisoformat(series["start"])
        uid = f"{series['id']}@{UID_DOMAIN}"
        events.append(_vevent(uid, summary, dt, duration, description, location,
                              rrule=series.get("rrule"),
                              count=series.get("count")))
    return events


def build_ics(selected_ids: list[str]) -> str:
    """Build a complete ICS calendar for the given series ids.

    Unknown ids are ignored. An empty (but valid) calendar header is
    returned when no series is selected.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SSL Simracing//Subscription Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for sid in selected_ids:
        series = get_series(sid)
        if series is None:
            continue
        lines.extend(_series_events(series))

    lines.append("END:VCALENDAR")
    raw = _CRLF.join(lines)
    return _CRLF.join(_fold(line) for line in raw.split(_CRLF))