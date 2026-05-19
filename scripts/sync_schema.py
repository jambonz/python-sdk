#!/usr/bin/env python3
"""Sync JSON Schema files from the @jambonz/schema repo.

Downloads verb, component, and callback schemas and bundles them into this
package. Run this whenever the upstream schema changes.

Usage:
    # Download the pinned version (SCHEMA_VERSION below)
    python scripts/sync_schema.py

    # Download a specific version tag
    python scripts/sync_schema.py v0.1.1

    # Copy from a local directory instead
    python scripts/sync_schema.py --local /path/to/schema
"""

import json
import shutil
import sys
import urllib.request
from pathlib import Path

# ── Pin the schema version here ──────────────────────────────────────
SCHEMA_VERSION = "v0.3.8"
# ────────────────────────────────────────────────────────────────────

DEST = Path(__file__).resolve().parent.parent / "src" / "jambonz_sdk" / "schema"
GITHUB_RAW = "https://raw.githubusercontent.com/jambonz/schema/{version}"

SUBDIRS = ["verbs", "components", "callbacks"]


def download_file(url: str, dest: Path) -> None:
    urllib.request.urlretrieve(url, dest)


def sync_from_github(version: str) -> None:
    base_url = GITHUB_RAW.format(version=version)

    # Ensure destination exists
    DEST.mkdir(parents=True, exist_ok=True)

    # Download root schema
    root_schema = "jambonz-app.schema.json"
    print(f"Downloading {root_schema}...")
    download_file(f"{base_url}/{root_schema}", DEST / root_schema)

    # Download each subdirectory's index and files
    total = 0
    for subdir in SUBDIRS:
        subdir_path = DEST / subdir
        subdir_path.mkdir(exist_ok=True)

        # GitHub doesn't have a directory listing API on raw, so we fetch
        # the known file list from the root schema's $ref entries or use
        # the GitHub API
        api_url = (
            f"https://api.github.com/repos/jambonz/schema/contents/{subdir}"
            f"?ref={version}"
        )
        print(f"Fetching {subdir}/ file list...")
        req = urllib.request.Request(api_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            files = json.loads(resp.read())

        schema_files = [f["name"] for f in files if f["name"].endswith(".schema.json")]
        for fname in schema_files:
            download_file(f"{base_url}/{subdir}/{fname}", subdir_path / fname)
            total += 1

    print(f"Downloaded {total} schema files + root schema → {DEST} (version {version})")


def sync_from_local(src: Path) -> None:
    if not src.is_dir():
        print(f"Error: {src} is not a directory")
        sys.exit(1)

    # Clean and recreate destination
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)

    # Copy root schema
    root_schema = src / "jambonz-app.schema.json"
    if root_schema.exists():
        shutil.copy2(root_schema, DEST / "jambonz-app.schema.json")

    # Copy subdirectories
    total = 0
    for subdir in SUBDIRS:
        src_dir = src / subdir
        if src_dir.is_dir():
            dest_dir = DEST / subdir
            dest_dir.mkdir(exist_ok=True)
            for f in src_dir.glob("*.schema.json"):
                shutil.copy2(f, dest_dir / f.name)
                total += 1

    print(f"Copied {total} schema files + root schema from {src} → {DEST}")


def main() -> None:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--local":
            if len(sys.argv) < 3:
                print("Usage: python scripts/sync_schema.py --local /path/to/schema")
                sys.exit(1)
            sync_from_local(Path(sys.argv[2]))
        elif arg.startswith("v"):
            sync_from_github(arg)
        else:
            print(f"Unknown argument: {arg}")
            print("Usage:")
            print("  python scripts/sync_schema.py            # download pinned version")
            print("  python scripts/sync_schema.py v0.1.1     # download specific version")
            print("  python scripts/sync_schema.py --local /path/to/schema")
            sys.exit(1)
    else:
        sync_from_github(SCHEMA_VERSION)


if __name__ == "__main__":
    main()
