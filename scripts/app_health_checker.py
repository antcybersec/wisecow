#!/usr/bin/env python3
"""
Application Health Checker (PS2 - Objective 4)
Checks HTTP endpoints and reports UP/DOWN based on status codes and response time.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class HealthResult:
    url: str
    status: str
    http_code: int | None
    response_time_ms: float | None
    message: str
    checked_at: str


def check_url(
    url: str,
    timeout: float,
    expected_codes: set[int],
) -> HealthResult:
    checked_at = datetime.now(timezone.utc).isoformat()
    start = datetime.now(timezone.utc)

    try:
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            code = response.status
            if code in expected_codes:
                return HealthResult(
                    url=url,
                    status="UP",
                    http_code=code,
                    response_time_ms=round(elapsed_ms, 2),
                    message=f"Application responding with HTTP {code}",
                    checked_at=checked_at,
                )
            return HealthResult(
                url=url,
                status="DOWN",
                http_code=code,
                response_time_ms=round(elapsed_ms, 2),
                message=f"Unexpected HTTP status {code}; expected {sorted(expected_codes)}",
                checked_at=checked_at,
            )
    except urllib.error.HTTPError as exc:
        elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        if exc.code in expected_codes:
            return HealthResult(
                url=url,
                status="UP",
                http_code=exc.code,
                response_time_ms=round(elapsed_ms, 2),
                message=f"Application responding with HTTP {exc.code}",
                checked_at=checked_at,
            )
        return HealthResult(
            url=url,
            status="DOWN",
            http_code=exc.code,
            response_time_ms=round(elapsed_ms, 2),
            message=str(exc),
            checked_at=checked_at,
        )
    except urllib.error.URLError as exc:
        return HealthResult(
            url=url,
            status="DOWN",
            http_code=None,
            response_time_ms=None,
            message=f"Connection failed: {exc.reason}",
            checked_at=checked_at,
        )
    except TimeoutError:
        return HealthResult(
            url=url,
            status="DOWN",
            http_code=None,
            response_time_ms=None,
            message=f"Request timed out after {timeout}s",
            checked_at=checked_at,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP application health checker")
    parser.add_argument(
        "urls",
        nargs="+",
        help="URLs to check (e.g. http://localhost:4499 http://wisecow.local)",
    )
    parser.add_argument("--timeout", type=float, default=5.0, help="Request timeout in seconds")
    parser.add_argument(
        "--expected-codes",
        default="200",
        help="Comma-separated acceptable HTTP status codes (default: 200)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    expected = {int(code.strip()) for code in args.expected_codes.split(",") if code.strip()}
    results = [check_url(url, args.timeout, expected) for url in args.urls]

    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        for result in results:
            symbol = "✓" if result.status == "UP" else "✗"
            print(f"{symbol} [{result.status}] {result.url}")
            print(f"    HTTP: {result.http_code or 'N/A'} | Latency: {result.response_time_ms or 'N/A'} ms")
            print(f"    {result.message}")

    down_count = sum(1 for r in results if r.status == "DOWN")
    return 1 if down_count else 0


if __name__ == "__main__":
    sys.exit(main())
