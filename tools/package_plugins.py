#!/usr/bin/env python3
"""Build one installable plugin ZIP from its reviewed source files."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SLUGS = ("resets-today", "runs-since-pb")
PACKAGE_FILES = (
    "plugin.toml",
    "main.py",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", choices=PLUGIN_SLUGS)
    parser.add_argument("--tag", default="", help="Require this release tag")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    arguments = parser.parse_args()

    slug = arguments.plugin
    if arguments.tag:
        match = re.fullmatch(r"(resets-today|runs-since-pb)-v(.+)", arguments.tag)
        if match is None:
            parser.error(f"unsupported release tag: {arguments.tag!r}")
        tag_slug, tag_version = match.groups()
        if slug is not None and slug != tag_slug:
            parser.error("--plugin does not match --tag")
        slug = tag_slug
    else:
        tag_version = ""

    if slug is None:
        parser.error("--plugin or --tag is required")

    plugin_root = ROOT / "plugins" / slug
    manifest = tomllib.loads(
        (plugin_root / "plugin.toml").read_text(encoding="utf-8")
    )
    version = str(manifest["version"])
    if tag_version and tag_version != version:
        parser.error(
            f"tag version {tag_version!r} does not match manifest {version!r}"
        )

    arguments.output.mkdir(parents=True, exist_ok=True)
    archive = arguments.output / f"greensplit-{slug}-{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name in PACKAGE_FILES:
            source = plugin_root / name
            if not source.is_file():
                parser.error(f"package file is missing: {source}")
            package.write(source, name)

    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
