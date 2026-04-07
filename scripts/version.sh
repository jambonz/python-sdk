#!/bin/bash
# Usage: ./scripts/version.sh patch|minor|major
# Mimics `npm version` — bumps version in pyproject.toml, commits, and tags.

set -e

BUMP=${1:-patch}

if [[ "$BUMP" != "patch" && "$BUMP" != "minor" && "$BUMP" != "major" ]]; then
  echo "Usage: $0 patch|minor|major"
  exit 1
fi

# Read current version
CURRENT=$(python3 -c "
import re
with open('pyproject.toml') as f:
    m = re.search(r'^version\s*=\s*\"(.+?)\"', f.read(), re.M)
    print(m.group(1))
")

# Bump version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"
case "$BUMP" in
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch) PATCH=$((PATCH + 1)) ;;
esac
NEW="$MAJOR.$MINOR.$PATCH"

# Update pyproject.toml
sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml

# Commit and tag
git add pyproject.toml
git commit -m "v$NEW"
git tag "v$NEW"

echo "v$NEW"
echo "Run: git push && git push --tags"
