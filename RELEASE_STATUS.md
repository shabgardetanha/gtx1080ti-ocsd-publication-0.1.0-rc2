# Release status — 0.1.0-rc2

**Decision:** Experimental release candidate; production release blocked.

## Source provenance

- Host-exported source SHA-256: `a92e6f87ab6037e76d4ba0f0e850bf0e422e9600b7dfddda602e8b2ab0b5178f`
- Cleaned RC2 source SHA-256: `f6990a761e01ea95e3db51cd42cd6b0db980efe6a1807ad5a2239c8737ada940`
- Source cleanup and rationale: `docs/SOURCE_CHANGELOG.md`

## RC2 validation performed in the package build environment

- Python compilation: PASS.
- Unit tests against exact RC2 source: 26/26 PASS.
- Static candidate verification: PASS.
- systemd unit syntax verification: PASS using `systemd-analyze verify`.
- No hardware, `/dev/mem`, iLO, IPMI, GPU load, container, or VM operations were performed during these RC2 package tests.

## Hardware evidence carried forward from the host transcripts

- GPU telemetry and OCSD record updates observed.
- iLO `22-PCI 2` observed Enabled/OK after one iLO reset.
- Five paired readings observed a mean iLO-GPU delta of 15 °C.
- Twenty-three fan samples do not prove causal GPU-driven fan response.

## Not verified

- Causal fan control.
- Full offset/lag/threshold calibration.
- Long-duration reliability.
- Reboot persistence and automatic boot activation.
- Watchdog/crash recovery under hardware fault conditions.
- Qualification on any server other than the one described in the README.

No production-ready or general HPE Gen9 compatibility claim is authorized.
