"""Regenerate static/data.js from the single source of truth (series.py).

Run this whenever you edit series.py, then commit & push:
    python make_data.py
    git add . && git commit -m "update series" && git push

GitHub Pages will pick up the new data.js automatically.
"""

import json
from pathlib import Path

from series import SERIES

BASE = Path(__file__).resolve().parent
OUT = BASE / "static" / "data.js"


def main() -> None:
    data = json.dumps(SERIES, indent=2, ensure_ascii=False)
    out = (
        "// Auto-generated from series.py by make_data.py — do not edit by hand.\n"
        "window.SERIES = " + data + ";\n"
    )
    OUT.write_text(out, encoding="utf-8")
    print(f"Wrote static/data.js ({len(SERIES)} series)")


if __name__ == "__main__":
    main()