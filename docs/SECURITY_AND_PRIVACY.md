# Security and privacy

## Sensitive material excluded

Never publish:

- iLO passwords, username/password pairs, or `X-Auth-Token` values;
- `/var/lib/gen9-t4-ocsd/ownership.json`;
- physical-memory snapshots or OCSD backups;
- host boot IDs, serial numbers, MAC addresses, private IP addresses, or private hostnames;
- `/etc` configuration copied from the live host;
- private keys, certificates, shell history, or diagnostic transcripts containing secrets.

## Privilege and attack surface

The publisher needs root privileges because it maps a firmware-owned physical memory allocation through `/dev/mem`. This is a high-impact operation. Keep the source small and independently reviewed. Do not add unrelated process or workload management.

## TLS and credentials

Historical diagnostic scripts used disabled TLS certificate verification. They are not included as public tooling. Any new Redfish client must validate a trusted CA or a pinned certificate and fail closed on certificate errors. Credentials must be collected interactively or from a protected secret store, never embedded in source or command-line arguments.

## Runtime behavior

The publisher reads NVIDIA and IPMI telemetry and writes only its validated, owned OCSD record. It does not enumerate, signal, stop, or restart containers, VMs, Docker workloads, or arbitrary processes. A source-level unit test checks for the absence of those APIs/commands; reviewers must still inspect code changes.

## Reporting

No security contact or response-time SLA is currently published. Use the repository's private vulnerability reporting capability if enabled by the maintainer.
