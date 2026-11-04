#!/usr/bin/env python3
"""Generate an AguaceroWx-compatible GRLevelX placefile from the USGS past-day feed."""
import json
import pathlib
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OUTPUT = "earthquakes_24h.txt"
USER_AGENT = "AguaceroWx-USGS-Earthquake-Placefile/1.1 (public data visualization)"
GITHUB_RAW = "https://raw.githubusercontent.com/mookiemoo1103/earthquake/main/assets"

# Magnitude color bands and matching small circular PNG markers.
BANDS = [
    (0.0, 1.9, "green", (65, 190, 105)),
    (2.0, 3.9, "yellow", (245, 210, 55)),
    (4.0, 4.9, "orange", (245, 145, 45)),
    (5.0, 6.9, "red", (230, 65, 55)),
    (7.0, 10.0, "purple", (180, 70, 220)),
]

def band_for(magnitude):
    if magnitude is None:
        return "gray", (190, 190, 190)
    for low, high, name, color in BANDS:
        if low <= magnitude <= high:
            return name, color
    return "gray", (190, 190, 190)

def safe_text(value):
    return str(value).replace("\\", "\\\\").replace('"', "'").replace("\r", " ").replace("\n", " ")

def local_time(ms):
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(ZoneInfo("America/Chicago"))
    return dt.strftime("%b %d, %Y %I:%M:%S %p %Z")

def main():
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    now = datetime.now(timezone.utc)
    cutoff_ms = int((now - timedelta(hours=24)).timestamp() * 1000)
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
        place = props.get("place") or "Location not reported"
        url = props.get("url") or ""
        magnitude_label = f"{float(magnitude):.1f}" if isinstance(magnitude, (int, float)) else "?"
        events.append((event_ms, float(lat), float(lon), depth_km, magnitude, place, url, magnitude_label))

    events.sort(key=lambda item: item[0], reverse=True)

    lines = [
        "; USGS Earthquakes - Past 24 Hours",
        "; Colored dot marker with magnitude label; hover marker for event details.",
        "Title: USGS Earthquakes - Last 24 Hours",
        "RefreshSeconds: 10",
        'Font: 1, 12, 1, "Arial"',
        # Each dot is a tiny transparent PNG, hosted alongside this script in GitHub.
        'IconFile: 1, 18, 18, 8, 8, "' + GITHUB_RAW + '/dot_green.png"',
        'IconFile: 2, 18, 18, 8, 8, "' + GITHUB_RAW + '/dot_yellow.png"',
        'IconFile: 3, 18, 18, 8, 8, "' + GITHUB_RAW + '/dot_orange.png"',
        'IconFile: 4, 18, 18, 8, 8, "' + GITHUB_RAW + '/dot_red.png"',
        'IconFile: 5, 18, 18, 8, 8, "' + GITHUB_RAW + '/dot_purple.png"',
        'IconFile: 6, 18, 18, 8, 8, "' + GITHUB_RAW + '/dot_gray.png"',
    ]

    icon_numbers = {"green": 1, "yellow": 2, "orange": 3, "red": 4, "purple": 5, "gray": 6}

    for event_ms, lat, lon, depth_km, magnitude, place, url, mag_label in events:
        band, _ = band_for(magnitude)
        depth_label = f"{float(depth_km):.1f} km" if isinstance(depth_km, (int, float)) else "Unknown"
        mag_full = f"{float(magnitude):.1f}" if isinstance(magnitude, (int, float)) else "Unknown"
        hover = (
            f"Magnitude: {mag_full}\\n"
            f"Location: {place}\\n"
            f"Depth: {depth_label}\\n"
            f"Date/time: {local_time(event_ms)}\\n"
            f"USGS: {url}"
        )
        # The icon is the dot; magnitude is a separate plain numeric label.
        # Hovering the dot displays the full event details and local date/time.
        lines.extend([
            f"Object: {lat:.4f},{lon:.4f}",
            f'  Icon: 0,0,000,{icon_numbers[band]},1,"{safe_text(hover)}"',
            f'  Text: 12,0,1,"{mag_label}"',
            "End:",
        ])

    if not events:
        lines.append('Place: 0, 0, No earthquakes reported in the last 24 hours')

    lines.append(f"; Events plotted: {len(events)}")
    pathlib.Path(OUTPUT).write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(events)} earthquake markers.")

if __name__ == "__main__":
    main()
