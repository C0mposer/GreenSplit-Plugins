#!/usr/bin/env python3
"""Refresh catalog download totals from declared GitHub release assets."""

from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


CATALOG = Path(__file__).resolve().parents[1] / "plugins.json"


def github_release(repository: str, tag: str, token: str) -> dict[str, object]:
    url = f"https://api.github.com/repos/{repository}/releases/tags/{tag}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "GreenSplit-Plugin-Registry",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 2

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    changed = False
    for plugin in catalog.get("plugins", []):
        source = plugin.get("github_release")
        if not isinstance(source, dict):
            continue
        repository = str(source.get("repository", "")).strip()
        tag = str(source.get("tag", "")).strip()
        asset_pattern = str(source.get("asset", "*.zip")).strip()
        if not repository or not tag:
            continue
        try:
            release = github_release(repository, tag, token)
        except (urllib.error.URLError, json.JSONDecodeError) as error:
            print(f"Could not update {plugin.get('id', '<unknown>')}: {error}", file=sys.stderr)
            return 1
        downloads = sum(
            int(asset.get("download_count", 0))
            for asset in release.get("assets", [])
            if fnmatch.fnmatch(str(asset.get("name", "")), asset_pattern)
        )
        if plugin.get("downloads") != downloads:
            plugin["downloads"] = downloads
            changed = True

    if changed:
        CATALOG.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
