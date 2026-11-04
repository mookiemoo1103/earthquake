def local_datetime(timestamp_ms):
    instant = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    local = instant.astimezone(ZoneInfo("America/Chicago"))
    return (
        local.strftime("%b %d, %Y"),
        local.strftime("%I:%M:%S %p %Z"),
    )

def main():
    request = urllib.request.Request(
        FEED_URL, headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        feed = json.loads(response.read().decode("utf-8"))

    cutoff_ms = int(
        (datetime.now(timezone.utc) - timedelta(hours=24)).timestamp() * 1000
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

        magnitude = props.get("mag")
        magnitude_text = (
            f"{float(magnitude):.1f}" if magnitude is not None else "?"
        )
        depth_text = (
            f"{float(depth_km):.1f} km"
            if isinstance(depth_km, (int, float)) else "Unknown"
        )

        earthquakes.append({
            "time": event_time,
            "lat": float(latitude),
            "lon": float(longitude),
            "magnitude": magnitude,
            "magnitude_text": magnitude_text,
            "place": clean_field(props.get("place") or "Location not reported"),
            "url": clean_field(props.get("url") or ""),
            "depth": depth_text,
        })

    earthquakes.sort(key=lambda item: item["time"], reverse=True)

    lines = [
        "; USGS Earthquakes - Past 24 Hours",
        "; Hover over an earthquake icon for event details.",
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
        magnitude_text = quake["magnitude_text"]

        # Keep the magnitude label centered over the icon.
        text_width = len(magnitude_text) * 7
        x_offset = -round(text_width / 2)

        event_date, event_time = local_datetime(quake["time"])
        magnitude_detail = (
            f"{float(quake['magnitude']):.1f}"
            if quake["magnitude"] is not None else "Unknown"
        )

        # GRLevelX/AguaceroWx hoverText is the final quoted field in Icon.
        # Keep it on one line and avoid embedded quote characters.
        hover_text = clean_field(
            f"USGS EARTHQUAKE | "
            f"Magnitude: {magnitude_detail} | "
            f"Date: {event_date} | "
            f"Time: {event_time} | "
            f"Location: {quake['place']} | "
            f"Depth: {quake['depth']} | "
            f"USGS Event: {quake['url']}"
        )

        lines.extend([
            f"Object: {quake['lat']:.4f},{quake['lon']:.4f}",
            f'  Icon: 0,0,000,{icon_id},1,"{hover_text}"',
            f'  Text: {x_offset},4,1,"{magnitude_text}"',
            "End:",
        ])

    if not earthquakes:
        lines.append("; No USGS earthquakes were returned for the past 24 hours.")

    lines.append(f"; Events plotted: {len(earthquakes)}")
    pathlib.Path(OUTPUT).write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(f"Generated {OUTPUT}: {len(earthquakes)} earthquake(s).")

if __name__ == "__main__":
    main()
