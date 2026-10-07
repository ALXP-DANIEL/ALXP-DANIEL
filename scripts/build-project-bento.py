#!/usr/bin/env python3
"""Rebuild the profile bento from the owning repositories' project.json files."""
import base64
import json
from html import escape
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ("PORTFOLIO", "main", "WEB", 0, 0, 420, 540),
    ("QR-PIXEL", "main", "TOOL", 440, 0, 670, 260),
    ("METEO", "master", "WEATHER", 440, 280, 380, 260),
    ("ANDROID_DEVICE_XIAOMI_PIANO", 'main', "DEVICE", 840, 280, 270, 260),
]

def fetch(url):
    with urlopen(url, timeout=30) as response:
        return response.read()

parts = []
records = []
for index, (repo, branch, category, x, y, width, height) in enumerate(SOURCES, 1):
    base = f"https://raw.githubusercontent.com/ALXP-DANIEL/{repo}/{branch}/"
    manifest = json.loads(fetch(base + "project.json"))
    src = manifest.get("profileImage") or manifest["thumbnail"]
    url = urljoin(base, src)
    title = escape(manifest["title"])
    caption = escape(manifest.get("profileSummary", ""))
    if len(manifest.get("profileSummary", "")) > 40:
        raise ValueError(f"{repo}: profileSummary exceeds 40 characters")
    image = "data:image/jpeg;base64," + base64.b64encode(fetch(url)).decode()
    title_size = min(28, (width - 52) / (max(len(manifest["title"]), 1) * 0.6))
    key = f"project-{index}"
    parts.append(f'''<svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><clipPath id="{key}-clip"><rect width="{width}" height="{height}" rx="24"/></clipPath><linearGradient id="{key}-shade" x1="0%" y1="0%" x2="0%" y2="100%"><stop stop-color="#000" stop-opacity=".1"/><stop offset=".5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></linearGradient></defs>
<g clip-path="url(#{key}-clip)"><image href="{image}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice"/><rect width="{width}" height="{height}" fill="url(#{key}-shade)"/></g>
<g fill="#fff" font-family="JetBrains Mono, ui-monospace, Menlo, Consolas, monospace"><text x="26" y="36" font-size="11" letter-spacing="2">{index:02d} / {category}</text><text x="26" y="{height-62}" font-size="{title_size:.1f}" font-weight="600" letter-spacing="-1">{title}</text><text x="26" y="{height-30}" font-size="12" fill="#ddd">{caption}</text></g><path d="M{width-48} 40l15-15m-15 0h15v15" stroke="#fff" stroke-width="2" fill="none"/></svg>''')
    records.append({"repository": repo, "branch": branch, "manifest": base + "project.json", "image": url})
    print(f"Fetched {repo}: {manifest['title']}")
svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1110" height="540" viewBox="0 0 1110 540"><title>Selected projects</title>' + "".join(parts) + '</svg>'
ET.fromstring(svg)
(ROOT / "assets/bento-projects-aligned.svg").write_text(svg)
(ROOT / "assets/project-cover-sources.json").write_text(json.dumps(records, indent=2) + "\n")
print("Built assets/bento-projects-aligned.svg")
