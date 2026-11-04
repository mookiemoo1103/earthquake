# USGS Earthquakes — Last 24 Hours (AguaceroWx)

This repository generates a GRLevelX-style `.txt` placefile from the public USGS
GeoJSON feed and is designed to load as a live placefile in AguaceroWx.

## What it displays

- Earthquakes from the previous rolling 24 hours
- Magnitude labels at each epicenter
- Magnitude colors: green (M0.0–1.9), yellow (M2.0–3.9), orange (M4.0–4.9),
  red (M5.0–6.9), purple (M7.0+)
- Hover details: magnitude, location, depth, UTC origin time, and USGS event link

## Data source

USGS public GeoJSON feed:
https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson

The feed is maintained by USGS and is not guaranteed to publish new events every
10 seconds.

## Install on GitHub

1. Create a **public** GitHub repository.
2. Upload all files from this folder, including the hidden `.github` folder.
3. In the repository, open **Actions** and enable workflows if GitHub prompts you.
4. Open **Update USGS Earthquake Placefile** and click **Run workflow** once.
5. After it completes, open `earthquakes_24h.txt` and click **Raw**.
6. Copy the raw URL. It will look like:
   `https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPOSITORY/main/earthquakes_24h.txt`

## Load in AguaceroWx

1. Open **Map Style** → **Custom map overlays** → **Open layer library**.
2. Choose **Live link**.
3. Paste the raw GitHub URL from step 6 and continue.
4. Save & Load the placefile.

AguaceroWx supports GRLevelX-style placefiles. In the placefile settings, set the
refresh interval to **15 seconds** (the shortest interval listed in the current
AguaceroWx guide), or leave it on the placefile's own refresh setting if your
version honors `RefreshSeconds: 10`.

## Important refresh limitation

The generated placefile contains `RefreshSeconds: 10`, so compatible software can
request the URL every 10 seconds. However:

- AguaceroWx's current guide lists selectable refresh intervals starting at
  **15 seconds**, not 10 seconds.
- GitHub Actions scheduled workflows run on a minimum practical 5-minute cadence.
- USGS's all-day feed generally updates on roughly a minute cadence.

Therefore, this GitHub-hosted version is compatible and will refresh in AguaceroWx,
but the file content will normally change on the GitHub workflow cadence (about
5 minutes), not every 10 seconds. The 10-second setting only controls how often
the client re-downloads the currently hosted file.

## Run locally

Requires Python 3. The script uses only the Python standard library:

```bash
python3 generate_placefile.py
```

It writes `earthquakes_24h.txt` in the current folder.
