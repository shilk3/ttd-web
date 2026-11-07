#!/usr/bin/env bash
# Builds OpenTTD for the browser (WebAssembly) with a phone-friendly page,
# and puts the result in ./docs (ready to host as static files).
#
# Needs: git, cmake, ninja, python3, curl, unzip, a C++ compiler (for host tools).
# Emscripten is installed automatically into $WORK/emsdk.
set -euo pipefail

OPENTTD_VERSION="${OPENTTD_VERSION:-15.3}"
OPENGFX_VERSION="${OPENGFX_VERSION:-8.0}"
OPENSFX_VERSION="${OPENSFX_VERSION:-1.0.3}"
EMSDK_VERSION="3.1.57"   # the version OpenTTD's own Dockerfile pins

REPO="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HOME/build}"
OUT="$REPO/docs"
JOBS="$(nproc)"
mkdir -p "$WORK"

# --- Emscripten -------------------------------------------------------------
if [ ! -d "$WORK/emsdk" ]; then
  git clone --depth 1 https://github.com/emscripten-core/emsdk.git "$WORK/emsdk"
fi
(cd "$WORK/emsdk" && ./emsdk install "$EMSDK_VERSION" && ./emsdk activate "$EMSDK_VERSION")
# shellcheck disable=SC1091
source "$WORK/emsdk/emsdk_env.sh" >/dev/null

# --- OpenTTD source ---------------------------------------------------------
SRC="$WORK/OpenTTD"
if [ ! -d "$SRC" ]; then
  git clone --depth 1 -b "$OPENTTD_VERSION" https://github.com/OpenTTD/OpenTTD.git "$SRC"
fi
cd "$SRC"
for p in "$REPO"/patches/*.patch; do
  git apply --check "$p" 2>/dev/null && git apply "$p" || echo "patch already applied: $(basename "$p")"
done

# Our phone page replaces the stock one.
cp "$REPO/web/shell.html" os/emscripten/shell.html
# Let the page write first-run defaults once saved files are loaded.
python3 - os/emscripten/pre.js <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "        Module.removeRunDependency('syncfs');"
new = "        if (Module.onFsReady) Module.onFsReady();\n" + old
if "onFsReady" not in s:
    assert old in s, "pre.js layout changed"
    open(p, "w").write(s.replace(old, new, 1))
EOF

# The liblzma port used by OpenTTD.
cp os/emscripten/ports/liblzma.py "$EMSDK/upstream/emscripten/tools/ports/contrib/liblzma.py"

# Some build sandboxes cannot download GitHub release archives (only git works).
# Set PORTS_VIA_GIT=1 to fetch the port sources with git and serve them locally.
if [ "${PORTS_VIA_GIT:-0}" = "1" ]; then
  M="$WORK/mirror"; mkdir -p "$M"; cd "$M"
  [ -f release-2.28.4.zip ] || { git clone -q --depth 1 -b release-2.28.4 https://github.com/libsdl-org/SDL.git SDL-release-2.28.4 && rm -rf SDL-release-2.28.4/.git && zip -qr release-2.28.4.zip SDL-release-2.28.4; }
  [ -f v1.2.13.tar.gz ] || { git clone -q --depth 1 -b v1.2.13 https://github.com/madler/zlib.git zlib-1.2.13 && rm -rf zlib-1.2.13/.git && tar czf v1.2.13.tar.gz zlib-1.2.13; }
  [ -f xz-5.4.6.tar.xz ] || { git clone -q --depth 1 -b v5.4.6 https://github.com/tukaani-project/xz.git xz-5.4.6 && rm -rf xz-5.4.6/.git && tar cJf xz-5.4.6.tar.xz xz-5.4.6; }
  P="$EMSDK/upstream/emscripten/tools/ports"
  sed -i "s#https://github.com/libsdl-org/SDL/archive/{TAG}.zip#http://127.0.0.1:8765/{TAG}.zip#; s#sha512hash=HASH#sha512hash=None#" "$P/sdl2.py"
  sed -i "s#https://github.com/madler/zlib/archive/refs/tags/v{VERSION}.tar.gz#http://127.0.0.1:8765/v{VERSION}.tar.gz#; s#sha512hash=HASH#sha512hash=None#" "$P/zlib.py"
  sed -i "s#https://github.com/tukaani-project/xz/releases/download/v{VERSION}/xz-{VERSION}.tar.xz#http://127.0.0.1:8765/xz-{VERSION}.tar.xz#; s#sha512hash=HASH#sha512hash=None#" "$P/contrib/liblzma.py"
  python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &
  SERVER_PID=$!; trap 'kill $SERVER_PID 2>/dev/null || true' EXIT
  sleep 1
  embuilder build sdl2 zlib libpng contrib.liblzma
  cd "$SRC"
fi

# --- Host tools (strgen etc.) ---------------------------------------------
mkdir -p build-host
(cd build-host && cmake .. -G Ninja -DOPTION_TOOLS_ONLY=ON >/dev/null && ninja tools)

# --- Free base sets (graphics + sounds) -----------------------------------
mkdir -p build/baseset
cd build/baseset
fetch_set() { # name version
  [ -f "$1-$2.tar" ] && return
  curl -fsSLO "https://cdn.openttd.org/$1-releases/$2/$1-$2-all.zip"
  unzip -qo "$1-$2-all.zip" && rm "$1-$2-all.zip"
}
fetch_set opengfx "$OPENGFX_VERSION"
fetch_set opensfx "$OPENSFX_VERSION"
cd "$SRC/build"

# --- The game ---------------------------------------------------------------
emcmake cmake .. -G Ninja -DHOST_BINARY_DIR=../build-host -DCMAKE_BUILD_TYPE=Release \
  -DOPTION_USE_ASSERTS=OFF -DCMAKE_MODULE_PATH="$SRC/os/emscripten/cmake"
# The page template is not a tracked dependency; force a relink so it is picked up.
rm -f openttd.html
ninja -j"$JOBS"

# --- Collect the site -------------------------------------------------------
rm -rf "$OUT"; mkdir -p "$OUT"
cp openttd.html "$OUT/index.html"
cp openttd.js openttd.wasm openttd.data "$OUT/"
cp "$REPO"/web/{manifest.webmanifest,icon-180.png,icon-192.png,icon-512.png} "$OUT/"
BUILD_ID="$(date +%Y%m%d%H%M%S)"
sed "s/BUILD_ID/$OPENTTD_VERSION-$BUILD_ID/" "$REPO/web/sw.js" > "$OUT/sw.js"
touch "$OUT/.nojekyll"
echo "Done. Site is in $OUT"
ls -la "$OUT"
