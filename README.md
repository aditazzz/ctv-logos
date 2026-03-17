# CTV Logos

Script and assets for **CTV / streaming / ad tech** brand logos: fetched via [Brandfetch](https://brandfetch.com/developers), converted to **black on transparent** (SVG or PNG), and grouped by category.

## Contents

- **`logos/`** — Python downloader script and docs
  - `download_logos.py` — Fetches logos from Brandfetch API, converts to black-on-transparent
  - `requirements.txt` — `requests`, `Pillow`
  - `README.md` — Detailed usage and brand list
- **`CTV_Logos/`** — Output folder: `AdTech/`, `StreamingPlatforms/`, `TVPlatforms/` with 35 logos
- **`CTV_Logos.zip`** — Same contents as a zip (generated when you run the script)

## Quick start

1. Get a free API key at [brandfetch.com/developers](https://brandfetch.com/developers).
2. Set it when running the script:
   ```bash
   cd logos
   pip install -r requirements.txt
   export BRANDFETCH_API_KEY="your_key_here"
   python download_logos.py
   ```
   Or paste the key into `download_logos.py` where it says `PASTE_YOUR_KEY_HERE` (don’t commit that).
3. Output appears in `CTV_Logos/` and `CTV_Logos.zip` (one level up from `logos/`).

## Pushing to GitHub

- The repo is set up so the **API key is not committed** (use `BRANDFETCH_API_KEY` or a local paste).
- Code, README, and the **CTV_Logos** results are intended to be committed so others can use the script and see the logos.

After creating a new repository on GitHub:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git add .
git commit -m "Add CTV logo downloader and results"
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name.
