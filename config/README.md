# Configuration

The current cleaned publisher is intentionally hardware-pinned to the single
qualification host:

- product: `ProLiant DL380 Gen9`
- GPU BDF: `00000000:0B:00.0`
- OCSD native bus mapping: `(4, 3)` for the two observed native records
- iLO sensor label observed: `22-PCI 2`

No runtime environment file is required by the current source. In particular,
`OCSD_WORKLOAD_UNITS` is obsolete and must not be configured. The publisher
does not discover or manage containers, VMs, Docker workloads, or processes.

Do not change the BDF, Bus/Device tuple, record mapping, or sensor label for
another machine without a new read-only inventory, record-layout review, and
hardware-specific tests.
