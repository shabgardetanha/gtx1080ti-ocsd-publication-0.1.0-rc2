"""Packaging guardrails for the example manual-start-only systemd unit."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "systemd" / "gen9-t4-ocsd.service"


class PackagingTests(unittest.TestCase):
    def test_service_is_notify_and_manual_start_only(self):
        text = UNIT.read_text()
        self.assertIn("Type=notify", text)
        self.assertIn("WatchdogSec=20", text)
        self.assertNotIn("[Install]", {line.strip() for line in text.splitlines()})

    def test_service_has_no_workload_or_environment_hooks(self):
        text = UNIT.read_text().lower()
        for forbidden in (
            "environmentfile=", "execstop=", "ocsd_workload_units",
            "ocsd-gpu-workload-guard", "ocsd-gpu-runtime",
            "pct", "qm stop", "docker", "systemctl stop",
        ):
            self.assertNotIn(forbidden, text)

    def test_project_has_license_and_third_party_notice(self):
        self.assertTrue((ROOT / "LICENSE").is_file())
        self.assertTrue((ROOT / "legal" / "THIRD_PARTY_NOTICES.md").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
