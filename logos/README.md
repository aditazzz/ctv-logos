# CTV / Entertainment Logos

**35 entertainment brand logos** — fetched via the **Brandfetch API**, output as **Black**, **White**, and **Color** (SVG or PNG), max 1000px.

---

## What’s included

| Category       | Count | Brands (sample) |
|----------------|-------|-----------------|
| **Entertainment** | 35 | Airbud, Alliance Media, BMG, Cineverse, Filmhub, Lionsgate, Monarch, Shoreline, Stingray, Tastemade, Tricoast, Video Elephant, Wonderphil, … |

Output: **CTV_Logos/Black/Entertainment/**, **CTV_Logos/White/Entertainment/**, **CTV_Logos/Color/Entertainment/**. Max dimension 1000px. The script also builds **CTV_Logos.zip** with the same structure.

---

## Quick start

1. **Get a free API key** at [brandfetch.com/developers](https://brandfetch.com/developers).
2. **Provide the key** in one of these ways:
   - **Option A:** Put the key in `logos/.brandfetch_key` (one line, no quotes). This file is gitignored.
   - **Option B:** `export BRANDFETCH_API_KEY='your_key'` before running.
3. **Run** from the project root (use the project venv so `requests` and `Pillow` are available):
   ```bash
   ./logos/run.sh
   ```
   or:
   ```bash
   .venv/bin/python logos/download_logos.py
   ```
4. **Output**
   - Folders: `CTV_Logos/Black/Entertainment/`, `CTV_Logos/White/Entertainment/`, `CTV_Logos/Color/Entertainment/` (max 1000px).
   - Zip: `CTV_Logos.zip` — same structure for easy sharing.

**Requirements:** Python 3.9+, `requests`, `Pillow` (see project root `requirements.txt` or install in the project venv).

---

## Summary

1. **Logo list** — One place for 35 entertainment brands, mapped to domains for Brandfetch (`download_logos.py` → `LOGOS`).
2. **Brandfetch downloader** — Script calls the API by domain; prefers SVG, falls back to PNG.
3. **Black / White / Color** — SVGs recolored via regex; PNGs converted with original alpha, resized to max 1000px.
4. **ZIP** — Script builds `CTV_Logos.zip` automatically.

Some brands may be missing or empty (e.g. not in Brandfetch or API timeout); the script prints a short list of those for manual fallback.
