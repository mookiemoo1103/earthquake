# USGS Earthquakes — Past 24 Hours (AguaceroWx)

## Repository layout (must be preserved)
```text
.github/
  workflows/
    update-placefile.yml
assets/
  dot_green.png
  dot_yellow.png
  dot_orange.png
  dot_red.png
  dot_purple.png
  dot_gray.png
generate_placefile.py
earthquakes_24h.txt
README.md
```

## Display
- Small circular dot at each earthquake epicenter.
- Numeric magnitude label beside the dot, without an `M` prefix.
- Hover tooltip includes magnitude, location, depth, Central Time date/time, and USGS event URL.
- Rolling previous 24 hours from the public USGS GeoJSON feed.

## Run
GitHub Actions regenerates the placefile on its schedule or when manually run.
GitHub scheduled workflows run on a 5-minute cadence; USGS feed publication is independent.

## AguaceroWx
Use **Map Style → Custom Map Overlays → Open layer library → Live link** and paste:
https://raw.githubusercontent.com/mookiemoo1103/earthquake/main/earthquakes_24h.txt

AguaceroWx also supports placefile layers under **Edit Layers → Add Layer → Custom Layer**.
Placefile display options (Show icons, Show text, Icon size, Text size) are available in Edit Layer.
