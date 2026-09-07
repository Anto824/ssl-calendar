"""FastAPI app that lets users pick event series and download a personalized ICS file."""

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from ics import build_ics
from series import SERIES

app = FastAPI(title="SSL Simracing Subscriptions")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def index(request: Request):
    """Render the series selection page with one checkbox per series."""
    return templates.TemplateResponse(
        request, "index.html", {"series": SERIES}
    )


@app.post("/subscribe")
def subscribe(request: Request, series: list[str] = Form(default=[])):
    """Generate and download an ICS file for the checked series.

    The browser submits the form as application/x-www-form-urlencoded;
    each checked box contributes one "series=<id>" value.
    """
    ics = build_ics(series)
    filename = "ssl-calendar.ics"
    return Response(
        content=ics,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)