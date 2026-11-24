# Publishing notes — RC2

This publication package contains the host-collected publisher source after a
small, documented cleanup, a new hardware-independent test suite, a manual
systemd unit example, licensing/attribution files, and updated Persian/English
documentation.

The package does not contain the active host's ownership state, physical-memory
snapshot, Redfish credentials/tokens, host service unit, or separate workload
utilities. The RC2 source is not byte-identical to the host source; hashes and
the exact cleanup are recorded in `docs/SOURCE_CHANGELOG.md`.

Before pushing to a public repository:

1. Review `LICENSE` and `legal/THIRD_PARTY_NOTICES.md` against the maintainer's
   right to publish the source.
2. Inspect the entire diff and the test suite.
3. Run `make check` in a clean Python environment.
4. Keep the release experimental until fan-control causality, soak testing,
   reboot persistence, and hardware-specific qualification are complete.

Suggested Git tag: `v0.1.0-rc2`. Do not use `v0.1.0` or mark it stable.
