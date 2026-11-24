# References and qualification context

1. **Ocean Media Now — Gen9 T4 OCSD Thermal Bridge**  
   https://github.com/oceanmedianow/gen9-t4-ocsd-thermal-bridge  
   The public README describes an experimental Tesla T4 implementation for a DL380 Gen9 with stock iLO 4 v2.82, BIOS `OptimalCooling`, and high-performance fans. It records a T4 + 15 °C observation on that tested system only. It explicitly says this does not qualify other firmware/chassis/GPU/fan combinations. The current project uses a GTX 1080 Ti, iLO 4 v2.77, and standard fans.

2. **Ocean Media Now — MIT license**  
   https://raw.githubusercontent.com/oceanmedianow/gen9-t4-ocsd-thermal-bridge/main/LICENSE  
   The MIT license file is included in the package with the copyright notice shown in the upstream source and repository.

3. **conroy-cheers/ocsd**  
   https://github.com/conroy-cheers/ocsd  
   Prior reverse-engineering reference. Its README states that OCSD protocol documentation is not public and that the work was reverse-engineered on a single ML350 Gen9, without testing on other hardware. No source from this repository is included in this package.

4. **HPE iLO 4 RESTful API documentation**  
   https://hewlettpackard.github.io/ilo-rest-api-docs/ilo4/  
   Use iLO 4-specific schema and behavior. Do not infer iLO 4 behavior from iLO 5/6/7 documentation.

5. **HPE iLOrest**  
   https://github.com/HewlettPackard/ilorest  
   External tooling reference. The test host reported iLOrest 7.4.0.0.

These references provide protocol/API context only. They do not certify the user's exact combination of server, firmware, GPU, and standard fans.
