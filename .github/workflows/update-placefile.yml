#!/usr/bin/env python3
"""Generate an AguaceroWx-compatible GRLevelX placefile from the USGS past-day feed."""
import json
import pathlib
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OUTPUT = "earthquakes_24h.txt"
USER_AGENT = "AguaceroWx-USGS-Earthquake-Placefile/1.2"
GITHUB_RAW = "https://raw.githubusercontent.com/mookiemoo1103/earthquake/main/assets"

# Magnitude bands: each band uses its matching transparent PNG.
BANDS = [
    (0.0, 1.9, "green"),
    (2.0, 3.9, "yellow"),
    (4.0, 4.9, "orange"),
    (5.0, 6.9, "red"),
    (7.0, 10.0, "purple"),
]

def band_for(magnitude):
    if magnitude is None:
        return "gray"
    for low, high, name in BANDS:
        if low <= magnitude <= high:
            return name
    return "gray"

def safe_text(value):
    return (str(value).replace("\\", "\\\\").replace('"', "'")
            .replace("\r", " ").replace("\n", " "))

def local_time(ms):
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.astimezone(ZoneInfo("America/Chicago")).strftime(
        "%b %d, %Y %I:%M:%S %p %Z"
    )

def main():
    request = urllib.request.Request(
        FEED_URL, headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    cutoff_ms = int(
        (datetime.now(timezone.utc) - timedelta(hours=24)).timestamp() * 1000
    )
    events = []

    for feature in data.get("features", []):
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or []
        if len(coords) < 3 or props.get("time") is None:
            continue

        event_ms = int(props["time"])
        if event_ms < cutoff_ms:
            continue

        lon, lat, depth_km = coords[:3]
        if lat is None or lon is None:
            continue

        magnitude = props.get("mag")
        mag_label = (
            f"{float(magnitude):.1f}"
            if isinstance(magnitude, (int, float)) else "?"
        )
        events.append((
            event_ms, float(lat), float(lon), depth_km, magnitude,
            props.get("place") or "Location not reported",
            props.get("url") or "", mag_label
        ))

    events.sort(key=lambda item: item[0], reverse=True)

    lines = [
        "; USGS Earthquakes - Past 24 Hours",
        "; Magnitude number is centered over each colored earthquake icon.",
        "Title: USGS Earthquakes - Last 24 Hours",
        "RefreshSeconds: 10",
        'Font: 1, 12, 1, "Arial"',
        f'IconFile: 1, 32, 32, 16, 16, "{GITHUB_RAW}/dot_green.png"',
        f'IconFile: 2, 32, 32, 16, 16, "{GITHUB_RAW}/dot_yellow.png"',
        f'IconFile: 3, 32, 32, 16, 16, "{GITHUB_RAW}/dot_orange.png"',
        f'IconFile: 4, 32, 32, 16, 16, "{GITHUB_RAW}/dot_red.png"',
        f'IconFile: 5, 32, 32, 16, 16, "{GITHUB_RAW}/dot_purple.png"',
        f'IconFile: 6, 32, 32, 16, 16, "{GITHUB_RAW}/dot_gray.png"',
        "Color: 255 255 255",
    ]

    icon_numbers = {
        "green": 1, "yellow": 2, "orange": 3,
        "red": 4, "purple": 5, "gray": 6
    }

    for event_ms, lat, lon, depth_km, magnitude, place, url, mag_label in events:
        band = band_for(magnitude)
        depth_label = (
            f"{float(depth_km):.1f} km"
            if isinstance(depth_km, (int, float)) else "Unknown"
        )
        mag_full = (
            f"{float(magnitude):.1f}"
            if isinstance(magnitude, (int, float)) else "Unknown"
        )
        hover = (
            f"Magnitude: {mag_full}\\n"
            f"Location: {place}\\n"
            f"Depth: {depth_label}\\n"
            f"Date/time: {local_time(event_ms)}\\n"
            f"USGS: {url}"
        )

        lines.extend([
            f"Object: {lat:.4f},{lon:.4f}",
            f'  Icon: 0,0,000,{icon_numbers[band]},1,"{safe_text(hover)}"',
            # Text is offset left by about half the label width, centering it
            # horizontally on the icon hotspot. The small vertical offset
            # centers the text over the icon in the map display.
            f'  Text: -9,4,1,"{mag_label}"',
            "End:",
        ])

    if not events:
        lines.append("Place: 0, 0, No earthquakes reported in the last 24 hours")

    lines.append(f"; Events plotted: {len(events)}")
    pathlib.Path(OUTPUT).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(events)} earthquake markers.")

if __name__ == "__main__":
    main()
