"""Hardcoded event series definitions.

Each series is a dict with:
    id:          unique slug used in URLs / filenames
    name:        display name
    description: text shown on the site and in the ICS DESCRIPTION
    location:    optional venue string
    start:       first occurrence as an ISO datetime string (local time)
    duration:    event length in minutes
    rrule:       (recurring) RFC 5545 recurrence rule, e.g. "FREQ=WEEKLY;BYDAY=MO"
                 set "count" to limit the number of occurrences (default: unlimited)
    dates:       (one-off) list of ISO datetime strings; each becomes its own VEVENT

A series must define exactly one of "rrule" or "dates".
"""

SERIES = [
    {
        "id": "ssl-mx5-cup-2026",
        "name": "SSL MX-5 Cup 2026",
        "description": "MX-5 NR-A ND 2022 championship featuring Sprint and Reverse Grid races.",
        "location": "Multiple Venues (Daytona, Tsukuba, Nurburgring, Road Atlanta)",
        "start": "2026-08-02T18:00:00",
        "duration": 60,
        "dates": [
            "2026-08-02T18:00:00",
            "2026-08-16T18:00:00",
            "2026-08-30T18:00:00",
            "2026-09-20T18:00:00",
        ],
    },
    {
        "id": "ssl-season-6",
        "name": "Slipstream Simracing League - Season 6",
        "description": "10-week series alternating between Sprint and Endurance events.",
        "location": "Global Circuits",
        "start": "2026-08-06T18:00:00",
        "duration": 90,
        "rrule": "FREQ=WEEKLY;BYDAY=TH",
        "count": 10,
    },
    {
        "id": "ssl-wec-series",
        "name": "SSL WEC Series",
        "description": "Official WEC Season featuring 2 and 3-hour endurance races.",
        "location": "Le Mans, Spa-Francorchamps, Fuji, Nürburgring",
        "start": "2026-06-23T18:00:00",
        "duration": 180,
        "dates": [
            "2026-06-23T18:00:00",
            "2026-07-28T18:00:00",
            "2026-09-01T18:00:00",
            "2026-09-29T18:00:00",
        ],
    },
]

def get_series(series_id: str) -> dict | None:
    """Look up a series by id."""
    for s in SERIES:
        if s["id"] == series_id:
            return s
    return None