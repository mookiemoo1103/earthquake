#!/usr/bin/env python3
"""Generate an AguaceroWx-compatible GRLevelX placefile from the USGS past-day feed."""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OUTPUT = "earthquakes_24h.txt"
USER_AGENT = "AguaceroWx-USGS-Earthquake-Placefile/1.0 (public data visualization)"

COLORS = [
    (0.0, 1.9, (65, 190, 105)),
    (2.0, 3.9, (245, 210, 55)),
    (4.0, 4.9, (245, 145, 45)),
    (5.0, 6.9, (230, 65, 55)),
    (7.0, 10.0, (180, 70, 220)),
]

def color_for(magnitude):
    if magnitude is None:
        return (190, 190, 190)
    for low, high, color in COLORS:
        if low <= magnitude <= high:
            return color
    return (190, 190, 190)

def safe_placefile_text(value):
    return str(value).replace("\\", "\\\\").replace('"', "'").replace("\r", " ").replace("\n", " ")

def utc_string(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

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
        event_time = int(props["time"])
        if event_time < cutoff_ms:
            continue

        lon, lat, depth_km = coords[:3]
        if lat is None or lon is None:
            continue
        mag = props.get("mag")
        place = props.get("place") or "Location not reported"
        url = props.get("url") or ""
        title = props.get("title") or (f"M{mag}" if mag is not None else "Earthquake")
        events.append((event_time, float(lat), float(lon), depth_km, mag, place, url, title))

    events.sort(key=lambda item: item[0], reverse=True)

    lines = [
        "; USGS Earthquakes - Past 24 Hours",
        "; Generated from the USGS public GeoJSON feed.",
        "; GRLevelX-style placefile compatible with AguaceroWx.",
        "Title: USGS Earthquakes - Last 24 Hours",
        "RefreshSeconds: 10",
        "Font: 1, 12, 1, \"Arial\"",
    ]

    for event_time, lat, lon, depth_km, mag, place, url, title in events:
        magnitude_text = f"M{mag:.1f}" if isinstance(mag, (int, float)) else "M?"
        depth_text = f"{depth_km:.1f} km" if isinstance(depth_km, (int, float)) else "Unknown"
        hover = (
            f"{title} | {place} | Depth: {depth_text} | "
            f"Time: {utc_string(event_time)} | {url}"
        )
        r, g, b = color_for(mag)
        lines.append(f"Color: {r} {g} {b}")
        lines.append(f'Text: {lat:.4f}, {lon:.4f}, 1, "{magnitude_text}", "{safe_placefile_text(hover)}"')

    if not events:
        lines.extend([
            "Color: 190 190 190",
            'Place: 0, 0, No earthquakes reported in the last 24 hours',
        ])

    lines.append(f"; Events plotted: {len(events)}")
    pathlib.Path(OUTPUT).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(events)} earthquake markers.")

if __name__ == "__main__":
    main()
