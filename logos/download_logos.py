#!/usr/bin/env python3
"""
Clean logo downloader using Brandfetch API.
All logos come pre-transparent. We just convert to black.
Get your free API key at: brandfetch.com/developers
"""

import os, re, zipfile
from typing import Optional

import requests
from PIL import Image
from io import BytesIO

API_KEY = os.environ.get("BRANDFETCH_API_KEY", "").strip() or None  # set env or paste key below
if not API_KEY:
    API_KEY = "PASTE_YOUR_KEY_HERE"  # or get free key at brandfetch.com/developers

LOGOS = {
    "AdTech": {
        "cineverse":    "cineverse.com",
        "infillion":    "infillion.com",
        "wurl":         "wurl.com",
        "frequency":    "frequency.com",
        "justwatch":    "justwatch.com",
        "gumgum":       "gumgum.com",
        "kargo":        "kargo.com",
        "canvasspace":  "canvas.space",      # https://canvas.space/
        "magnite":      "magnite.com",       # SpringServe/Magnite
    },
    "StreamingPlatforms": {
        "sling":        "sling.com",
        "primevideo":   "primevideo.com",   # Prime
        "philo":        "philo.com",
        "lgchannels":   "lgchannels.com",    # LG Channels
        "anoki":        "anoki.ai",
        "localnow":     "localnow.com",
        "fubo":         "fubo.tv",
        "roku":         "roku.com",          # The Roku Channel
        "plex":         "plex.tv",
        "tubi":         "tubi.tv",
        "tablo":        "tablotv.com",
        "youtube":      "youtube.com",       # YouTube TV VOD
        "trc":          "trc.com",          # TRC – confirm domain
        "pluto":        "pluto.tv",
        "directv":      "directv.com",       # DirecTV
        "tivo":         "tivo.com",
        "freecast":     "freecast.com",
    },
    "TVPlatforms": {
        "vizio":        "vizio.com",         # VIZIO Watch Free
        "hp":           "hp.com",
        "whale":        "whale.io",          # or confirm domain
        "vidaa":        "vidaa.com",         # Vidaa Hisense
        "hisense":      "hisense.com",
        "tcl":          "tcl.com",
        "rakuten":      "rakuten.com",
        "lg":           "lg.com",            # LG (Channels is in Streaming)
    }
}

OUT = "CTV_Logos"
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


def to_black_png(data: bytes) -> Optional[bytes]:
    """Convert any PNG to solid black on transparent background."""
    img = Image.open(BytesIO(data)).convert("RGBA")
    pixels = list(img.getdata())
    # Check result isn't empty
    visible = sum(1 for p in pixels if p[3] > 10)
    if visible < len(pixels) * 0.005:
        return None
    new_pixels = [(0, 0, 0, p[3]) if p[3] > 10 else (0, 0, 0, 0) for p in pixels]
    img.putdata(new_pixels)
    img.thumbnail((800, 800))
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def to_black_svg(data: bytes) -> bytes:
    """Replace all colors in SVG with black."""
    svg = data.decode("utf-8", errors="replace")
    svg = re.sub(r'fill\s*=\s*"(?!none)[^"]*"',   'fill="#000000"',   svg)
    svg = re.sub(r'fill\s*:\s*(?!none)[^;}"]+',    'fill:#000000',     svg)
    svg = re.sub(r'stroke\s*=\s*"(?!none)[^"]*"',  'stroke="#000000"', svg)
    svg = re.sub(r'stop-color\s*:\s*[^;}"]+',       'stop-color:#000000', svg)
    return svg.encode("utf-8")


def fetch_logo(domain: str):
    """
    Call Brandfetch API, return (ext, data) where ext is 'svg' or 'png'.
    Prefers SVG, falls back to PNG.
    """
    url = f"https://api.brandfetch.io/v2/brands/{domain}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return None, None

    brand = r.json()
    logos = brand.get("logos", [])

    svg_url = png_url = None

    for logo in logos:
        # Prefer the main wordmark logo
        if logo.get("type") not in ("logo", "symbol"):
            continue
        for fmt in logo.get("formats", []):
            src = fmt.get("src", "")
            if not svg_url and fmt.get("format") == "svg":
                svg_url = src
            if not png_url and fmt.get("format") == "png":
                png_url = src

    # Try SVG first
    for (url, ext) in [(svg_url, "svg"), (png_url, "png")]:
        if not url:
            continue
        try:
            r2 = requests.get(url, headers=HEADERS, timeout=15)
            if r2.status_code == 200 and len(r2.content) > 500:
                return ext, r2.content
        except Exception:
            continue

    return None, None


def main():
    if not API_KEY or API_KEY == "PASTE_YOUR_KEY_HERE":
        print("Set BRANDFETCH_API_KEY or edit API_KEY in this script. Get a key at: brandfetch.com/developers")
        raise SystemExit(1)
    # Clean start
    import shutil
    if os.path.exists(OUT):
        shutil.rmtree(OUT)

    failed = []

    for category, brands in LOGOS.items():
        folder = os.path.join(OUT, category)
        os.makedirs(folder, exist_ok=True)

        for name, domain in brands.items():
            print(f"  {name} ({domain})...", end=" ", flush=True)

            ext, data = fetch_logo(domain)

            if not data:
                print("✗ not found")
                failed.append(name)
                continue

            if ext == "svg":
                final = to_black_svg(data)
                path = os.path.join(folder, f"{name}.svg")
                with open(path, "wb") as f:
                    f.write(final)
                print("✓ SVG")

            else:  # png
                final = to_black_png(data)
                if not final:
                    print("✗ empty after processing")
                    failed.append(name)
                    continue
                path = os.path.join(folder, f"{name}.png")
                with open(path, "wb") as f:
                    f.write(final)
                print("✓ PNG")

    # ZIP
    zip_path = f"{OUT}.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for root, dirs, files in os.walk(OUT):
            for file in files:
                full = os.path.join(root, file)
                zf.write(full)

    print(f"\n{'='*50}")
    print(f"  ✓ ZIP saved: {zip_path}")
    if failed:
        print(f"  ✗ Still need manual download ({len(failed)}):")
        for f in failed:
            print(f"      • {f}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
