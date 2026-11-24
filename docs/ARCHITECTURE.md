# Architecture

## Data path

```text
NVIDIA GTX 1080 Ti
   │
   ▼
NVIDIA driver / NVML via nvidia-smi
   │  PCI BDF + temperature
   ▼
Host-side Python publisher
   │  SMBIOS Type 229 discovery
   │  Validate OCSD header + native records
   │  Update only dedicated third 160-byte record
   ▼
HPE OCSD allocation in physical memory
   │
   ▼
iLO 4 PCI sensor registration
   │
   ▼
Stock HPE thermal policy
   │
   ▼
Six standard system fans
```

## Component responsibilities

- **Telemetry:** `nvidia-smi` returns the GPU BDF and temperature.
- **Discovery:** SMBIOS Type 229 is scanned for a unique `$OCS` marker and a 16 KiB allocation.
- **Validation:** the 64-byte OCSD header, allocation size, record size, device count, checksum, and two observed native record headers are checked.
- **Publisher:** the process owns and updates the third 160-byte record. It checks write readback and confirms the active header has not changed.
- **iLO:** discovers and exposes the PCI sensor. In the qualification host, `22-PCI 2` was observed as Enabled/OK after one management-processor reset.
- **Fan control:** remains the stock HPE/iLO thermal policy. The publisher does not write PWM values or patch iLO firmware.

## Explicitly excluded functionality

This project does not enumerate, monitor, signal, stop, restart, or otherwise manage containers, VMs, Docker workloads, inference processes, or arbitrary host processes. No workload service, container ID, VM ID, or process ID is configured in this publisher.

The RC2 source has no workload-management helpers, process enumeration API, process signaling API, or service-stop command. Its only external commands are telemetry reads (`nvidia-smi` and `ipmitool`) and local Python/kernel operations needed for publication.

## OCSD layout observed on the qualification host

- SMBIOS Type 229 marker count: 1.
- Allocation size: 16 KiB.
- Physical address observed: `0x791f4000`.
- Header size: 64 bytes.
- Initial device count: 2.
- Record size: 160 bytes.
- First record begins at allocation offset 64.
- Publisher's third record begins at `64 + (2 × 160) = 384`.
- Device count observed after claim: 3.
- Native record header Bus mapping observed by the publisher: 4 then 3.

The allocation address is discovered at runtime. The BDF, native record mapping, and sensor mapping are still hardware-specific and must not be copied to another system without qualification.

## Readiness semantics

`READY=1` means the process claimed and published its OCSD record and began its loop. It does not establish iLO calibration or GPU-driven fan behavior. In the qualification evidence, `22-PCI 2` later returned numeric values and was separately paired with NVIDIA and OCSD samples.

## Fail-high and restore behavior

- If `nvidia-smi` fails during claim or the main loop, the publisher writes the configured conservative value `85 C` into its owned record.
- The publisher does not stop or signal workloads at a temperature threshold.
- On a graceful process stop, the publisher attempts to read the GPU temperature and requires three consecutive samples at or below `55 C` before restoring the original header and clearing its own record.
- If the GPU cannot be read or is not cool within the restore timeout, the publisher leaves the owned OCSD record in place and exits with an error rather than clearing the fail-high state.
- The native records are never intentionally rewritten.

This behavior is based on the current source and synthetic unit tests. Fault behavior on every hardware/firmware condition has not been live-qualified.
