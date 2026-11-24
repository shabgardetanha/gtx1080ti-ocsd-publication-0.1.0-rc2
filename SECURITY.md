# Security policy

This project writes to a firmware-owned physical memory allocation via
`/dev/mem` and requires root privileges. A malformed or incorrectly mapped
write can corrupt management-state data or affect thermal behavior.

## Scope

Security reports should cover this repository's publisher source, packaging,
test tools, and documentation. Do not publish credentials, Redfish tokens,
SMBIOS dumps containing unrelated information, physical-memory snapshots, or
`/var/lib/gen9-t4-ocsd/ownership.json`.

## Operational safeguards

- Use only on the exact hardware profile that has passed local qualification.
- Preserve a verified pre-change OCSD snapshot outside the public repository.
- Never overwrite native OCSD records.
- Do not add workload/container/VM management to the publisher.
- Do not use unverified TLS in reusable Redfish clients.
- Do not flash modified iLO firmware as part of the normal installation.
- Stop testing if the iLO sensor becomes unavailable or the record ownership
  checks fail.

No security contact or response-time SLA is currently published. For private
reports, contact the repository maintainer through the official repository
hosting platform.
