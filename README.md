# USGS Earthquake Placefile for AguaceroWx

This repository publishes a USGS earthquake placefile for the past 24 hours. It uses six transparent concentric-ring icons, colored by magnitude, with the magnitude number centered over each icon.

## Files in this package

- `generate_placefile.py` — downloads the USGS GeoJSON feed and generates the placefile.
- `earthquakes_24h.txt` — generated placefile consumed by AguaceroWx.
- `assets/` — six transparent PNG icons used by the placefile.
- `.github/workflows/update-placefile.yml` — scheduled GitHub Actions workflow.

## Install / replace the repository contents

1. Extract the ZIP file.
2. Open the `earthquake` GitHub repository.
3. Upload **all contents inside this package folder** to the repository root. Preserve the `.github/workflows/` and `assets/` folder structure.
4. Replace files when GitHub asks, then commit to the `main` branch.
5. In GitHub, open **Actions** → **Update USGS Earthquake Placefile** → **Run workflow**.
6. Wait for the workflow to finish successfully.

The repository should contain:

```
earthquake/
├── .github/
│   └── workflows/
│       └── update-placefile.yml
├── assets/
│   ├── dot_green.png
│   ├── dot_yellow.png
│   ├── dot_orange.png
│   ├── dot_red.png
│   ├── dot_purple.png
│   └── dot_gray.png
├── generate_placefile.py
├── earthquakes_24h.txt
└── README.md
```

## AguaceroWx placefile URL

Use this URL in AguaceroWx:

`https://raw.githubusercontent.com/mookiemoo1103/earthquake/main/earthquakes_24h.txt`

## Magnitude colors

- 0.0–1.9: green
- 2.0–3.9: yellow
- 4.0–4.9: orange
- 5.0–6.9: red
- 7.0 and above: purple
- Missing/unknown magnitude: gray

## Update frequency note

The placefile advertises a 10-second refresh interval to the client. The USGS feed and GitHub Actions do not update every 10 seconds: the workflow is scheduled every 5 minutes, and the USGS feed has its own publication cadence. A client refresh cannot make new source data appear before GitHub republishes the file.
