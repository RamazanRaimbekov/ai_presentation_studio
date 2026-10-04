import os
import tempfile
from urllib.parse import urlparse

import requests


def search_pexels_image_url(query: str) -> str:
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key or not query:
        return ""
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": key},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=8,
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return ""
        src = photos[0].get("src", {})
        return src.get("large2x") or src.get("large") or src.get("medium") or ""
    except Exception:
        return ""


def _download_temp_image(url: str):
    if not url:
        return None
    try:
        img = requests.get(url, timeout=12)
        img.raise_for_status()
        suffix = ".jpg"
        path = urlparse(url).path.lower()
        if path.endswith(".png"):
            suffix = ".png"
        fh = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        fh.write(img.content)
        fh.close()
        return fh.name
    except Exception:
        return None


def fetch_pexels_image(query: str):
    return _download_temp_image(search_pexels_image_url(query))
