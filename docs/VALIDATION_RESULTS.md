# Validation results

This document separates captured host observations from RC2 package tests. The RC2 unit tests use synthetic memory and mocks; they do not access the live hardware.

## 1. Host observations supplied in the project handoff

| Item | Observation | Scope |
|---|---|---|
| NVIDIA telemetry | `00000000:0B:00.0`, 48–49 °C | Qualification host |
| OCSD allocation | `0x791f4000`, 16 KiB | Qualification host only |
| Header device count | 2 initially, 3 after publish | Qualification host |
| OCSD record | valid in five paired samples | Qualification host |
| Record counter | 2030 to 2051 | Qualification host |
| iLO PCI sensor | `22-PCI 2`, Enabled/OK | After one iLO reset |
| GPU temperature | 48–49 °C across five samples | Paired sample window |
| iLO sensor temperature | 63–64 °C across five samples | Paired sample window |
| Mean iLO-GPU delta | 15.0 °C | Five samples; not calibrated |

## 2. Five paired readings

| Sample | GPU °C | GPU util % | OCSD °C | Counter | iLO PCI2 °C | iLO-GPU °C |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 49 | 0 | 48 | 2030 | 64 | 15 |
| 2 | 49 | 0 | 48 | 2035 | 63 | 14 |
| 3 | 48 | 0 | 49 | 2040 | 64 | 16 |
| 4 | 49 | 0 | 49 | 2046 | 63 | 14 |
| 5 | 48 | 0 | 48 | 2051 | 64 | 16 |

Means: GPU 48.6 °C; OCSD record 48.4 °C; iLO PCI2 63.6 °C; iLO-GPU delta 15.0 °C. This validates a stable relationship during a nearly constant idle point only; it does not validate slope, offset stability, latency, hysteresis, full temperature range, or fan causality.

## 3. Twenty-three fan samples

GPU remained 48–49 °C; iLO PCI2 remained 63–64 °C; PCI2 Zone remained 35–36 °C.

| Sample window | Fan 1 | Fan 2 | Fan 3 | Fan 4 | Fan 5 | Fan 6 |
|---|---:|---:|---:|---:|---:|---:|
| Initial samples 1–7 | 9 | 9 | 23 | 29 | 29 | 29 |
| Peak at sample 8 | 16 | 16 | 23 | 65 | 82 | 65 |
| Sample 9 | 14 | 14 | 23 | 55 | 69 | 55 |
| Sample 10 | 11 | 11 | 21 | 41 | 52 | 41 |
| Sample 12 | 12 | 12 | 21 | 50 | 63 | 50 |
| Samples 14–15 | 9 | 9 | 21 | 32 | 40 | 32 |
| Samples 17–23 | 9 | 9 | 21 | 26 | 27 | 27 |

Interpretation: fan speeds changed substantially during the monitoring window, but GPU and PCI2 temperatures were nearly unchanged. Possible confounders include other thermal inputs and iLO policy settling. These samples do not prove that the fan transient was caused by the GPU sensor.

## 4. PCI sensor inventory after iLO reset

| Sensor | Reading | State |
|---|---:|---|
| 21-PCI 1 | 0 °C | Absent |
| 22-PCI 2 | 63–64 °C | Enabled / OK |
| 23-PCI 3 | 0 °C | Absent |
| 31-PCI 1 Zone | 35–36 °C | Enabled |
| 32-PCI 2 Zone | 35–36 °C | Enabled |
| 33-PCI 3 Zone | 35–36 °C | Enabled |

Do not confuse the physical PCI sensor with the corresponding PCI Zone sensor.

## 5. RC2 package tests run in the build environment

| Check | Result | Qualification |
|---|---|---|
| `py_compile` on publisher and tests | PASS | Current cleaned RC2 source |
| Unit tests | 26/26 PASS | Current cleaned RC2 source; synthetic memory/mocks |
| Static candidate verifier | PASS | Source/secret/API-symbol checks; manual review remains necessary |
| `systemd-analyze verify` | PASS | Example unit syntax only; not installed on the user's Host |
| Full hardware integration | NOT RUN | No hardware/Host operations in package-building environment |

Test coverage includes header checksum/validation, device-count update, native header mapping, record construction/ownership/corruption, GPU BDF matching and temperature range, iLO text parsing, SMBIOS Type 229 discovery, dedicated-record publication, claim/native-record preservation, initial fail-high when GPU telemetry fails, graceful restore with three cool samples, retention of the owned fail-high record when the GPU remains hot, and absence of workload-management calls. Three additional packaging tests verify the manual-start-only unit and legal notice files.

## 6. Remaining qualification gaps

- Additional paired samples at different naturally occurring GPU temperatures.
- Fan-response correlation while recording all other thermal inputs.
- Long-duration stability and watchdog recovery.
- Reboot persistence and controlled crash recovery.
- Hardware fault-injection under a recoverable test condition.
- Independent maintainer review and public repository release process.

Raw tabular data are retained as `validation/paired_samples_5.csv` and
`validation/fan_response_23_samples.csv` for later plotting and independent
review.
