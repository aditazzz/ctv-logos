#!/bin/bash
# Run the logo downloader with the project venv (so requests/Pillow work).
cd "$(dirname "$0")"
exec ../.venv/bin/python download_logos.py "$@"
