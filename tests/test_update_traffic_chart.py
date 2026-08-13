import datetime as dt
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import update_traffic_chart as traffic  # noqa: E402


class JsonResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def http_error(status: int, message: str) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://example.goatcounter.com/api/v0/stats/total",
        status,
        message,
        {},
        io.BytesIO(json.dumps({"error": message}).encode()),
    )


class FetchStatsTests(unittest.TestCase):
    def test_retries_transient_404_then_succeeds(self):
        responses = [http_error(404, "not found"), JsonResponse(b'{"stats":[]}')]
        delays = []

        def urlopen(_request, timeout):
            self.assertEqual(timeout, 30)
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

        result = traffic.fetch_stats(
            "example",
            "token",
            dt.date(2026, 8, 13),
            urlopen=urlopen,
            sleep=delays.append,
        )

        self.assertEqual(result, {"stats": []})
        self.assertEqual(delays, [1])

    def test_does_not_retry_authentication_error(self):
        attempts = 0

        def urlopen(_request, timeout):
            nonlocal attempts
            attempts += 1
            raise http_error(401, "unauthorized")

        with self.assertRaisesRegex(SystemExit, "HTTP 401: unauthorized"):
            traffic.fetch_stats(
                "example",
                "token",
                dt.date(2026, 8, 13),
                urlopen=urlopen,
                sleep=lambda _delay: None,
            )

        self.assertEqual(attempts, 1)

    def test_stops_after_bounded_network_retries(self):
        attempts = 0

        def urlopen(_request, timeout):
            nonlocal attempts
            attempts += 1
            raise urllib.error.URLError("temporary DNS failure")

        with self.assertRaisesRegex(SystemExit, "temporary DNS failure"):
            traffic.fetch_stats(
                "example",
                "token",
                dt.date(2026, 8, 13),
                urlopen=urlopen,
                sleep=lambda _delay: None,
            )

        self.assertEqual(attempts, traffic.MAX_FETCH_ATTEMPTS)


if __name__ == "__main__":
    unittest.main()
