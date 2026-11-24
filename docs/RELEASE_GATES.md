# Release gates

## RC2 package completeness

- [x] Exact host source was exported before publication cleanup.
- [x] Baseline and cleaned source hashes are recorded.
- [x] Dead workload-management stubs/configuration removed from RC2 source.
- [x] No process, container, Docker, or VM lifecycle code is present in RC2 publisher.
- [x] 26 hardware-independent unit tests were written for the exact RC2 source and passed.
- [x] Python compilation passed.
- [x] Static candidate verification passed.
- [x] Example systemd unit passed `systemd-analyze verify` in the package build environment.
- [x] MIT license and third-party attribution notes included.
- [x] No Redfish test client with disabled TLS verification is included in runtime or tooling.
- [x] Manual-start-only unit example included without stale `EnvironmentFile` or workload hooks.

## Before public source release

- [ ] Project maintainer confirms authority to publish the host-collected source and the included MIT notice.
- [ ] Maintainer reviews the final source diff and package contents.
- [ ] A clean clone/checkout of the archive runs `make check` successfully.
- [ ] Repository metadata and release tag are created by the maintainer.
- [ ] No private snapshots, ownership JSON, tokens, credentials, boot IDs, or local host service files are included.

## Before claiming fan-control validation

- [ ] Obtain paired GPU/OCSD/iLO measurements at multiple naturally occurring GPU temperatures.
- [ ] Quantify offset, lag, repeatability, quantization, clamping, and error bounds.
- [ ] Record CPU, inlet, chipset, PCI Zone, and all six fan readings concurrently.
- [ ] Demonstrate that fan response follows PCI 2 temperature while controlling for other thermal inputs and expected iLO policy lag.
- [ ] Use only low-risk, bounded conditions; do not run a high-temperature stress test merely to force fan response.

## Before production readiness

- [ ] Long-duration soak test.
- [ ] Fault-injection test for NVIDIA telemetry loss and iLO sensor loss.
- [ ] Crash/restart and ownership-state recovery tests on hardware or a faithful disposable test harness.
- [ ] Planned host reboot persistence test in a maintenance window.
- [ ] Validate behavior when iLO resets independently.
- [ ] Verify no native OCSD record/header corruption.
- [ ] Review fail-high/restore path, systemd restart policy, and watchdog behavior.
- [ ] Validate rollback on a recoverable system.

## Decision

Current status: **Experimental RC2. Package checks pass. Hardware fan-control causality and production reliability remain unverified.**
