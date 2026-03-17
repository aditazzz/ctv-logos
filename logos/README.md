# CTV / Streaming & Ad Tech Logos

**35 brand logos** — fetched via the **Brandfetch API**, output as **Black**, **White**, and **Color** (SVG or PNG), max 1000px.

---

## What’s included

| Category | Brands |
|----------|--------|
| **Ad tech** (9) | Cineverse, Infillion, Wurl, Frequency, JustWatch, GumGum, Kargo, Canvas Space, Magnite |
| **Streaming** (18) | Sling, Prime, Philo, LG Channels, Anoki, Local Now, Fubo, Roku Channel, Plex, Tubi, Tablo, YouTube TV VOD, TRC, Pluto, DirecTV, TiVo, Freecast |
| **TV / devices** (8) | VIZIO Watch Free, HP, Whale, Vidaa, Hisense, TCL, Rakuten, LG |

Output is **CTV_Logos/Black/**, **CTV_Logos/White/**, and **CTV_Logos/Color/** (each with AdTech, StreamingPlatforms, TVPlatforms). Max dimension 1000px.

---

## Quick start

1. Get a free API key at [brandfetch.com/developers](https://brandfetch.com/developers).
2. In `download_logos.py`, set `API_KEY = "your_key_here"`.
3. Install and run:
   ```bash
   pip install -r requirements.txt
   python download_logos.py
   ```
4. **Output**
   - Folders: `CTV_Logos/Black/`, `CTV_Logos/White/`, `CTV_Logos/Color/` (each with AdTech, StreamingPlatforms, TVPlatforms). Max 1000px.
   - Zip: `CTV_Logos.zip` — same structure for easy sharing.

**Requirements:** Python 3.9+, `requests`, `Pillow` (see `requirements.txt`).

---

## Summary of what we built

1. **Logo list** — One place for 35 CTV/streaming/ad tech brands, mapped to domains for Brandfetch.
2. **Brandfetch downloader** — `download_logos.py` calls the Brandfetch API by domain, prefers SVG and falls back to PNG.
3. **Black-on-transparent** — SVGs are recolored to black via regex; PNGs are converted to black with original alpha and thumbnailed to 800px max.
4. **Category subfolders** — Logos go into `CTV_Logos/AdTech/`, `CTV_Logos/StreamingPlatforms/`, and `CTV_Logos/TVPlatforms/`.
5. **ZIP** — Script builds `CTV_Logos.zip` automatically.
6. **Python 3.9 compatible** — Type hints use `Optional[bytes]` instead of `bytes | None`.

---

## Manual fallbacks (optional)

If a brand is missing from Brandfetch or you need an alternate source, the links below point to Wikimedia Commons and other logo sites for manual download.

- [Cineverse](https://commons.wikimedia.org/wiki/File:Cineverse_logo.jpg) · [Infillion](https://commons.wikimedia.org/wiki/File:Infillionlogo.svg) · [Wurl](https://brand.wurl.com/) · [JustWatch](https://commons.wikimedia.org/wiki/File:JustWatch_Logo.svg)
- [Sling](https://commons.wikimedia.org/wiki/File:Sling_TV_logo.svg) · [Prime Video](https://commons.wikimedia.org/wiki/File:Prime_Video_logo_(2024).svg) · [Fubo](https://commons.wikimedia.org/wiki/File:Fubo_2023.svg) · [VIZIO](https://commons.wikimedia.org/wiki/File:VIZIO_logo.svg)
- [Roku Channel](https://commons.wikimedia.org/wiki/File:The_Roku_Channel_Logo.svg) · [Pluto TV](https://commons.wikimedia.org/wiki/File:Pluto_TV_logo_2024.svg) · [TiVo](https://commons.wikimedia.org/wiki/File:TiVo_logo_2011_RGB.svg)
- [GumGum](https://iconlogovector.com/logo/gumgum) · [Magnite](https://companieslogo.com/magnite/logo/) · [Tubi](https://iconlogovector.com/logo/tubi-tubi-tv) · [Plex](https://iconlogovector.com/logo/plex) · [YouTube TV](https://latestlogo.com/logos/youtube-tv/) · [Rakuten TV](https://latestlogo.com/logos/rakuten-tv/)

Logos are often trademarked; use per each brand’s guidelines for public or commercial use.
