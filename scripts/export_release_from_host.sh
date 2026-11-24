#!/usr/bin/env bash
# Read-only source collector. Does not install, start, stop, or modify services.
set -Eeuo pipefail
umask 077

SRC="/opt/gen9-t4-ocsd/gen9_t4_ocsd.py"
STAGE="/root/gen9-t4-ocsd-thermal-bridge-gtx1080ti-slot2"
DEST="${1:-/root/ocsd-release-candidate}"

if [[ $EUID -ne 0 ]]; then
  echo "ERROR: run as root on the Proxmox host" >&2
  exit 1
fi
if [[ ! -f "$SRC" ]]; then
  echo "ERROR: installed publisher not found: $SRC" >&2
  exit 1
fi
if [[ -e "$DEST" ]]; then
  echo "ERROR: destination already exists; choose a new empty path: $DEST" >&2
  exit 1
fi

mkdir -p "$DEST/src" "$DEST/metadata"
cp -p "$SRC" "$DEST/src/gen9_t4_ocsd.py"

# Do not collect registration helper yet: the captured helper still contains
# legacy workload-unit validation and must be redesigned before public release.
# Do not collect ownership.json, OCSD snapshots, /etc credentials, or runtime logs.

{
  echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python=$(python3 --version 2>&1)"
  echo "kernel=$(uname -r)"
  echo "proxmox=$(pveversion 2>/dev/null | head -n 1 || true)"
  echo "nvidia_smi=$(/usr/bin/nvidia-smi --version 2>/dev/null | head -n 1 || true)"
  echo "publisher_service=$(systemctl is-active gen9-t4-ocsd.service 2>/dev/null || true)"
} > "$DEST/metadata/runtime_versions.txt"

# Do not export the host's systemd unit or environment file. The public
# package supplies a separately reviewed manual-start-only example unit.

python3 "$(dirname "$0")/verify_candidate.py" "$DEST" | tee "$DEST/metadata/static_verification.txt"
(
  cd "$DEST"
  find src metadata -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)

ARCHIVE="${DEST}.tar.gz"
tar -C "$(dirname "$DEST")" -czf "$ARCHIVE" "$(basename "$DEST")"
echo
echo "CANDIDATE_DIR=$DEST"
echo "CANDIDATE_ARCHIVE=$ARCHIVE"
echo "No services, containers, VMs, workloads, OCSD memory, or iLO settings were changed."
echo "Review and sanitize the candidate before public upload."
