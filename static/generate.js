/* ICS (RFC 5545) generation in the browser — JS port of ics.py.
 * Produces byte-compatible output (except DTSTAMP, which reflects
 * generation time). No dependencies; runs as a plain <script>.
 */

const UID_DOMAIN = "ssl-simracing.example";
const CRLF = "\r\n";

function escapeText(text) {
  return String(text)
    .replace(/\\/g, "\\\\")
    .replace(/;/g, "\\;")
    .replace(/,/g, "\\,")
    .replace(/\r\n/g, "\\n")
    .replace(/\n/g, "\\n");
}

/** Fold a content line to 75 octets per RFC 5545 section 3.1.
 * First line carries 75 octets; continuation lines start with a space
 * (counting toward the limit) and carry 74 payload octets.
 * Multi-byte UTF-8 characters are never split across a fold.
 */
function foldLine(line) {
  const bytes = new TextEncoder().encode(line);
  if (bytes.length <= 75) return line;

  const decoder = new TextDecoder();
  const parts = [];
  let start = 0;
  while (start < bytes.length) {
    const room = start === 0 ? 75 : 74;
    let end = Math.min(start + room, bytes.length);
    // Back off so we don't cut a multi-byte character in half.
    while (end < bytes.length && (bytes[end] & 0xC0) === 0x80) end--;
    let chunk = bytes.slice(start, end);
    if (start > 0) {
      const withSpace = new Uint8Array(chunk.length + 1);
      withSpace[0] = 0x20; // ' '
      withSpace.set(chunk, 1);
      chunk = withSpace;
    }
    parts.push(decoder.decode(chunk));
    start = end;
  }
  return parts.join(CRLF);
}

/** "2026-08-02T18:00:00" -> "20260802T180000" (floating local time). */
function formatDt(iso) {
  return iso.replace(/[-:]/g, "").substring(0, 15);
}

/** Current UTC time as "20260907T133015Z". */
function dtStamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
}

function vEvent(uid, summary, dtstart, duration, description, location,
                rrule, count) {
  const lines = [
    "BEGIN:VEVENT",
    "UID:" + uid,
    "DTSTAMP:" + dtStamp(),
    "DTSTART:" + formatDt(dtstart),
    "DURATION:PT" + duration + "M",
    "SUMMARY:" + escapeText(summary),
  ];
  if (rrule) {
    lines.push("RRULE:" + (count ? rrule + ";COUNT=" + count : rrule));
  }
  if (description) {
    lines.push("DESCRIPTION:" + escapeText(description));
  }
  if (location) {
    lines.push("LOCATION:" + escapeText(location));
  }
  lines.push("END:VEVENT");
  return lines.join(CRLF);
}

/** Build the VEVENT blocks for one series (same rules as ics.py). */
function seriesEvents(series) {
  const duration = series.duration != null ? Number(series.duration) : 60;
  const summary = series.name;
  const description = series.description || "";
  const location = series.location || null;
  const events = [];

  if (series.dates) {
    for (const raw of series.dates) {
      const uid = series.id + "-" + formatDt(raw) + "@" + UID_DOMAIN;
      events.push(vEvent(uid, summary, raw, duration, description, location));
    }
  } else {
    const uid = series.id + "@" + UID_DOMAIN;
    events.push(vEvent(uid, summary, series.start, duration, description,
                       location, series.rrule || null, series.count || null));
  }
  return events;
}

/** Build a complete ICS calendar for the given series ids.
 *  Unknown ids are ignored; an empty selection yields a valid empty calendar.
 */
function buildICS(selectedIds, seriesList) {
  const series = (seriesList || window.SERIES || []);
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//SSL Simracing//Subscription Generator//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
  ];

  for (const sid of selectedIds || []) {
    const s = series.find((x) => x.id === sid);
    if (!s) continue;
    lines.push(...seriesEvents(s));
  }

  lines.push("END:VCALENDAR");
  return lines.join(CRLF).split(CRLF).map(foldLine).join(CRLF);
}

/* ---- page wiring (only when loaded in a browser with the form) ---- */
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("subscribe-form");
    const msg = document.getElementById("form-msg");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const ids = Array.from(form.querySelectorAll('input[name="series"]:checked'))
        .map((c) => c.value);
      if (ids.length === 0) {
        msg.textContent = "Please check at least one series.";
        msg.style.display = "block";
        return;
      }
      msg.style.display = "none";
      const ics = buildICS(ids);
      const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ssl-subscriptions.ics";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  });
}

/* Export for testing under Node (ignored by browsers). */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { buildICS, escapeText, foldLine, seriesEvents };
}