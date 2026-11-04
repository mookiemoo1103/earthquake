#!/usr/bin/env python3
"""Build a USGS past-24-hour earthquake placefile for AguaceroWx."""
import json
import pathlib
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OUTPUT = "earthquakes_24h.txt"
USER_AGENT = "AguaceroWx-USGS-Earthquake-Placefile/1.3"
ASSET_BASE = "https://raw.githubusercontent.com/mookiemoo1103/earthquake/main/assets"

# Color bands retained from the previous version.
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

def clean_field(value):
    """Keep quotes and line breaks from breaking placefile object syntax."""
    return str(value or "").replace('"', "'").replace("\r", " ").replace("\n", " ")

def central_time(timestamp_ms):
    instant = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return instant.astimezone(ZoneInfo("America/Chicago")).strftime(
        "%b %d, %Y %I:%M:%S %p %Z"
    )

def main():
    req = urllib.request.Request(
        FEED_URL, headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        feed = json.loads(response.read().decode("utf-8"))

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    cutoff_ms = int(cutoff.timestamp() * 1000)
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

        magnitude = props.get("mag")
        mag_text = f"{float(magnitude):.1f}" if magnitude is not None else "?"
        place = clean_field(props.get("place") or "Location not reported")
        url = clean_field(props.get("url") or "")
        depth_text = (
            f"{float(depth_km):.1f} km"
            if isinstance(depth_km, (int, float)) else "Unknown"
        )
        earthquakes.append({
            "time": event_time,
            "lat": float(latitude),
            "lon": float(longitude),
            "mag": magnitude,
            "mag_text": mag_text,
            "place": place,
            "url": url,
            "depth": depth_text,
        })

    earthquakes.sort(key=lambda item: item["time"], reverse=True)

    lines = [
        "; USGS Earthquakes - Past 24 Hours",
        "; Magnitude text is horizontally centered over the icon.",
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
        _, icon_id = select_icon(quake["mag"])
        magnitude_text = quake["mag_text"]

        # Approximate Arial 12-pixel character width and center variable-width
        # magnitude labels on the icon's 0,0 hotspot.
        estimated_text_width = len(magnitude_text) * 7
        x_offset = -round(estimated_text_width / 2)

        tooltip = (
            f"Magnitude: {magnitude_text} | "
            f"Location: {quake['place']} | "
            f"Depth: {quake['depth']} | "
            f"Date/time: {central_time(quake['time'])} | "
            f"USGS: {quake['url']}"
        )
        tooltip = clean_field(tooltip)

        lines.extend([
            f"Object: {quake['lat']:.4f},{quake['lon']:.4f}",
            f'  Icon: 0,0,000,{icon_id},1,"{tooltip}"',
            f'  Text: {x_offset},4,1,"{magnitude_text}"',
            "End:",
        ])

    if not earthquakes:
        lines.append("; No USGS earthquakes were returned for the past 24 hours.")

    lines.append(f"; Events plotted: {len(earthquakes)}")
    pathlib.Path(OUTPUT).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT}: {len(earthquakes)} earthquake(s).")

if __name__ == "__main__":
    main()
