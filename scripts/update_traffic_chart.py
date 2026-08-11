#!/usr/bin/env python3
"""Fetch GoatCounter aggregates and render a README-safe SVG trend chart."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SITE_CODE_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
CHART_DAYS = 30
WIDTH = 900
HEIGHT = 270
LEFT = 62
RIGHT = 30
TOP = 82
BOTTOM = 50


def fetch_stats(site_code: str, token: str, today: dt.date) -> dict:
    start = today - dt.timedelta(days=CHART_DAYS - 1)
    end = today + dt.timedelta(days=1)
    query = urllib.parse.urlencode(
        {
            "start": f"{start.isoformat()}T00:00:00Z",
            "end": f"{end.isoformat()}T00:00:00Z",
        }
    )
    url = f"https://{site_code}.goatcounter.com/api/v0/stats/total?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "papernote-traffic-chart/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        response_text = error.read().decode("utf-8", errors="replace").strip()
        try:
            response_payload = json.loads(response_text)
            detail = response_payload.get("error") or response_payload.get("errors")
        except json.JSONDecodeError:
            detail = response_text
        message = f"GoatCounter API returned HTTP {error.code}"
        if detail:
            message += f": {detail}"
        raise SystemExit(message) from None


def daily_series(payload: dict, today: dt.date) -> list[tuple[dt.date, int]]:
    start = today - dt.timedelta(days=CHART_DAYS - 1)
    values: dict[dt.date, int] = {}
    for item in payload.get("stats", []):
        day_text = item.get("day")
        if not day_text:
            continue
        day = dt.date.fromisoformat(day_text[:10])
        values[day] = int(item.get("daily") or sum(item.get("hourly") or []))
    return [
        (start + dt.timedelta(days=offset), values.get(start + dt.timedelta(days=offset), 0))
        for offset in range(CHART_DAYS)
    ]


def render_svg(series: list[tuple[dt.date, int]], updated_at: dt.datetime) -> str:
    plot_width = WIDTH - LEFT - RIGHT
    plot_height = HEIGHT - TOP - BOTTOM
    values = [value for _, value in series]
    maximum = max(max(values, default=0), 1)

    points: list[tuple[float, float]] = []
    for index, (_, value) in enumerate(series):
        x = LEFT + plot_width * index / max(len(series) - 1, 1)
        y = TOP + plot_height * (1 - value / maximum)
        points.append((x, y))

    line_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area_points = (
        f"{LEFT},{TOP + plot_height} "
        + line_points
        + f" {LEFT + plot_width},{TOP + plot_height}"
    )
    total = sum(values)
    start_label = series[0][0].strftime("%m-%d")
    middle_label = series[len(series) // 2][0].strftime("%m-%d")
    end_label = series[-1][0].strftime("%m-%d")
    middle_x = points[len(points) // 2][0]
    update_label = updated_at.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    grid = []
    for fraction in (0, 0.5, 1):
        y = TOP + plot_height * fraction
        label = round(maximum * (1 - fraction))
        grid.append(
            f'<line x1="{LEFT}" y1="{y:.1f}" x2="{LEFT + plot_width}" y2="{y:.1f}" '
            'stroke="#d8dee4" stroke-width="1"/>'
            f'<text x="{LEFT - 12}" y="{y + 4:.1f}" text-anchor="end" '
            'fill="#57606a" font-size="11">'
            f"{label}</text>"
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">papernote 最近 30 天访问趋势</title>
  <desc id="desc">过去 30 天共 {total} 次访问，单日最高 {max(values, default=0)} 次。</desc>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="#ffffff" stroke="#d0d7de"/>
  <text x="{LEFT}" y="31" fill="#24292f" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="18" font-weight="600">papernote · 最近 30 天访问趋势</text>
  <text x="{LEFT}" y="55" fill="#57606a" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="12">过去 30 天 {total} 次访问 · 更新于 {update_label}</text>
  <g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">{''.join(grid)}</g>
  <polygon points="{area_points}" fill="#2da44e" fill-opacity="0.12"/>
  <polyline points="{line_points}" fill="none" stroke="#1a7f37" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  <text x="{LEFT}" y="{HEIGHT - 22}" fill="#57606a" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="11">{start_label}</text>
  <text x="{middle_x:.1f}" y="{HEIGHT - 22}" text-anchor="middle" fill="#57606a" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="11">{middle_label}</text>
  <text x="{LEFT + plot_width}" y="{HEIGHT - 22}" text-anchor="end" fill="#57606a" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="11">{end_label}</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("assets/traffic.svg"))
    parser.add_argument("--fixture", type=Path, help="Read API JSON from a local fixture")
    parser.add_argument("--today", type=dt.date.fromisoformat, default=dt.datetime.now(dt.timezone.utc).date())
    args = parser.parse_args()

    if args.fixture:
        payload = json.loads(args.fixture.read_text(encoding="utf-8"))
    else:
        site_code = os.environ.get("GOATCOUNTER_CODE", "").strip().lower()
        token = os.environ.get("GOATCOUNTER_API_TOKEN", "").strip()
        if not SITE_CODE_RE.fullmatch(site_code):
            raise SystemExit("GOATCOUNTER_CODE is missing or invalid")
        if not token:
            raise SystemExit("GOATCOUNTER_API_TOKEN is missing")
        payload = fetch_stats(site_code, token, args.today)

    series = daily_series(payload, args.today)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_svg(series, dt.datetime.now(dt.timezone.utc)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
