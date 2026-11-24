# Third-party notices and attribution

## Primary publisher source

The host-collected publisher source contains:

- `SPDX-License-Identifier: MIT`
- `Copyright (c) 2026 Josh Murphy (Ocean Media Now)`
- Project attribution to the Ocean Media Now Gen9 OCSD Thermal Bridge

The repository `https://github.com/oceanmedianow/gen9-t4-ocsd-thermal-bridge`
exposes an MIT license in its repository metadata and provides the corresponding
`LICENSE` file. The MIT text is included at the project root. The source header
and copyright notice are preserved.

The current publication source is a cleanup of the exact source collected from
the user's host. It removes dead workload-management stubs/configuration and
renames stale T4-specific runtime messages. It does not claim to be byte-for-byte
the original host file; see `docs/SOURCE_CHANGELOG.md` and `metadata/`.

## OCSD protocol prior art (not vendored)

`https://github.com/conroy-cheers/ocsd` is cited as prior reverse-engineering
work and an explanation of the OCSD concept. No source file from that repository
is included in this package. Its repository page does not expose a LICENSE file
in the root listing; this package does not assume permission to copy or
redistribute that project's source code. See its README and disclaimer for the
single-ML350-Gen9 qualification limitation.

## iLO 4 reverse-engineering prior art (not vendored)

`https://github.com/kendallgoto/ilo4_unlock` is acknowledged in the upstream
OCSD project's documentation. No binary, firmware image, or source file from
that project is included in this package.

## Runtime tools (external prerequisites)

The runtime invokes tools installed by the operator, including:

- NVIDIA driver utilities (`nvidia-smi`)
- `ipmitool`
- Linux kernel interfaces (`/dev/mem`, SMBIOS sysfs, NVIDIA device nodes)
- systemd for service supervision

These are not redistributed by this project and remain subject to their own
licenses and vendor terms.

## Trademark and affiliation notice

HPE, ProLiant, iLO, NVIDIA, GeForce, and Proxmox are names/marks of their
respective owners. This independent experimental project is not sponsored,
endorsed, or supported by HPE, NVIDIA, or Proxmox.
