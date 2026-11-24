# Project status — 0.1.0-rc2

## Current state

The package has a cleaned publisher source, 26 hardware-independent unit tests, a manual-start-only example systemd unit, an MIT license file corresponding to the public Ocean Media Now repository, and updated operational/security/release documentation.

## Confirmed host evidence

- GPU: GTX 1080 Ti, BDF `0000:0b:00.0`.
- Host publisher was observed active after the final patch.
- OCSD third record was valid and updating; counter advanced from 2030 to 2051 during five paired samples.
- iLO `22-PCI 2` was observed Enabled/OK at 63–64 °C.
- GPU was 48–49 °C during those samples; mean observed iLO-GPU delta was 15 °C.
- Fan readings varied during the 23-sample run, with Fan 5 peaking at 82%, while GPU/PCI2 temperatures remained nearly stable.

## RC2 package checks

- Python compilation: PASS.
- New release-source tests: 26/26 PASS.
- Static candidate verifier: PASS.
- systemd unit syntax verifier: PASS.
- No live hardware or host service was accessed during the RC2 package tests.

## Not confirmed

- Causal GPU temperature to fan-speed response.
- Offset and sensor transfer calibration over multiple GPU temperature points.
- Long-duration stability, watchdog recovery, crash recovery, or reboot persistence.
- Qualification on other servers, iLO firmware versions, GPUs, fan types, or PCI placements.
- Actual installation of the RC2 source/unit on the user's live host.

## Release decision

`0.1.0-rc2` is an experimental source/test/documentation candidate. Do not label it stable, production-ready, HPE-supported, or universally compatible with Gen9.
