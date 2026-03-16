#!/usr/bin/env bash
# Build the sayata_simulators wheel with .pyc-only (no source).
#
# Compiles all simulator .py files to .pyc bytecode, packages them
# as a wheel, and outputs to packages/. Candidates receive only the
# wheel — they cannot read simulator source.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$(mktemp -d)"
PKG_NAME="sayata_simulators"
VERSION="1.0.0"
SIM_DIR="$PROJECT_DIR/src/sayata/simulators"

echo "Building $PKG_NAME-$VERSION wheel..."
echo "  Source:    $SIM_DIR"
echo "  Build dir: $BUILD_DIR"

# Create package directory
PKG_DIR="$BUILD_DIR/$PKG_NAME"
mkdir -p "$PKG_DIR"

# Copy simulator source files
for f in __init__.py carrier_a_sim.py carrier_b_sim.py carrier_c_sim.py carrier_d_sim.py; do
    cp "$SIM_DIR/$f" "$PKG_DIR/$f"
done

# Compile to .pyc (legacy locations: .pyc next to .py)
python3 -m compileall -b -q "$PKG_DIR"

# Remove .py source — keep only .pyc
find "$PKG_DIR" -name "*.py" -delete
# Remove __pycache__ if created
find "$PKG_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create dist-info directory
DIST_INFO="$BUILD_DIR/$PKG_NAME-$VERSION.dist-info"
mkdir -p "$DIST_INFO"

cat > "$DIST_INFO/METADATA" <<EOF
Metadata-Version: 2.1
Name: $PKG_NAME
Version: $VERSION
Summary: Carrier simulators for Sayata interview exercise
Requires-Python: >=3.12
Requires-Dist: fastapi>=0.115
Requires-Dist: uvicorn>=0.34
EOF

cat > "$DIST_INFO/WHEEL" <<EOF
Wheel-Version: 1.0
Generator: build_simulators.sh
Root-Is-Purelib: true
Tag: py3-none-any
EOF

cat > "$DIST_INFO/top_level.txt" <<EOF
sayata_simulators
EOF

# Generate RECORD with sha256 hashes
cd "$BUILD_DIR"
python3 -c "
import hashlib, base64, os

records = []
for root, dirs, files in os.walk('.'):
    for f in sorted(files):
        path = os.path.join(root, f)[2:]  # strip ./
        if path == '$PKG_NAME-$VERSION.dist-info/RECORD':
            continue
        with open(path, 'rb') as fh:
            digest = hashlib.sha256(fh.read()).digest()
        h = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
        size = os.path.getsize(path)
        records.append(f'{path},sha256={h},{size}')
records.append('$PKG_NAME-$VERSION.dist-info/RECORD,,')
print('\n'.join(records))
" > "$DIST_INFO/RECORD"

# Package as wheel (.whl = zip with specific naming)
WHEEL_FILE="$PKG_NAME-$VERSION-py3-none-any.whl"
mkdir -p "$PROJECT_DIR/packages"
zip -q -r "$PROJECT_DIR/packages/$WHEEL_FILE" .

echo "  Output:   packages/$WHEEL_FILE"

# Cleanup
rm -rf "$BUILD_DIR"

echo "Done!"
