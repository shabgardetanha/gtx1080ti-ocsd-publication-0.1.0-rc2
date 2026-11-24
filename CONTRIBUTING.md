# Contributing

This is an experimental, hardware-specific project. Contributions must not
claim general HPE Gen9 compatibility based on the single qualification host.

Before a change is accepted:

1. Run `python3 -m unittest discover -s tests -v`.
2. Run `python3 -m py_compile src/gen9_t4_ocsd.py`.
3. Run `python3 scripts/verify_candidate.py .`.
4. Review that no workload/container/VM/process lifecycle management has been
   introduced.
5. Preserve the two native OCSD records and test the dedicated third-record
   ownership and restoration behavior using synthetic memory only.
6. For hardware-affecting changes, provide read-only preflight evidence and a
   rollback plan before any live test.
7. Do not include host memory snapshots, ownership state, credentials, private
   IP addresses, or Redfish tokens in commits or issue reports.

Hardware qualification evidence must identify the exact server, iLO firmware,
System ROM, GPU, PCI BDF, fans, and test conditions. Do not use high-load stress
as a shortcut to demonstrate fan response.
