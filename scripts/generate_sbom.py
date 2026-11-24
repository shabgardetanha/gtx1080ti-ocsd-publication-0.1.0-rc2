#!/usr/bin/env python3
"""Generate a minimal SPDX 2.3 file manifest for this source tree.

The SBOM omits itself and SHA256SUMS to avoid recursive self-hashes. Those
artifacts are covered by the release archive checksum and package manifest.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SBOM_PATH = ROOT / "SBOM.spdx.json"
EXCLUDED = {"SBOM.spdx.json", "SHA256SUMS"}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

files = []
relationships = []
for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDED or "__pycache__" in path.parts:
        continue
    spdx_id = "SPDXRef-File-" + hashlib.sha256(rel.encode()).hexdigest()[:16]
    files.append({
        "fileName": "./" + rel,
        "SPDXID": spdx_id,
        "checksums": [{"algorithm": "SHA256", "checksumValue": sha256(path)}],
        "licenseConcluded": "MIT",
        "licenseInfoInFiles": ["MIT"],
        "copyrightText": "NOASSERTION",
    })
    relationships.append({
        "spdxElementId": "SPDXRef-Package-Publisher",
        "relationshipType": "CONTAINS",
        "relatedSpdxElement": spdx_id,
    })

source_hash = sha256(ROOT / "src" / "gen9_t4_ocsd.py")
doc = {
    "spdxVersion": "SPDX-2.3",
    "dataLicense": "CC0-1.0",
    "SPDXID": "SPDXRef-DOCUMENT",
    "name": "gtx1080ti-ocsd-publication-rc2",
    "documentNamespace": "https://github.com/oceanmedianow/gen9-t4-ocsd-thermal-bridge/releases/tag/v0.1.0-rc2/sbom/" + source_hash,
    "creationInfo": {
        "creators": ["Tool: scripts/generate_sbom.py"],
        "created": "2026-11-24T00:00:00Z",
        "comment": "Generated source-tree manifest. SBOM.spdx.json and SHA256SUMS are excluded from the file list to avoid recursive self-hashes; the release archive hash covers both. External runtime tools are not redistributed.",
    },
    "packages": [{
        "name": "gtx1080ti-ocsd-publisher",
        "SPDXID": "SPDXRef-Package-Publisher",
        "versionInfo": "0.1.0-rc2",
        "downloadLocation": "https://github.com/oceanmedianow/gen9-t4-ocsd-thermal-bridge",
        "filesAnalyzed": True,
        "licenseConcluded": "MIT",
        "licenseDeclared": "MIT",
        "copyrightText": "Copyright (c) 2026 Josh Murphy (Ocean Media Now)",
        "summary": "Experimental NVIDIA GPU temperature publisher for HPE Gen9 OCSD",
    }],
    "files": files,
    "relationships": relationships,
}
SBOM_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print(f"SBOM generated: {len(files)} files")
