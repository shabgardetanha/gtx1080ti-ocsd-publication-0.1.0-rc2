# Incident and change timeline

All dates below are 2026-11-23 as reported in the conversation.

1. **Read-only preflight:** OCSD allocation discovered at `0x791f4000`, size 16 KiB, initial device count 2, third record empty. GPU reported 48 °C.
2. **Initial tooling:** HPE iLOrest 7.4.0.0 installed in `/opt/ilorest`; wrapper created at `/usr/sbin/ilorest`.
3. **Initial registration attempt:** failed because iLO sensor `22-PCI 2` was Disabled/Not Available.
4. **Initial publisher run:** staged unit tests 32/32 passed. Publisher claimed the third OCSD record but PCI BDF case mismatch caused NVIDIA telemetry failure. It published conservative 85 °C; recovery retained the record because telemetry could not be read.
5. **PCI identity correction:** comparison was made case-insensitive. Direct publisher import subsequently read GPU temperature as 48 °C.
6. **Workload-management removal:** final patch script changed publisher behavior to remove workload stop calls and workload-unit validation. Static check passed. Installed service subsequently became active.
7. **Redfish path correction:** Session URL without trailing slash returned HTTP 308. Adding the trailing slash produced HTTP 201 and valid token; Chassis and Thermal GET returned HTTP 200.
8. **iLO reset:** first generic script cancelled because no ResetType values were advertised. A subsequent request to the advertised `Manager.Reset` target with `{}` returned HTTP 200 / `ResetInProgress`. One reset was accepted.
9. **Sensor discovery after reset:** iLO Redfish reported `22-PCI 2` as Enabled/OK at 64 °C; PCI 1 and PCI 3 were Absent. PCI 2 Zone remained Enabled at 36 °C.
10. **Five paired samples:** GPU 48–49 °C, OCSD 48–49 °C, iLO PCI2 63–64 °C; iLO–GPU delta 14–16 °C, mean 15 °C.
11. **Fan monitor:** 23 supplied samples showed GPU 48–49 °C and PCI2 63–64 °C. Fans 4–6 transiently reached 65/82/65% at sample 8, then returned gradually toward 26/27/27%. Since GPU and PCI2 temperatures remained nearly constant, causal GPU-to-fan response is not demonstrated.

## Lessons learned

- Normalize PCI BDF case before comparison and test it explicitly.
- Distinguish OCSD record ordinal from iLO sensor label.
- A numeric iLO reading is not proof of a calibrated GPU temperature relationship.
- A fan speed transient is not proof of causality; log concurrent thermal inputs.
- Do not treat legacy staging unit tests as validation of a later patched source tree.
- iLO 4's Session collection path required a trailing slash on this firmware.
- Do not infer a `ResetType` when the iLO action does not advertise one; inspect the action and use its documented payload.
- Keep workload management outside the publisher.
