#!/usr/bin/env python3
"""Build a USGS past-24-hour earthquake placefile for AguaceroWx."""

import json
import pathlib
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OUTPUT = "earthquakes_24h.txt"
USER_AGENT = "AguaceroWx-USGS-Earthquake-Placefile/1.5"
ASSET_BASE = "https://raw.githubusercontent.com/mookiemoo1103/earthquake/main/assets"

MAGNITUDE_BANDS = (
    (0.0, 1.9, "green", 1),
    (2.0, 3.9, "yellow", 2),
    (4.0, 4.9, "orange", 3),
    (5.0, 6.9, "red", 4),
    (7.0, 10.0, "purple", 5),
)


def select_icon(magnitude):
    if magnitude is None:
        return "gray", 6

    for lower, upper, color, icon_id in MAGNITUDE_BANDS:
        if lower <= float(magnitude) <= upper:
            return color, icon_id

    return "gray", 6


def local_datetime(timestamp_ms):
    """Convert a USGS timestamp to Central Time."""
    instant = datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=timezone.utc
    )
    local = instant.astimezone(ZoneInfo("America/Chicago"))

    return (
        local.strftime("%b %d, %Y"),
        local.strftime("%I:%M:%S %p %Z"),
    )


def main():
    # Download the latest USGS earthquake data.
    request = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": USER_AGENT},
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        feed = json.loads(response.read().decode("utf-8"))

    # Keep only earthquakes from the past 24 hours.
    cutoff_ms = int(
        (
            datetime.now(timezone.utc)
            - timedelta(hours=24)
        ).timestamp() * 1000
    )

    earthquakes = []

    for feature in feed.get("features", []):
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        event_time = props.get("time")

        if event_time is None or len(coordinates) < 3:
            continue

        event_time = int(event_time)

        if event_time < cutoff_ms:
            continue

        longitude, latitude, depth_km = coordinates[:3]

        if latitude is None or longitude is None:
            continue

        # Convert depth from kilometers to miles.
        depth_miles = (
            float(depth_km) * 0.621371
            if isinstance(depth_km, (int, float))
            else None
        )

        earthquakes.append({
            "time": event_time,
            "lat": float(latitude),
            "lon": float(longitude),
            "magnitude": props.get("mag"),
            "depth_miles": depth_miles,
        })

    earthquakes.sort(
        key=lambda item: item["time"],
        reverse=True
    )

    # Placefile definitions and existing icon assets.
    lines = [
        "; USGS Earthquakes - Past 24 Hours",
        "; Click an earthquake icon for date, time, and depth in miles.",
        "Title: USGS Earthquakes - Last 24 Hours",
        "RefreshSeconds: 10",
        'Font: 1, 12, 1, "Arial"',
        f'IconFile: 1, 32, 32, 16, 16, "{ASSET_BASE}/dot_green.png"',
        f'IconFile: 2, 32, 32, 16, 16, "{ASSET_BASE}/dot_yellow.png"',
        f'IconFile: 3, 32, 32, 16, 16, "{ASSET_BASE}/dot_orange.png"',
        f'IconFile: 4, 32, 32, 16, 16, "{ASSET_BASE}/dot_red.png"',
        f'IconFile: 5, 32, 32, 16, 16, "{ASSET_BASE}/dot_purple.png"',
        f'IconFile: 6, 32, 32, 16, 16, "{ASSET_BASE}/dot_gray.png"',
        "Color: 255 255 255",
    ]

    for quake in earthquakes:
        _, icon_id = select_icon(quake["magnitude"])

        magnitude = quake["magnitude"]
        magnitude_text = (
            f"{float(magnitude):.1f}"
            if magnitude is not None
            else "?"
        )

        # Center the magnitude label over the icon.
        text_width = len(magnitude_text) * 7
        x_offset = -round(text_width / 2)

        event_date, event_time = local_datetime(quake["time"])

        depth_text = (
            f'{quake["depth_miles"]:.1f} miles'
            if quake["depth_miles"] is not None
            else "Unknown"
        )

        # Click information: three stacked lines.
        hover_text = (
            f"Date: {event_date}\\n"
            f"Time: {event_time}\\n"
            f"Depth: {depth_text}"
        )

        lines.extend([
            f'Object: {quake["lat"]:.4f},{quake["lon"]:.4f}',
            f'  Icon: 0,0,000,{icon_id},1,"{hover_text}"',
            f'  Text: {x_offset},4,1,"{magnitude_text}"',
            "End:",
        ])

    if not earthquakes:
        lines.append(
            "; No USGS earthquakes were returned for the past 24 hours."
        )

    lines.append(
        f"; Events plotted: {len(earthquakes)}"
    )

    pathlib.Path(OUTPUT).write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(
        f"Generated {OUTPUT}: {len(earthquakes)} earthquake(s)."
    )


if __name__ == "__main__":
    main()
