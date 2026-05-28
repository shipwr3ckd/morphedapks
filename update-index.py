# Copyright (c) 2026 nvbangg (github.com/nvbangg)

import json
import re
import urllib.request
from pathlib import Path

REPO = "nvbangg/builder-for-morphe"
BASE_URL = f"https://github.com/{REPO}/blob/main/"
SCRIPT_DIR = Path(__file__).parent
README_PATH = SCRIPT_DIR / "temp" / "README.md"
INDEX_PATH = SCRIPT_DIR / "index.html"
CONTENT_START = "<!-- CONTENT_START -->"
CONTENT_END = "<!-- CONTENT_END -->"


def fix_relative_links(html):
    def replace_href(match):
        href = match.group(1)
        if href.startswith("#") or re.match(r"[a-z0-9+.\-]+:", href, re.IGNORECASE):
            return match.group(0)
        return f'href="{BASE_URL}{href}"'

    return re.sub(r'href="([^"]*)"', replace_href, html)


def main():
    readme_text = README_PATH.read_text(encoding="utf-8")

    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": readme_text, "mode": "gfm", "context": REPO}).encode(
            "utf-8"
        ),
        headers={"Content-Type": "application/json", "User-Agent": REPO},
    )

    with urllib.request.urlopen(req) as response:
        content_html = response.read().decode("utf-8")

    content_html = fix_relative_links(content_html)
    content_html = content_html.replace('id="user-content-', 'id="')

    index_html = INDEX_PATH.read_text(encoding="utf-8")
    updated_html = re.sub(
        rf"{re.escape(CONTENT_START)}[\s\S]*?{re.escape(CONTENT_END)}",
        f"{CONTENT_START}\n{content_html}\n{CONTENT_END}",
        index_html,
    )
    INDEX_PATH.write_text(updated_html, encoding="utf-8")
    print(f"Updated {INDEX_PATH}")


if __name__ == "__main__":
    main()
