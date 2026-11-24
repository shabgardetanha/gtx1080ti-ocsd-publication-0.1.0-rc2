# Compatibility and limitations

## Qualification profile

Only one observed host profile is included in the evidence: HPE DL380 Gen9,
iLO 4 firmware 2.77, P89/System ROM with BIOS revision 2.76, NVIDIA GeForce
GTX 1080 Ti Founders Edition in PCI Slot 2, Proxmox VE 9.2.2, kernel
`7.0.2-6-pve`, standard system fans.

## Difference from the upstream reference system

The Ocean Media Now upstream README describes a Tesla T4 implementation on a
DL380 Gen9 with stock iLO 4 v2.82, BIOS `OptimalCooling`, and high-performance
fans. The same README explicitly limits its claims to the tested machine. The
user's system is not that profile: it uses a GTX 1080 Ti, iLO 4 v2.77, and
standard fans. Do not infer equivalence from the shared Gen9 model name.

## What the evidence supports

- iLO sensor `22-PCI 2` can become Enabled/OK on the tested machine after one
  iLO management-processor reset while the publisher record is present.
- During five paired samples, iLO read approximately GPU temperature +15 °C.
- Fan readings changed during a separate observation window, but GPU and PCI2
  temperatures were essentially constant. Therefore GPU-driven fan response is
  not established.

## Known unknowns

- Whether the 15 °C difference is stable across temperature/load range.
- Whether iLO thermal policy directly uses the PCI2 value for fan control on
  this firmware/fan configuration.
- Fan policy thresholds, delay, hysteresis, and other sensor interactions.
- Long-duration data integrity and recovery across host/iLO reboot or faults.
- Compatibility with other GPUs, slots, BIOS settings, iLO revisions, fan kits,
  or DL380 Gen9 system configurations.

## Unsupported claims

Do not claim that this is HPE supported, that all Gen9 systems behave the same,
that fans are proven to track GPU temperature, or that 15 °C is a universal
calibration offset.
