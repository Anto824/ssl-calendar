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
        "id": "ssl-season-7",
        "name": "Slipstream Simracing League - Season 7",
        "description": "10-week series alternating between Sprint and Endurance events.",
        "location": "Global Circuits",
        "start": "2026-08-06T21:00:00",
        "duration": 90,
        "rrule": "FREQ=WEEKLY;BYDAY=TH",
        "count": 10,
    },
    {
    "id": "ssl-side-series-2026-2027",
    "name": "SSL Side Series",
    "description": "Side Series featuring Multiclass and Endurance races across various car classes.",
    "location": "Multiple Venues (Watkins Glen, Tokyo Expressway, Fuji Speedway, Brands Hatch, Spa-Francorchamps, Daytona Road Course)",
    "start": "2026-11-10T20:30:00",
    "duration": 60,
    "dates": [
        "2026-11-10T20:30:00",
        "2026-11-29T20:30:00",
        "2026-12-08T20:30:00",
        "2026-12-22T20:30:00",
        "2027-01-05T20:30:00",
        "2027-01-19T20:30:00"
    ]
},
]

def get_series(series_id: str) -> dict | None:
    """Look up a series by id."""
    for s in SERIES:
        if s["id"] == series_id:
            return s
    return None
