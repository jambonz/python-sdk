#!/usr/bin/env bash
set -euo pipefail

# Publish jambonz-sdk to PyPI
#
# Prerequisites:
#   pip install build twine
#
# Usage:
#   # Dry run — build only, don't upload
#   ./scripts/publish.sh --dry-run
#
#   # Publish to TestPyPI first (recommended for first time)
#   ./scripts/publish.sh --test
#
#   # Publish to real PyPI
#   ./scripts/publish.sh
#
# Authentication:
#   Set TWINE_USERNAME and TWINE_PASSWORD env vars, or use a ~/.pypirc file,
#   or use a PyPI API token:
#     TWINE_USERNAME=__token__
#     TWINE_PASSWORD=pypi-xxxxx

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# Parse args
DRY_RUN=false
TEST_PYPI=false
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --test)    TEST_PYPI=true ;;
    esac
done

# Check tools
for cmd in python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: $cmd is required"
        exit 1
    fi
done

# Use venv if available
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python3"
fi

# Ensure build and twine are installed
$PYTHON -m pip install --quiet build twine

# Show version
VERSION=$($PYTHON -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
echo "Building jambonz-sdk v${VERSION}"

# Clean previous builds
rm -rf dist/ build/

# Build
echo "Building sdist and wheel..."
$PYTHON -m build
echo ""
echo "Built artifacts:"
ls -la dist/

# Verify
echo ""
echo "Checking package..."
$PYTHON -m twine check dist/*

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "Dry run complete. To publish, run without --dry-run"
    exit 0
fi

# Upload
if [ "$TEST_PYPI" = true ]; then
    echo ""
    echo "Uploading to TestPyPI..."
    $PYTHON -m twine upload --repository testpypi dist/*
    echo ""
    echo "Published to TestPyPI!"
    echo "Install with: pip install -i https://test.pypi.org/simple/ jambonz-sdk"
else
    echo ""
    echo "Uploading to PyPI..."
    $PYTHON -m twine upload dist/*
    echo ""
    echo "Published to PyPI!"
    echo "Install with: pip install jambonz-sdk"
fi
