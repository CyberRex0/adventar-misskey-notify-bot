import copy
import io
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

from libs.adventar_calendar import (
    CalendarDataError, MAX_HTML_BYTES, REQUEST_TIMEOUT,
    _AdventarRedirectHandler, fetch_calendar, parse_calendar,
)


def page(data, suffix=";"):
    return ('<!doctype html><script>const unrelated = {};</script>'
            '<SCRIPT data-test="yes">\n window.__ADVENTAR_DATA__ = '
            + json.dumps(data, ensure_ascii=True) + suffix + '</SCRIPT>').encode()


class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "calendar": {"title": "テスト & カレンダー", "year": 2026},
            "entries": [{"day": 3, "owner": {"name": "参加者"},
                         "comment": "予定の題名\n補足", "title": "記事 | サイト",
                         "url": "https://example.org/?a=1&b=2"}],
        }

    def test_existing_data_structure_and_meanings(self):
        calendar, title = parse_calendar(page(self.data))
        self.assertEqual(title, "テスト & カレンダー Advent Calendar 2026")
        self.assertEqual(list(calendar), [3])
        self.assertEqual(calendar[3], {
            "user": "参加者", "title": "予定の題名\n補足", "articleTitle": "記事 | サイト",
            "url": "https://example.org/?a=1&b=2",
        })
        self.assertNotIn(1, calendar)

    def test_empty_optional_values(self):
        for value in ("", None):
            for key in ("comment", "title", "url"):
                self.data["entries"][0][key] = value
            calendar, _ = parse_calendar(page(self.data, suffix=""))
            self.assertEqual(calendar[3], {
                "user": "参加者", "title": None, "articleTitle": None, "url": None,
            })

    def test_empty_calendar(self):
        self.data["entries"] = []
        calendar, _ = parse_calendar(page(self.data))
        self.assertEqual(calendar, {})

    def test_registered_user_named_register_is_preserved(self):
        self.data["entries"][0]["owner"]["name"] = "登録"
        calendar, _ = parse_calendar(page(self.data))
        self.assertEqual(list(calendar), [3])
        self.assertEqual(calendar[3]["user"], "登録")

    def test_comment_and_article_title_do_not_fall_back_to_each_other(self):
        for comment, article_title in (("", "記事 | サイト"), ("参加コメント", "")):
            self.data["entries"][0].update(comment=comment, title=article_title)
            calendar, _ = parse_calendar(page(self.data))
            self.assertEqual(calendar[3]["title"], comment or None)
            self.assertEqual(calendar[3]["articleTitle"], article_title or None)

    def test_json_text_is_not_html_unescaped_or_executed(self):
        text = '&amp; <b>literal</b> "); dangerous(); //'
        self.data["entries"][0]["comment"] = text
        calendar, _ = parse_calendar(page(self.data))
        self.assertEqual(calendar[3]["title"], text)

    def test_non_json_scripts_are_rejected(self):
        for html in (
            b'<p>window.__ADVENTAR_DATA__={}</p>',
            b'<script>// window.__ADVENTAR_DATA__={}</script>',
            b'<script src="external.js">window.__ADVENTAR_DATA__={}</script>',
            b'<script>window.__ADVENTAR_DATA__=dangerous()</script>',
            page(self.data, suffix='; dangerous();'),
        ):
            with self.subTest(html=html[:80]), self.assertRaises(CalendarDataError):
                parse_calendar(html)

    def test_invalid_schema(self):
        cases = [None, {}, {"calendar": {}, "entries": []}]
        for key, value in (("day", 0), ("day", 26), ("day", True),
                           ("day", "3"), ("owner", None), ("title", [])):
            data = copy.deepcopy(self.data)
            data["entries"][0][key] = value
            cases.append(data)
        duplicate = copy.deepcopy(self.data)
        duplicate["entries"] *= 2
        cases.append(duplicate)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(CalendarDataError):
                parse_calendar(page(data))

    def test_size_limit(self):
        with self.assertRaises(CalendarDataError):
            parse_calendar(b" " * (MAX_HTML_BYTES + 1))

    @patch("adventar_calendar.build_opener")
    def test_fetch_is_bounded_and_uses_fixed_https_origin(self, build):
        response = Mock(wraps=io.BytesIO(page(self.data)))
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        build.return_value.open.return_value = response
        calendar, _ = fetch_calendar(13130)
        self.assertEqual(calendar[3]["user"], "参加者")
        response.read.assert_called_once_with(MAX_HTML_BYTES + 1)
        args, kwargs = build.return_value.open.call_args
        self.assertEqual(args[0].full_url, "https://adventar.org/calendars/13130")
        self.assertEqual(kwargs["timeout"], REQUEST_TIMEOUT)
        self.assertTrue(response.__exit__.called)

    @patch("adventar_calendar.build_opener")
    def test_network_errors_propagate(self, build):
        for error in (URLError("unavailable"), TimeoutError(),
                      HTTPError("https://adventar.org", 404, "Not Found", {}, None)):
            build.return_value.open.side_effect = error
            with self.assertRaises(type(error)):
                fetch_calendar(13130)

    @patch("adventar_calendar.build_opener")
    def test_invalid_ids_do_not_make_requests(self, build):
        for value in (None, True, 0, -1, "13130", "https://example.org"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fetch_calendar(value)
        build.assert_not_called()

    def test_redirects_stay_on_adventar_https(self):
        handler = _AdventarRedirectHandler()
        request = Request("https://adventar.org/calendars/13130")
        allowed = handler.redirect_request(
            request, None, 302, "Found", {}, "https://adventar.org/calendars/1")
        self.assertEqual(allowed.full_url, "https://adventar.org/calendars/1")
        for target in ("http://adventar.org/", "https://example.org/",
                       "https://adventar.org@example.org/", "http://127.0.0.1/"):
            with self.subTest(target=target), self.assertRaises(CalendarDataError):
                handler.redirect_request(request, None, 302, "Found", {}, target)


if __name__ == "__main__":
    unittest.main()
