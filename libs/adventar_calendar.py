"""Fetch Adventar's embedded JSON without running page scripts or a browser."""

import json
import re
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from selectolax.lexbor import LexborHTMLParser


MAX_HTML_BYTES = 2 * 1024 * 1024
REQUEST_TIMEOUT = 20
_ASSIGNMENT = re.compile(r"\s*window\.__ADVENTAR_DATA__\s*=\s*")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"

class CalendarDataError(ValueError):
    """The response does not contain usable Adventar calendar data."""


class _AdventarRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        if (target.scheme != "https" or target.netloc != "adventar.org"):
            raise CalendarDataError("Refusing redirect outside https://adventar.org")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _text(value, field):
    if not isinstance(value, str):
        raise CalendarDataError("Invalid text field: " + field)
    return value


def _optional_text(value, field):
    return "" if value is None else _text(value, field)


def parse_calendar(html):
    """Return the existing (day dictionary, displayed calendar title) format.

    Only inline script text is inspected. JSON decoding never evaluates JavaScript,
    fetches linked resources, or interprets HTML entities inside the script.
    """
    if len(html) > MAX_HTML_BYTES:
        raise CalendarDataError("Calendar HTML exceeds the size limit")
    document = LexborHTMLParser(html)
    data = None
    for script in document.css("script:not([src])"):
        source = script.text()
        assignment = _ASSIGNMENT.match(source)
        if assignment is None:
            continue
        payload = source[assignment.end():].strip()
        if payload.endswith(";"):
            payload = payload[:-1]
        try:
            data = json.loads(payload)
        except (ValueError, RecursionError) as exc:
            raise CalendarDataError("Invalid __ADVENTAR_DATA__ JSON") from exc
        break
    if not isinstance(data, dict):
        raise CalendarDataError("Missing __ADVENTAR_DATA__ object")

    metadata = data.get("calendar")
    entries = data.get("entries")
    if not isinstance(metadata, dict) or not isinstance(entries, list):
        raise CalendarDataError("Missing calendar or entries")
    name = _text(metadata.get("title"), "calendar.title")
    year = metadata.get("year")
    if type(year) is not int:
        raise CalendarDataError("Invalid calendar year")
    calendar_title = "{} Advent Calendar {}".format(name, year)

    calendar = {}
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise CalendarDataError("Invalid entry")
        day = entry.get("day")
        if type(day) is not int or not 1 <= day <= 25 or day in seen:
            raise CalendarDataError("Invalid or duplicate entry day")
        seen.add(day)
        owner = entry.get("owner")
        if not isinstance(owner, dict):
            raise CalendarDataError("Missing entry owner")
        user = _text(owner.get("name"), "owner.name")
        comment = _optional_text(entry.get("comment"), "comment")
        article_title = _optional_text(entry.get("title"), "title")
        url = _optional_text(entry.get("url"), "url")
        calendar[day] = {
            "user": user,
            # Keep the participant's comment separate from the linked page title.
            "title": comment or None,
            "articleTitle": article_title or None,
            "url": url or None,
        }
    return calendar, calendar_title


def fetch_calendar(calendar_id):
    """Fetch one bounded HTTPS response from Adventar with certificate checks."""
    if type(calendar_id) is not int or calendar_id <= 0:
        raise ValueError("Calendar ID must be a positive integer")
    request = Request(
        "https://adventar.org/calendars/{}".format(calendar_id),
        headers={"Accept": "text/html", "User-Agent": USER_AGENT},
    )
    with build_opener(_AdventarRedirectHandler()).open(
        request, timeout=REQUEST_TIMEOUT
    ) as response:
        html = response.read(MAX_HTML_BYTES + 1)
    return parse_calendar(html)
