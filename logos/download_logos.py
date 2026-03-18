#!/usr/bin/env python3
"""
Clean logo downloader using Brandfetch API.
Outputs BLACK, WHITE, and COLOR versions (max 1000px). B/W for light/dark backgrounds; color for brand-accurate use.
Get your key at: brandfetch.com/developers

Run with the project venv (so requests/Pillow are available):
  ../.venv/bin/python download_logos.py   (from logos/)
  or:  /path/to/RLJ2/.venv/bin/python /path/to/RLJ2/logos/download_logos.py
"""

import os
import re
import zipfile
from typing import Optional

try:
    import requests
    from PIL import Image
except ImportError as e:
    print("Missing dependency:", e)
    print("\nRun with the project venv (from RLJ2 folder):")
    print("  ./logos/run.sh")
    print("or:")
    print("  .venv/bin/python logos/download_logos.py")
    raise SystemExit(1)

from io import BytesIO

def _load_api_key():
    key = os.environ.get("BRANDFETCH_API_KEY", "").strip() or None
    if key:
        return key
    # Try key file next to this script (gitignored)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for key_file in [
        os.path.join(script_dir, ".brandfetch_key"),
        os.path.join(os.getcwd(), "logos", ".brandfetch_key"),
        os.path.join(os.getcwd(), ".brandfetch_key"),
    ]:
        if os.path.isfile(key_file):
            try:
                with open(key_file) as f:
                    key = (f.readline() or "").strip()
                    if key and key != "PASTE_YOUR_KEY_HERE":
                        return key
            except OSError:
                continue
    return "PASTE_YOUR_KEY_HERE"


API_KEY = _load_api_key()

# --- CTV / streaming / ad tech (commented out) ---
# LOGOS = {
#     "AdTech": {
#         "cineverse":    "cineverse.com",
#         "infillion":    "infillion.com",
#         "wurl":         "wurl.com",
#         "frequency":    "frequency.com",
#         "justwatch":    "justwatch.com",
#         "gumgum":       "gumgum.com",
#         "kargo":        "kargo.com",
#         "canvasspace":  "canvas.space",
#         "magnite":      "magnite.com",
#     },
#     "StreamingPlatforms": {
#         "sling":        "sling.com",
#         "primevideo":   "primevideo.com",
#         "philo":        "philo.com",
#         "lgchannels":   "lgchannels.com",
#         "anoki":        "anoki.ai",
#         "localnow":     "localnow.com",
#         "fubo":         "fubo.tv",
#         "roku":         "roku.com",
#         "plex":         "plex.tv",
#         "tubi":         "tubi.tv",
#         "tablo":        "tablotv.com",
#         "youtube":      "youtube.com",
#         "trc":          "trc.com",
#         "pluto":        "pluto.tv",
#         "directv":      "directv.com",
#         "tivo":         "tivo.com",
#         "freecast":     "freecast.com",
#     },
#     "TVPlatforms": {
#         "vizio":        "vizio.com",
#         "hp":           "hp.com",
#         "whale":        "whale.io",
#         "vidaa":        "vidaa.com",
#         "hisense":      "hisense.com",
#         "tcl":          "tcl.com",
#         "rakuten":      "rakuten.com",
#         "lg":           "lg.com",
#     }
# }

# --- Only the 13 that failed (alternate domains) — comment in to fill gaps without using quota on the rest ---
# LOGOS = {
#     "Entertainment": {
#         "artist_view":           "artistviewent.com",
#         "brain_power":           "brainpowerstudio.com",
#         "dlt_entertainment":     "dltentertainment.com",
#         "echelon":               "echelonstudios.us",
#         "epic_pictures":         "epic-pictures.com",
#         "foundation":            "foundation-distribution.com",
#         "gemelli":               "gemellifilm.com",
#         "giant_entertainment":   "giantpictures.com",
#         "green_apple":           "greenappleent.com",
#         "one_world_digital":     "oneworld.digital",
#         "questar":               "questarentertainment.com",
#         "vision_films":          "visionfilms.com",
#         "wonderphil":            "wonderphil.biz",
#     }
# }

# --- Only the 3 still missing (comment in to append without re-fetching all) ---
# LOGOS = {
#     "Entertainment": {
#         "gemelli":       "gemellifilm.com",
#         "green_apple":   "greenappleent.com",
#         "vision_films":  "visionfilms.com",
#     }
# }

LOGOS = {
    "Entertainment": {
        "airbud_entertainment":   "airbudentertainment.com",
        "alliance_media":        "alliancemedia.com",
        "artist_view":           "artistviewent.com",
        "bayview":               "bayview.com",
        "bmg":                   "bmg.com",
        "brain_power":           "brainpowerstudio.com",
        "cineverse":             "cineverse.com",
        "dlt_entertainment":     "dltentertainment.com",
        "echelon":               "echelonstudios.us",
        "electric_entertainment": "electricentertainment.com",
        "epic_pictures":         "epic-pictures.com",
        "filmhub":               "filmhub.com",
        "foundation":            "foundation-distribution.com",
        "gemelli":               "gemellifilm.com",
        "giant_entertainment":   "giantpictures.com",
        "green_apple":           "greenappleent.com",
        "imagicomm":             "imagicomm.com",
        "indie_rights":          "indierights.com",
        "lionsgate":             "lionsgate.com",
        "monarch":               "monarch.com",
        "new_films_international": "newfilmsinternational.com",
        "nicely":                "nicely.com",
        "one_world_digital":     "oneworld.digital",
        "questar":               "questarentertainment.com",
        "radial_entertainment":  "radialentertainment.com",
        "relativity_media":      "relativitymedia.com",
        "shoreline":             "shorelineentertainment.com",
        "spi":                   "spientertainment.com",
        "stingray":              "stingray.com",
        "studio_tf1":            "tf1.fr",
        "tastemade":             "tastemade.com",
        "tesera_entertainment":  "teseraentertainment.com",
        "tricoast":              "tricoast.com",
        "video_elephant":        "videoelephant.com",
        "vision_films":          "visionfilms.com",
        "wonderphil":            "wonderphil.biz",
    }
}

OUT = "CTV_Logos"
MAX_SIZE = 1000   # max width/height in px (800–1000 ideal for decks)
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


def _img_pixels_rgba(img: "Image.Image") -> list:
    """Pixel list (r,g,b,a) per pixel. Uses get_flattened_data on Pillow 10+ to avoid getdata deprecation."""
    if hasattr(img, "get_flattened_data"):
        flat = img.get_flattened_data()
        # get_flattened_data() returns a sequence of (r,g,b,a) per pixel, not flat bytes
        return list(flat)
    return list(img.getdata())


def _recolor_png(data: bytes, color: tuple) -> Optional[bytes]:
    """Convert PNG to solid (r,g,b) on transparent; max dimension MAX_SIZE.
    Detects light-background (black-on-white) vs dark-background (white-on-dark) and keeps
    the logo shape either way so dark backgrounds become transparent (avoids black boxes).
    """
    img = Image.open(BytesIO(data)).convert("RGBA")
    pixels = _img_pixels_rgba(img)
    r, g, b = color
    # Detect background: median luminance of opaque pixels
    opaque_lums = [
        int(0.299 * pr + 0.587 * pg + 0.114 * pb)
        for (pr, pg, pb, pa) in pixels
        if pa > 10
    ]
    light_bg = False
    if len(opaque_lums) >= 10:
        median_lum = sorted(opaque_lums)[len(opaque_lums) // 2]
        light_bg = median_lum > 140  # mostly white/light -> logo is dark

    new_pixels = []
    for p in pixels:
        pr, pg, pb, pa = p
        lum = int(0.299 * pr + 0.587 * pg + 0.114 * pb)
        if pa <= 10:
            new_pixels.append((0, 0, 0, 0))
            continue
        if light_bg:
            # Logo is dark pixels; keep dark, make light transparent
            if lum < 230:
                new_a = min(255, int(pa * (255 - lum) / 255))
                new_pixels.append((r, g, b, new_a))
            else:
                new_pixels.append((0, 0, 0, 0))
        else:
            # Logo is light pixels; keep light, make dark transparent
            if lum > 25:
                new_a = min(255, int(pa * (lum / 255)))
                new_pixels.append((r, g, b, new_a))
            else:
                new_pixels.append((0, 0, 0, 0))
    visible = sum(1 for p in new_pixels if p[3] > 10)
    if visible < len(pixels) * 0.005:
        return None
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
    visible = sum(1 for p in _img_pixels_rgba(img) if p[3] > 10)
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
            if r.status_code == 429:
                print("\n  → Quota exceeded. Brandfetch limits are per ACCOUNT, not per key — a new key on the same account won't help.")
                print("  → Wait for the daily reset (check brandfetch.com/developers) or create a key from a different Brandfetch account.")
                try:
                    d = r.json()
                    if "used" in d and "quota" in d:
                        print(f"  → Current: used {d['used']} / quota {d['quota']}")
                except Exception:
                    pass
                raise SystemExit(1)
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
    # No longer wiping OUT — each run adds/overwrites only the logos in LOGOS (keeps existing files)
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

            status_printed = False
            if ext == "svg":
                ext_name = "svg"
                black_data = to_black_svg(data)
                white_data = to_white_svg(data)
                color_data = data  # original colors
            else:
                ext_name = "png"
                black_data = to_black_png(data)
                white_data = to_white_png(data) if black_data else None
                color_data = to_color_png(data)
                if not black_data:
                    # Recolor produced nothing (e.g. odd luminance); keep color in all three so we don't lose the logo
                    if color_data:
                        black_data = white_data = color_data
                        status_printed = True
                    else:
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
            if not status_printed:
                print("✓ B+W+C" if (white_data and color_data) else "✓")
            else:
                print("✓ color only (B/W empty)")

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
