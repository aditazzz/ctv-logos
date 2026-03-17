#!/usr/bin/env python3
"""
Clean logo downloader using Brandfetch API.
Outputs BLACK, WHITE, and COLOR versions (max 1000px). B/W for light/dark backgrounds; color for brand-accurate use.
Get your key at: brandfetch.com/developers
"""

import os, re, zipfile
from typing import Optional

import requests
from PIL import Image
from io import BytesIO

def _load_api_key():
    key = os.environ.get("BRANDFETCH_API_KEY", "").strip() or None
    if key:
        return key
    # Try key file next to this script (gitignored)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, ".brandfetch_key")
    if os.path.isfile(key_file):
        with open(key_file) as f:
            key = (f.readline() or "").strip()
            if key:
                return key
    return "PASTE_YOUR_KEY_HERE"


API_KEY = _load_api_key()

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
MAX_SIZE = 1000   # max width/height in px (800–1000 ideal for decks)
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


def _recolor_png(data: bytes, color: tuple) -> Optional[bytes]:
    """Convert PNG to solid (r,g,b) on transparent; max dimension MAX_SIZE."""
    img = Image.open(BytesIO(data)).convert("RGBA")
    pixels = list(img.getdata())
    visible = sum(1 for p in pixels if p[3] > 10)
    if visible < len(pixels) * 0.005:
        return None
    r, g, b = color
    new_pixels = [(r, g, b, p[3]) if p[3] > 10 else (0, 0, 0, 0) for p in pixels]
    img.putdata(new_pixels)
    img.thumbnail((MAX_SIZE, MAX_SIZE))
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def to_black_png(data: bytes) -> Optional[bytes]:
    return _recolor_png(data, (0, 0, 0))


def to_white_png(data: bytes) -> Optional[bytes]:
    return _recolor_png(data, (255, 255, 255))


def to_color_png(data: bytes) -> Optional[bytes]:
    """Keep original colors; only resize to max MAX_SIZE."""
    img = Image.open(BytesIO(data)).convert("RGBA")
    visible = sum(1 for p in img.getdata() if p[3] > 10)
    if visible < img.size[0] * img.size[1] * 0.005:
        return None
    img.thumbnail((MAX_SIZE, MAX_SIZE))
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _recolor_svg(data: bytes, hex_color: str) -> bytes:
    """Replace fills/strokes in SVG with given hex color."""
    svg = data.decode("utf-8", errors="replace")
    svg = re.sub(r'fill\s*=\s*"(?!none)[^"]*"',   f'fill="{hex_color}"',   svg)
    svg = re.sub(r'fill\s*:\s*(?!none)[^;}"]+',    f'fill:{hex_color}',     svg)
    svg = re.sub(r'stroke\s*=\s*"(?!none)[^"]*"',  f'stroke="{hex_color}"', svg)
    svg = re.sub(r'stop-color\s*:\s*[^;}"]+',       f'stop-color:{hex_color}', svg)
    return svg.encode("utf-8")


def to_black_svg(data: bytes) -> bytes:
    return _recolor_svg(data, "#000000")


def to_white_svg(data: bytes) -> bytes:
    return _recolor_svg(data, "#FFFFFF")


_api_error_shown = False


def fetch_logo(domain: str):
    """
    Call Brandfetch API, return (ext, data) where ext is 'svg' or 'png'.
    Prefers SVG, falls back to PNG.
    """
    global _api_error_shown
    url = f"https://api.brandfetch.io/v2/brands/{domain}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        if not _api_error_shown:
            _api_error_shown = True
            print(f"\n  [API error] Request failed: {e}")
        return None, None
    if r.status_code != 200:
        if not _api_error_shown:
            _api_error_shown = True
            msg = (r.text or "")[:300]
            print(f"\n  [API] Brandfetch returned HTTP {r.status_code}: {msg}")
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
        print("No API key found. Use one of:")
        print("  1. export BRANDFETCH_API_KEY='your_key'")
        print("  2. Put your key in logos/.brandfetch_key (one line, no quotes)")
        print("Get a free key at: brandfetch.com/developers")
        raise SystemExit(1)
    # Clean start
    import shutil
    if os.path.exists(OUT):
        shutil.rmtree(OUT)

    failed = []

    for category, brands in LOGOS.items():
        black_folder = os.path.join(OUT, "Black", category)
        white_folder = os.path.join(OUT, "White", category)
        color_folder = os.path.join(OUT, "Color", category)
        os.makedirs(black_folder, exist_ok=True)
        os.makedirs(white_folder, exist_ok=True)
        os.makedirs(color_folder, exist_ok=True)

        for name, domain in brands.items():
            print(f"  {name} ({domain})...", end=" ", flush=True)

            ext, data = fetch_logo(domain)

            if not data:
                print("✗ not found")
                failed.append(name)
                continue

            if ext == "svg":
                ext_name = "svg"
                black_data = to_black_svg(data)
                white_data = to_white_svg(data)
                color_data = data  # original colors
            else:
                ext_name = "png"
                black_data = to_black_png(data)
                white_data = to_white_png(data) if black_data else None
                color_data = to_color_png(data) if black_data else None
                if not black_data:
                    print("✗ empty after processing")
                    failed.append(name)
                    continue

            # Write Black, White, Color
            with open(os.path.join(black_folder, f"{name}.{ext_name}"), "wb") as f:
                f.write(black_data)
            if white_data:
                with open(os.path.join(white_folder, f"{name}.{ext_name}"), "wb") as f:
                    f.write(white_data)
            if color_data:
                with open(os.path.join(color_folder, f"{name}.{ext_name}"), "wb") as f:
                    f.write(color_data)
            print("✓ B+W+C" if white_data and color_data else "✓")

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
