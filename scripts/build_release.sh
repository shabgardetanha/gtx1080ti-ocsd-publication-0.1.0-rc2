#!/usr/bin/env bash
# Reproducible source-package builder; does not deploy or touch hardware.
set -Eeuo pipefail
umask 022
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="0.1.0-rc2"
NAME="gtx1080ti-ocsd-publication-${VERSION}"
OUT="${1:-$(dirname "$ROOT")/dist}"

mkdir -p "$OUT"

cd "$ROOT"
echo "===== RUN PACKAGE CHECKS ====="
make check

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify systemd/gen9-t4-ocsd.service
  echo "SYSTEMD_UNIT_SYNTAX: PASS"
else
  echo "SYSTEMD_UNIT_SYNTAX: SKIPPED (systemd-analyze unavailable)"
fi

echo
echo "===== GENERATE SBOM ====="
python3 scripts/generate_sbom.py

find . -type d -name __pycache__ -prune -exec rm -rf {} +
rm -f SHA256SUMS
find . -type f -not -path './.git/*' -not -name SHA256SUMS -print0 \
  | sort -z | xargs -0 sha256sum > SHA256SUMS

STAGE="$OUT/$NAME"
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp -a "$ROOT/." "$STAGE/"
rm -rf "$STAGE/.git" "$STAGE"/dist "$STAGE"/__pycache__

TAR="$OUT/$NAME.tar.gz"
ZIP="$OUT/$NAME.zip"
rm -f "$TAR" "$ZIP"
tar --sort=name --owner=0 --group=0 --numeric-owner \
  -czf "$TAR" -C "$OUT" "$NAME"
python3 - "$STAGE" "$ZIP" <<'PY'
from pathlib import Path
import sys, zipfile
root = Path(sys.argv[1])
out = Path(sys.argv[2])
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        z.write(path, (Path(root.name) / path.relative_to(root)).as_posix())
PY

sha256sum "$TAR" "$ZIP" | tee "$OUT/$NAME.checksums.txt"
echo
echo "RELEASE_TAR=$TAR"
echo "RELEASE_ZIP=$ZIP"
echo "No system service, GPU, /dev/mem, iLO, container, VM, or workload was accessed or changed."
