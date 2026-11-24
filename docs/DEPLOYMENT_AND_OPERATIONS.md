# Deployment and operations

This document describes the current experimental package. It is not a universal installer. Do not deploy on a different server without repeating hardware discovery and code review.

## Qualification host observed

- Publisher source path: `/opt/gen9-t4-ocsd/gen9_t4_ocsd.py`
- Service: `gen9-t4-ocsd.service`
- Runtime directory: `/run/gen9-t4-ocsd`
- State directory: `/var/lib/gen9-t4-ocsd`
- State file: `ownership.json`
- Runtime identity: root; requires `/dev/mem`, NVIDIA device nodes, and `/dev/ipmi0`.

## Prerequisites

- Exact HPE ProLiant DL380 Gen9 product match.
- NVIDIA driver installed and `/usr/bin/nvidia-smi` operational.
- `ipmitool` installed.
- `/dev/mem`, `/dev/ipmi0`, `/dev/nvidia0`, `/dev/nvidiactl` accessible to the service.
- One valid 16 KiB OCSD allocation discoverable through SMBIOS Type 229.
- Two valid native OCSD records and a safe, empty or recoverable third slot.
- A preserved private snapshot and a documented recovery path.

## Review and manual installation

The sample unit is `systemd/gen9-t4-ocsd.service`. It is deliberately manual-start-only: it has no `[Install]` section, no `EnvironmentFile`, no Workload Guard, no `ExecStop` helper, and no container/VM hooks.

Review the unit paths and device nodes. If an operator approves deployment on the qualified host, the manual installation shape is:

```bash
install -D -o root -g root -m 0755 \
  src/gen9_t4_ocsd.py \
  /opt/gen9-t4-ocsd/gen9_t4_ocsd.py

install -D -o root -g root -m 0644 \
  systemd/gen9-t4-ocsd.service \
  /etc/systemd/system/gen9-t4-ocsd.service

systemd-analyze verify /etc/systemd/system/gen9-t4-ocsd.service
systemctl daemon-reload
```

Do not run `systemctl enable`. Boot-time activation and reboot persistence are not qualified. Starting the service is a hardware-mutating operation because it opens `/dev/mem` read/write, claims the third OCSD slot, publishes a record, and updates the OCSD device count. Only start it after a host-specific preflight and a maintenance approval.

```bash
systemctl start gen9-t4-ocsd.service
systemctl status gen9-t4-ocsd.service --no-pager -l
journalctl -u gen9-t4-ocsd.service -n 50 --no-pager
```

The above commands are deployment instructions, not proof that deployment was performed by building this package.

## Stop and rollback semantics

A graceful `systemctl stop gen9-t4-ocsd.service` sends a signal to the publisher process itself. It does not signal or manage GPU workloads. The publisher then:

1. verifies that the header still matches its active header;
2. verifies that the third record is still owned by this publisher;
3. samples GPU temperature;
4. requires three consecutive samples at or below 55 C;
5. restores the original header and clears only its own third record.

If telemetry fails or the GPU does not cool within 90 seconds, the publisher retains its record (fail-high) and reports failure. The unit's stop timeout is 150 seconds to allow the bounded restore attempt. Do not use `kill -9` as a routine stop method. Do not manually clear the third record while `ownership.json` says the publisher owns it.

Before deployment, keep a private, verified OCSD snapshot outside the repository. A snapshot is recovery evidence, not a public artifact.

## Runtime observations from the qualification host

- Service type: `notify`.
- Watchdog: 20 seconds.
- Python: 3.13.5 at host export time.
- NVIDIA-SMI: 580.196.07 at host export time.
- The host's previously installed service was `static`; automatic boot enablement was not established.

## Redfish and iLO notes

The iLO 4 Session collection path required a trailing slash on the tested firmware:

`/redfish/v1/SessionService/Sessions/`

The path without the trailing slash returned HTTP 308. The corrected path returned HTTP 201, and the tested Chassis/Thermal GETs returned HTTP 200. A POST to the advertised Manager.Reset target with `{}` returned HTTP 200 and `iLO.0.10.ResetInProgress`; after iLO returned, `22-PCI 2` was observed Enabled/OK. This is a single host observation, not a universal reset or registration guarantee.

Diagnostic scripts used a Python SSL context with certificate verification disabled. Those scripts are not included in the release runtime. Any future reusable Redfish client must validate a CA or pinned certificate and fail closed on certificate errors.

## Operational prohibitions

- Do not modify native OCSD records.
- Do not manually clear the third record while owned.
- Do not copy the physical allocation address to another host.
- Do not repeatedly reset iLO.
- Do not patch iLO firmware as part of normal deployment.
- Do not claim fan-control causality from a single fan-speed change.
- Do not run high-load stress tests just to force a fan response.
- Do not add workload/container/VM/process-management behavior to this publisher.
