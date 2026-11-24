# NVIDIA GTX 1080 Ti → HPE DL380 Gen9 iLO 4 via OCSD

**Version:** `0.1.0-rc2`  
**Release status:** Experimental release candidate; not production-approved.

## Purpose

The host-side publisher reads the NVIDIA GPU temperature with `nvidia-smi`, discovers the HPE Option Card Sensor Data (OCSD) allocation through SMBIOS Type 229, validates the existing layout/native records, and updates only its dedicated third 160-byte record. iLO exposes the registered PCI temperature and remains responsible for its own stock thermal/fan policy.

The project does not set fan PWM, modify iLO firmware, or manage/stop containers, VMs, Docker workloads, or arbitrary processes.

## Observed results on the single qualification host

- Host: HPE ProLiant DL380 Gen9; iLO 4 firmware 2.77; System ROM P89 / BIOS 2.76.
- GPU: NVIDIA GeForce GTX 1080 Ti Founders Edition at PCI BDF `0000:0b:00.0`.
- Proxmox VE 9.2.2; kernel `7.0.2-6-pve`.
- The publisher read GPU temperature and updated its owned OCSD record.
- The observed OCSD allocation was 16 KiB at physical address `0x791f4000`; runtime discovery is used, and this address is not a portable constant.
- After one iLO management-processor reset, `22-PCI 2` was observed as `Enabled / OK`.
- Five paired samples showed GPU 48–49 °C and iLO PCI 2 63–64 °C. The observed delta was 14–16 °C, mean 15 °C.
- A separate 23-sample fan trace showed Fan 5 briefly reaching 82%, but GPU temperature remained near 48–49 °C. This does **not** establish GPU-caused fan response.

The 15 °C delta is a single-operating-point observation, not a calibrated offset. No offset correction is hardcoded in this release.

## RC2 source cleanup and provenance

The source was captured from the user's installed host publisher and then cleaned for publication. RC2 removes obsolete no-op workload-management stubs and environment configuration, replaces the old `publish_and_guard` wrapper with `publish_record`, removes unused offset/tolerance and workload-stop constants, and removes stale Tesla T4 runtime wording.

The host-collected baseline source SHA-256 was:

`a92e6f87ab6037e76d4ba0f0e850bf0e422e9600b7dfddda602e8b2ab0b5178f`

The cleaned RC2 publisher source SHA-256 is:

`f6990a761e01ea95e3db51cd42cd6b0db980efe6a1807ad5a2239c8737ada940`

RC2 is not byte-identical to the running host source. Packaging this release did not modify the active host service.

## Repository layout

- `src/`: cleaned publisher source.
- `tests/`: 26 hardware-independent tests for the exact RC2 source.
- `systemd/`: manual-start-only example unit.
- `config/`: configuration notes; no environment file is required.
- `docs/`: architecture, provenance, operations, validation, and release gates.
- `scripts/`: static verifier and host source exporter.
- `validation/`: captured measurement evidence.
- `LICENSE`, `legal/`: license and attribution notices.

## Run the release checks

No GPU, `/dev/mem`, IPMI, Redfish, containers, or VMs are accessed by the unit tests.

```bash
python3 -m py_compile src/gen9_t4_ocsd.py tests/test_publisher.py
python3 -m unittest discover -s tests -v
python3 scripts/verify_candidate.py .
systemd-analyze verify systemd/gen9-t4-ocsd.service
```

Or run `make check`.

## Deployment caution

There is no automatic installer. The example systemd unit is manual-start-only and has no workload hooks, `EnvironmentFile`, `ExecStop` helper, or `[Install]` section. Starting the publisher is a privileged, hardware-mutating operation: it writes to the third OCSD record and updates the OCSD device count. Read `docs/DEPLOYMENT_AND_OPERATIONS.md` before any deployment.

## Limitations

1. OCSD is not publicly specified. The `conroy-cheers/ocsd` reference says its reverse-engineering was based on a single ML350 Gen9 and was not tested on other hardware.
2. The Ocean Media Now reference project describes qualification for Tesla T4, iLO 4 v2.82, and high-performance fans. This test host uses a GTX 1080 Ti, iLO 4 v2.77, and standard fans; its results cannot be generalized.
3. The observed 15 °C difference has not been calibrated over a range of GPU temperatures.
4. The supplied fan trace does not prove GPU-to-fan causality.
5. Long-duration, reboot-persistence, watchdog-recovery, and hardware failure-injection tests remain outstanding.
6. The sample systemd unit passed syntax verification, but has not been independently installed and qualified on a separate host.

## Release decision

`0.1.0-rc2` is an experimental source/test/documentation candidate. It is not a stable release, a production approval, a universal Gen9 compatibility claim, or proof that fan speed is controlled by GPU temperature.
