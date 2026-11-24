# Changelog

## 0.1.0-rc2 — publication cleanup

- Added hardware-independent unit tests for the exact release source.
- Removed obsolete workload-management stubs, variables, and no-op wrapper.
- Simplified record publication to a focused `publish_record` operation.
- Removed unused provisional offset/tolerance settings and workload-stop
  threshold.
- Replaced stale T4 runtime wording with GPU-generic wording.
- Added a manual-start-only systemd unit example without EnvironmentFile or
  workload hooks.
- Added license, third-party notices, security/contribution guidance, CI, and
  source provenance documentation.
- Preserved the 85 C telemetry-failure value and original OCSD record
  ownership/restoration checks.
- Fan-control causality and hardware release remain unverified.

## 0.1.0-rc1 — initial evidence package

- Captured host source and recorded OCSD/iLO/fan observations.
- Documented the PCI sensor registration and five paired readings.
