#!/usr/bin/env python3
"""Static verification for a host-exported OCSD publisher candidate."""
from __future__ import annotations

import ast
import hashlib
import re
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: verify_candidate.py <candidate-root>")
    root = Path(sys.argv[1]).resolve()
    source = root / "src" / "gen9_t4_ocsd.py"
    if not source.is_file():
        fail(f"missing {source}")

    raw = source.read_bytes()
    text = raw.decode("utf-8")
    try:
        tree = ast.parse(text, filename=str(source))
        compile(tree, str(source), "exec")
    except SyntaxError as exc:
        fail(f"Python syntax error: {exc}")

    calls: list[ast.Call] = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    forbidden_names = {
        "stop_workloads", "workloads_active", "validate_workload_units",
    }
    forbidden_tokens = (
        "systemctl", "pct exec", "qm stop", "docker exec",
        "OCSD_WORKLOAD_UNITS", "ocsd-gpu-runtime",
        "ocsd-gpu-workload-guard", "ocsd-gpu-workload-monitor",
    )
    for node in calls:
        if isinstance(node.func, ast.Name) and node.func.id in forbidden_names:
            fail(f"obsolete workload-management function call at line {node.lineno}")
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in {"kill", "terminate", "Popen", "run", "call", "check_call"}:
                fail(f"process-control or non-read-only subprocess API at line {node.lineno}")
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                if node.func.attr != "check_output":
                    fail(f"unexpected subprocess API {node.func.attr} at line {node.lineno}")
    for token in forbidden_tokens:
        if token in text:
            fail(f"workload-management token found: {token}")

    # A publisher process may install signal handlers for its own lifecycle. Those
    # handlers are not equivalent to sending signals to GPU workloads.
    if "GPU_PCI" not in text or "gpu_temperature" not in text:
        fail("GPU telemetry identity/function not found")
    if "RECORD_SIZE" not in text or "RECORD_OFFSET" not in text:
        fail("OCSD record definitions not found")
    if re.search(r"https?://192\.168\.", text):
        fail("private iLO address found in publisher source")
    if re.search(r"(?i)(password|token)\s*=\s*['\"][^'\"]+['\"]", text):
        fail("possible embedded secret found")

    digest = hashlib.sha256(raw).hexdigest()
    print("PYTHON_SYNTAX: PASS")
    print("WORKLOAD_CALL_SCAN: PASS (manual review still required)")
    print("GPU_AND_OCSD_SYMBOLS: PASS")
    print("SECRET_PATTERN_SCAN: PASS")
    print("SOURCE_SHA256:", digest)
    print("NOTE: this static checker is not a substitute for tests or code review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
