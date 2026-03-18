#!/usr/bin/env bash
# Prepare delivery artifacts from this repo.
#
# Produces:
#   delivery/skeleton/     — minimal setup repo (pre-interview)
#   delivery/exercise.zip  — exercise materials (during interview)
#
# Skeleton source files live alongside the real files with _PREP / _stub
# suffixes (e.g. README_PREP.md, server_stub.py, test_setup.py, about.md).
# The exercise README is the repo's README.md.
#
# Usage:
#   bash scripts/prepare_delivery.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DELIVERY_DIR="$PROJECT_DIR/delivery"
WHEEL="sayata_simulators-1.0.0-cp312-none-any.whl"

echo "=== Preparing delivery artifacts ==="
echo ""

# --- Step 1: Build simulator wheel if not present ---
if [ ! -f "$PROJECT_DIR/packages/$WHEEL" ]; then
    echo "Building simulator wheel..."
    bash "$SCRIPT_DIR/build_simulators.sh"
    echo ""
fi

# --- Clean previous output ---
rm -rf "$DELIVERY_DIR"
mkdir -p "$DELIVERY_DIR/skeleton" "$DELIVERY_DIR/_exercise_staging"

# =====================================================================
# D1: Skeleton repo (pre-interview)
# =====================================================================
echo "--- Building skeleton repo ---"

SKEL="$DELIVERY_DIR/skeleton"

# Copy skeleton source files (renamed to their delivery names)
cp "$PROJECT_DIR/README_PREP.md" "$SKEL/README.md"
mkdir -p "$SKEL/docs"
cp "$PROJECT_DIR/docs/about.md" "$SKEL/docs/about.md"

mkdir -p "$SKEL/src/sayata"
touch "$SKEL/src/sayata/__init__.py"
cp "$PROJECT_DIR/src/sayata/server_stub.py" "$SKEL/src/sayata/server.py"

mkdir -p "$SKEL/tests"
cp "$PROJECT_DIR/tests/test_setup.py" "$SKEL/tests/test_setup.py"

# pyproject.toml (skeleton: no simulator dependency)
cat > "$SKEL/pyproject.toml" <<'SKEL_TOML'
[project]
name = "sayata-interview"
version = "0.1.0"
description = "Sayata quoting platform — interview exercise"
requires-python = "==3.12.*"
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "httpx>=0.28",
    "pydantic>=2.10",
    "pytest>=8.3",
    "requests>=2.32",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sayata"]

[tool.pytest.ini_options]
testpaths = ["tests"]
SKEL_TOML

# .gitignore
cat > "$SKEL/.gitignore" <<'SKEL_IGNORE'
__pycache__/
*.pyc
.venv/
.pytest_cache/
*.egg-info/
packages/
delivery/
SKEL_IGNORE

# Clean any stray __pycache__ from skeleton
find "$SKEL" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$SKEL" -name "*.pyc" -delete 2>/dev/null || true

echo "  Created: delivery/skeleton/"

# =====================================================================
# D2: Exercise zip (during interview)
# =====================================================================
echo "--- Building exercise.zip ---"

STAGE="$DELIVERY_DIR/_exercise_staging"

# README (full instructions — replaces skeleton README)
cp "$PROJECT_DIR/README.md" "$STAGE/README.md"
# Fix ticket links for exercise layout (tickets/ticket-N.md, not tickets/candidate/...)
sed -i '' 's|tickets/candidate/ticket-|tickets/ticket-|g' "$STAGE/README.md"

# pyproject.toml (adds sayata-simulators dependency + find-links)
cat > "$STAGE/pyproject.toml" <<'EXERCISE_TOML'
[project]
name = "sayata-interview"
version = "0.1.0"
description = "Sayata quoting platform — interview exercise"
requires-python = "==3.12.*"
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "httpx>=0.28",
    "pydantic>=2.10",
    "pytest>=8.3",
    "requests>=2.32",
    "sayata-simulators==1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sayata"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.uv]
find-links = ["packages"]
EXERCISE_TOML

# Source code (candidate's server + carriers — NO simulators)
mkdir -p "$STAGE/src/sayata/carriers"
cp "$PROJECT_DIR/src/sayata/__init__.py" "$STAGE/src/sayata/__init__.py"
cp "$PROJECT_DIR/src/sayata/server.py" "$STAGE/src/sayata/server.py"
cp "$PROJECT_DIR/src/sayata/models.py" "$STAGE/src/sayata/models.py"
cp "$PROJECT_DIR/src/sayata/carriers/__init__.py" "$STAGE/src/sayata/carriers/__init__.py"
cp "$PROJECT_DIR/src/sayata/carriers/base.py" "$STAGE/src/sayata/carriers/base.py"
cp "$PROJECT_DIR/src/sayata/carriers/carrier_a.py" "$STAGE/src/sayata/carriers/carrier_a.py"
cp "$PROJECT_DIR/src/sayata/carriers/carrier_b.py" "$STAGE/src/sayata/carriers/carrier_b.py"

# Simulator wheel (bytecode only)
mkdir -p "$STAGE/packages"
cp "$PROJECT_DIR/packages/$WHEEL" "$STAGE/packages/$WHEEL"

# Documentation (split docs — NO domain.md)
mkdir -p "$STAGE/docs"
for doc in architecture.md business-rules.md glossary.md frontend-guidelines.md; do
    cp "$PROJECT_DIR/docs/$doc" "$STAGE/docs/$doc"
done

# Candidate tickets only (NO interviewer tickets)
mkdir -p "$STAGE/tickets"
for ticket in ticket-1.md ticket-2.md ticket-3.md ticket-4.md; do
    cp "$PROJECT_DIR/tickets/candidate/$ticket" "$STAGE/tickets/$ticket"
done

# Scripts
mkdir -p "$STAGE/scripts"
cp "$PROJECT_DIR/scripts/start.py" "$STAGE/scripts/start.py"
cp "$PROJECT_DIR/scripts/verify.py" "$STAGE/scripts/verify.py"

# setup.sh
cp "$PROJECT_DIR/setup.sh" "$STAGE/setup.sh"
chmod +x "$STAGE/setup.sh"

# Tests (stub only — NO test_verification.py)
mkdir -p "$STAGE/tests"
cp "$PROJECT_DIR/tests/__init__.py" "$STAGE/tests/__init__.py"
cp "$PROJECT_DIR/tests/conftest.py" "$STAGE/tests/conftest.py"
cp "$PROJECT_DIR/tests/test_stub.py" "$STAGE/tests/test_stub.py"

# Build the zip
cd "$STAGE"
zip -q -r "$DELIVERY_DIR/exercise.zip" .

# Cleanup staging
rm -rf "$STAGE"

echo "  Created: delivery/exercise.zip"

# =====================================================================
# Summary
# =====================================================================
echo ""
echo "=== Delivery artifacts ready ==="
echo ""
echo "  delivery/skeleton/     → Push to candidate-facing repo"
echo "  delivery/exercise.zip  → Share during interview"
echo ""
echo "Verification:"
echo "  1. cd to a fresh dir, copy skeleton/, run: uv sync && uv run pytest -v"
echo "  2. Extract exercise.zip into it, run: bash setup.sh"
echo "  3. Start servers: uv run python scripts/start.py"
echo "  4. Verify: uv run python scripts/verify.py"
