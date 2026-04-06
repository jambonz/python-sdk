#!/usr/bin/env python3
"""Sync specs.json from the @jambonz/verb-specifications repo.

Downloads specs.json for a specific version tag and bundles it into this
package. Run this whenever the upstream spec changes.

Usage:
    # Download the pinned version (SPECS_VERSION below)
    python scripts/sync_specs.py

    # Download a specific version
    python scripts/sync_specs.py v0.1.10

    # Copy from a local file instead
    python scripts/sync_specs.py --local /path/to/specs.json
"""

import json
import shutil
import sys
import urllib.request
from pathlib import Path

# ── Pin the specs version here ──────────────────────────────────────
SPECS_VERSION = "v0.1.11"
# ────────────────────────────────────────────────────────────────────

DEST = Path(__file__).resolve().parent.parent / "src" / "jambonz_sdk" / "specs.json"
GITHUB_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/jambonz/verb-specifications/{version}/specs.json"
)


def sync_from_github(version: str) -> None:
    url = GITHUB_URL_TEMPLATE.format(version=version)
    print(f"Downloading specs.json {version} from {url}")
    urllib.request.urlretrieve(url, DEST)

    # Verify it's valid JSON
    with DEST.open() as f:
        specs = json.load(f)
    verb_count = len(specs)
    print(f"Downloaded → {DEST} ({verb_count} entries, version {version})")


def sync_from_file(src: Path) -> None:
    if not src.is_file():
        print(f"Error: {src} not found")
        sys.exit(1)
    shutil.copy2(src, DEST)
    with DEST.open() as f:
        specs = json.load(f)
    print(f"Copied {src} → {DEST} ({len(specs)} entries)")


def main() -> None:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--local":
            if len(sys.argv) < 3:
                print("Usage: python scripts/sync_specs.py --local /path/to/specs.json")
                sys.exit(1)
            sync_from_file(Path(sys.argv[2]))
        elif arg.startswith("v"):
            sync_from_github(arg)
        else:
            print(f"Unknown argument: {arg}")
            print("Usage:")
            print("  python scripts/sync_specs.py            # download pinned version")
            print("  python scripts/sync_specs.py v0.1.10    # download specific version")
            print("  python scripts/sync_specs.py --local /path/to/specs.json")
            sys.exit(1)
    else:
        sync_from_github(SPECS_VERSION)


if __name__ == "__main__":
    main()
