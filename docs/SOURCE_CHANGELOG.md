# Source changelog for publication RC2

## Baseline

The starting point was the exact host-collected file from
`/opt/gen9-t4-ocsd/gen9_t4_ocsd.py`, with SHA-256:

`a92e6f87ab6037e76d4ba0f0e850bf0e422e9600b7dfddda602e8b2ab0b5178f`

The baseline was collected by the host-side exporter. It was not reconstructed
from chat text.

## Publication-only cleanup

The RC2 source makes these narrowly scoped source changes:

1. Removes unused `stop_workloads`, `workloads_active`, and
   `validate_workload_units` stubs.
2. Removes the obsolete `WORKLOAD_UNITS` environment variable and the stale
   `OCSD_WORKLOAD_UNITS` configuration path.
3. Removes the no-op `request_thermal_stop` wrapper and the old
   `publish_and_guard` name; replaces them with `publish_record`, which only
   writes and read-back-validates the publisher's dedicated record.
4. Removes unused provisional iLO offset/tolerance constants. The observed
   15-degree difference is not implemented as a software correction.
5. Removes the unused 82-degree workload-stop threshold. The publisher does
   not stop or signal any workload at any temperature.
6. Renames the module logger, docstring, and runtime messages so the GTX
   1080 Ti adaptation is not misleadingly described as a Tesla T4 publisher.
7. Retains the existing fail-high value of 85 C for NVIDIA telemetry failure,
   the 75 C continuous threshold encoded in the OCSD record, ownership checks,
   the one-second publication loop, and conservative record restoration logic.

No OCSD binary layout, header checksum, record size, record offset, native
record mapping, GPU BDF, or observed sensor mapping was changed by this cleanup.

## Important provenance distinction

RC2 is a cleaned publication copy, not byte-identical to the running host file.
The host service was not modified by creating this package. The current host
continues to use its own installed file unless an operator separately deploys
this reviewed copy.


The line-by-line unified diff is retained in `docs/SOURCE_DIFF.patch` so the maintainer can review the exact RC1-host-export to RC2-publication changes.
