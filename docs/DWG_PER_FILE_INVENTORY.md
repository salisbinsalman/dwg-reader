# DWG Per-File Inventory

Complete forensic breakdown of every DWG in the dataset.
Generated from ODA File Converter + ezdxf parse of all 84 indexed DWGs.

**Parse failures:** 15 KSD DWGs fail with `DXFStructureError: missing ENDSEC tag` — these are marked ❌ and only CSV metadata is available.

## Summary Table

| # | Folder | Drawing | Title | Objects | Attrs | Conn | Ecosystem |
|---|--------|---------|-------|--------:|------:|------|-----------|
| 1 | CHEM_PID | `PCSG028666.03_Surface_size_preparation.dwg` | PCSG028666.03 Surface size preparation | 8529 | 83 | ✅ LIN_FROM/LIN_TO (94 records) | Valmet PS-21 |
| 2 | CHEM_PID | `PCSG028670.03_CPAM.dwg` | PCSG028670.03 CPAM | 4126 | 82 | ✅ LIN_FROM/LIN_TO (40 records) | Valmet PS-21 |
| 3 | CHEM_PID | `PCSG028671.02_Bentonite.dwg` | PCSG028671.02 Bentonite | 4968 | 83 | ✅ LIN_FROM/LIN_TO (55 records) | Valmet PS-21 |
| 4 | CHEM_PID | `PCSG028672.02_Dye_brown.dwg` | PCSG028672.02 Dye brown | 2733 | 78 | ✅ LIN_FROM/LIN_TO (22 records) | Valmet PS-21 |
| 5 | CHEM_PID | `PCSG028673.02_Defoamer.dwg` | PCSG028673.02 Defoamer | 2404 | 74 | ✅ LIN_FROM/LIN_TO (20 records) | Valmet PS-21 |
| 6 | OCC_PID | `STOD206340.10 OCC Pulping line 1.dwg` | OCC Pulping line 1 | 5410 | 65 | ✅ LIN_FROM/LIN_TO (72 records) | Valmet PS-21 |
| 7 | OCC_PID | `STOD206341.10 OCC Pulping line 2.dwg` | OCC Pulping line 2 | 5464 | 65 | ✅ LIN_FROM/LIN_TO (74 records) | Valmet PS-21 |
| 8 | OCC_PID | `STOD206342.10 OCC cleaning and fractionation.dwg` | OCC Cleaning and fractionation | 12771 | 50 | ✅ LIN_FROM/LIN_TO (252 records) | Valmet PS-21 |
| 9 | OCC_PID | `STOD206343.10 OCC Thickening.dwg` | OCC Thickening | 12405 | 92 | ✅ LIN_FROM/LIN_TO (258 records) | Valmet PS-21 |
| 10 | OCC_PID | `STOD206344.13_OCC Reject handling.dwg` | OCC Reject handling | 8760 | 50 | ✅ LIN_FROM/LIN_TO (140 records) | Valmet PS-21 |
| 11 | OCC_PID | `STOD212164.03 OCC Utility Pipe Routes.dwg` | OCC UTILITY PIPE ROUTES | 195065 | 36 | ✅ LIN_FROM/LIN_TO (111 records) | Valmet PS-21 |
| 12 | PM03_PID | `PCSG028667.02_sizing_agent.dwg` | PCSG028667.02 sizing agent | 2390 | 81 | ✅ LIN_FROM/LIN_TO (16 records) | Valmet PS-21 |
| 13 | PM03_PID | `PCSG028668.02_PAC.dwg` | PCSG028668.02 PAC | 2222 | 74 | ✅ LIN_FROM/LIN_TO (17 records) | Valmet PS-21 |
| 14 | PM03_PID | `PCSG028669.02_Defoamer_and_biocide.dwg` | PCSG028669.02 Defoamer and biocide | 2466 | 73 | ✅ LIN_FROM/LIN_TO (17 records) | Valmet PS-21 |
| 15 | PM03_PID | `PCSG028674.02_Biocide and hypochloride.dwg` | PCSG028674.02 Biocide and hypochloride | 1961 | 75 | ✅ LIN_FROM/LIN_TO (9 records) | Valmet PS-21 |
| 16 | PM03_PID | `PCSG028675.03_Biocide_and_hypochloride_dosing.dwg` | PCSG028675.03 Biocide and hypochloride d… | 2704 | 82 | ✅ LIN_FROM/LIN_TO (12 records) | Valmet PS-21 |
| 17 | PM03_PID | `PCSG028676.03_Micropolymer_and_wire_conditioning.dwg` | PCSG028676.03 Micropolymer and wire cond… | 2871 | 75 | ✅ LIN_FROM/LIN_TO (30 records) | Valmet PS-21 |
| 18 | PM03_PID | `PCSG028677.03_Wire_and_felt_cleaning_agents.dwg` | PCSG028677.03 Wire and felt cleaning age… | 2936 | 64 | ✅ LIN_FROM/LIN_TO (23 records) | Valmet PS-21 |
| 19 | PM03_PID | `PCSG028678.03_Optisizer_hard_with_spray_supply_system.dwg` | PCSG028678.03 Optisizer hard with spray … | 8470 | 82 | ✅ LIN_FROM/LIN_TO (134 records) | Valmet PS-21 |
| 20 | PM03_PID | `RAU6401403_03_FLOW_DIAGRAM_OCPRO.dwg` | RAU6401403 03 FLOW DIAGRAM OCPRO | 69171 | 107 | ⚠️ XDATA present, no named endpoints | Valmet flow-diag. |
| 21 | PM03_PID | `RAU6401404_01_FLOW_DIAGRAM_DOUBLEJET_TAIL_JET_P.dwg` | RAU6401404 01 FLOW DIAGRAM DOUBLEJET TAI… | 8290 | 83 | ⚠️ XDATA present, no named endpoints | Valmet flow-diag. |
| 22 | PM03_PID | `RAU8F00290.10_Steam and Condensate.dwg` | Steam and Condensate System | 25884 | 119 | ✅ LIN_FROM/LIN_TO (857 records) | Valmet PS-21 |
| 23 | PM03_PID | `RAU8G02312.11 Shower Water system.dwg` | Shower Water system | 18590 | 83 | ✅ LIN_FROM/LIN_TO (446 records) | Valmet PS-21 |
| 24 | PM03_PID | `RAU8G02313.11 Vacuum system.dwg` | Vacuum system | 8417 | 67 | ✅ LIN_FROM/LIN_TO (224 records) | Valmet PS-21 |
| 25 | PM03_PID | `RAU8G02314.09 Fresh and Cooling Water system.dwg` | Fresh and Cooling Water system | 242142 | 55 | ✅ LIN_FROM/LIN_TO (72 records) | Valmet PS-21 |
| 26 | PM03_PID | `RAU8G02315.10 Compressed Air system.dwg` | Compressed Air System | 74303 | 53 | ✅ LIN_FROM/LIN_TO (15 records) | Valmet PS-21 |
| 27 | PM03_PID | `RAU8G02316.10 Instrument Air.dwg` | Instrument Air | 159633 | 54 | ✅ LIN_FROM/LIN_TO (13 records) | Valmet PS-21 |
| 28 | PM03_PID | `RAU8G02317.09 Sealing Water system.dwg` | Sealing Water system | 11997 | 59 | ✅ LIN_FROM/LIN_TO (15 records) | Valmet PS-21 |
| 29 | PM03_PID | `RAU8G02327.09 Heating water.dwg` | Heating Water system | 14356 | 46 | ✅ LIN_FROM/LIN_TO (112 records) | Valmet PS-21 |
| 30 | PM03_PID | `RAU8G02334.07 Connections Between Departments.dwg` | CONNECTIONS BETWEEN DEPARTMENTS | 1424 | 43 | ✅ LIN_FROM/LIN_TO (84 records) | Valmet PS-21 |
| 31 | PM03_PID | `RAU8G02456.00 Washing water utility pipe route.dwg` | Washing water pipe route | 38841 | 45 | ⚠️ XDATA present, no named endpoints | Valmet PS-21 |
| 32 | PM03_PID | `STOD206336.11 Stock Preparation and Mixing area.dwg` | Stock Preparation and Mixing area | 7627 | 69 | ✅ LIN_FROM/LIN_TO (150 records) | Valmet PS-21 |
| 33 | PM03_PID | `STOD206337.11 Approach Flow System.dwg` | Approach Flow System | 8684 | 50 | ✅ LIN_FROM/LIN_TO (118 records) | Valmet PS-21 |
| 34 | PM03_PID | `STOD206338.11_White Water system.dwg` | White Water System | 4929 | 68 | ✅ LIN_FROM/LIN_TO (101 records) | Valmet PS-21 |
| 35 | PM03_PID | `STOD206339.10 Broke System.dwg` | Broke System | 11376 | 69 | ✅ LIN_FROM/LIN_TO (215 records) | Valmet PS-21 |
| 36 | TM01_PID | `GORA68210.05_Code 03 - P&ID AirCap_SWE Shotton_CE.dwg` | GORA68210.05 Code 03 - P&ID AirCap SWE S… | 7550 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 37 | TM01_PID | `GORA68211.03_Code 03 - P&Id Adv ReDry_SWE Shotton_CE.dwg` | GORA68211.03 Code 03 - P&Id Adv ReDry SW… | 4757 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 38 | TM01_PID | `GORA68212.04_Code 03 - P&ID Heat Recoveries_SWE Shotton_CE.dwg` | GORA68212.04 Code 03 - P&ID Heat Recover… | 4316 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 39 | TM01_PID | `KSDM160104102_04_SH01_Bale handling_C.dwg` | KSDM160104102 04 SH01 Bale handling C | 69 | 0 | ❌ parse failed | KSD Swedish |
| 40 | TM01_PID | `KSDM160104102_07_SH03_Soft and hardwood line_C.dwg` | KSDM160104102 07 SH03 Soft and hardwood … | 31 | 82 | 🔴 No semantic connectivity | KSD Swedish |
| 41 | TM01_PID | `KSDM160104102_07_SH05_Thick stock screening_C.dwg` | KSDM160104102 07 SH05 Thick stock screen… | 17 | 0 | ❌ parse failed | KSD Swedish |
| 42 | TM01_PID | `KSDM160104102_07_SH06_Approach system_C.dwg` | KSDM160104102 07 SH06 Approach system C | 170 | 0 | ❌ parse failed | KSD Swedish |
| 43 | TM01_PID | `KSDM160104102_07_SH07_Machine broke pulper system_C.dwg` | KSDM160104102 07 SH07 Machine broke pulp… | 60 | 81 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 44 | TM01_PID | `KSDM160104102_07_SH09_Internal broke system_C.dwg` | KSDM160104102 07 SH09 Internal broke sys… | 91 | 84 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 45 | TM01_PID | `KSDM160104102_08_SH02_SW_HW Dissolving system_C.dwg` | KSDM160104102 08 SH02 SW HW Dissolving s… | 104 | 83 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 46 | TM01_PID | `KSDM160104102_09_SH04_Mixing system_C.dwg` | KSDM160104102 09 SH04 Mixing system C | 12 | 0 | ❌ parse failed | KSD Swedish |
| 47 | TM01_PID | `KSDM160104102_09_SH08_Converting broke pulper_C.dwg` | KSDM160104102 09 SH08 Converting broke p… | 190 | 0 | ❌ parse failed | KSD Swedish |
| 48 | TM01_PID | `KSDM160104103_05_SH01_White water system_C.dwg` | KSDM160104103 05 SH01 White water system… | 32 | 0 | ❌ parse failed | KSD Swedish |
| 49 | TM01_PID | `KSDM160104103_08_SH04_White water system_C.dwg` | KSDM160104103 08 SH04 White water system… | 32 | 0 | ❌ parse failed | KSD Swedish |
| 50 | TM01_PID | `KSDM160104103_09_SH02_White water system_C.dwg` | KSDM160104103 09 SH02 White water system… | 32 | 0 | ❌ parse failed | KSD Swedish |
| 51 | TM01_PID | `KSDM160104103_09_SH03_White water system_C.dwg` | KSDM160104103 09 SH03 White water system… | 27 | 0 | ❌ parse failed | KSD Swedish |
| 52 | TM01_PID | `KSDM160104104_06_SH01_Shower water system_C.dwg` | KSDM160104104 06 SH01 Shower water syste… | 30845 | 0 | ❌ parse failed | KSD Swedish |
| 53 | TM01_PID | `KSDM160104105_05_SH03_Fresh water system_C.dwg` | KSDM160104105 05 SH03 Fresh water system… | 73 | 72 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 54 | TM01_PID | `KSDM160104105_06_SH01_Fresh water system_C.dwg` | KSDM160104105 06 SH01 Fresh water system… | 11 | 84 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 55 | TM01_PID | `KSDM160104105_06_SH02_Fresh water system_C.dwg` | KSDM160104105 06 SH02 Fresh water system… | 61 | 0 | ❌ parse failed | KSD Swedish |
| 56 | TM01_PID | `KSDM160104106_08_SH01_Vacuum system_C.dwg` | KSDM160104106 08 SH01 Vacuum system C | 142 | 82 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 57 | TM01_PID | `KSDM160104107_09_SH01_Steam and condensate system_C.dwg` | KSDM160104107 09 SH01 Steam and condensa… | 26293 | 0 | ❌ parse failed | KSD Swedish |
| 58 | TM01_PID | `KSDM160104108_06_SH01_Mill air system_C.dwg` | KSDM160104108 06 SH01 Mill air system C | 82 | 0 | ❌ parse failed | KSD Swedish |
| 59 | TM01_PID | `KSDM160104110_08_SH01_Internal effluent treatment_C.dwg` | KSDM160104110 08 SH01 Internal effluent … | 201 | 0 | ❌ parse failed | KSD Swedish |
| 60 | TM01_PID | `KSDM160104111_06_SH01_Process ventilation_C.dwg` | KSDM160104111 06 SH01 Process ventilatio… | 51 | 0 | ❌ parse failed | KSD Swedish |
| 61 | TM01_PID | `KSDM160104112_05_SH01_Sealing water system_C.dwg` | KSDM160104112 05 SH01 Sealing water syst… | 71 | 76 | ⚠️ XDATA present, no named endpoints | KSD Swedish |
| 62 | TM01_PID | `GORA68208.04_Code 13 - P&Id Mist Removal_SWE Shotton_CE.dwg` | GORA68208.04 Code 13 - P&Id Mist Removal… | 3705 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 63 | TM01_PID | `GORA68209.03_Code 13 - P&ID AdvWetDust_SWE Shotton_CE.dwg` | GORA68209.03 Code 13 - P&ID AdvWetDust S… | 3833 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 64 | TM01_PID | `GORB18781.02_Code 13 - P&ID Active AirFoil_SWE Shotton_CE.dwg` | GORB18781.02 Code 13 - P&ID Active AirFo… | 3080 | 0 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 65 | TM01_PID | `GORB18782.02_Code 13 - P&ID QCS - WIS_SWE Shotton_CE.dwg` | GORB18782.02 Code 13 - P&ID QCS - WIS SW… | 2067 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 66 | TM01_PID | `GORA68213.05_Code 14 - P&ID MHV Heat recovery_SWE Shotton_CE.dwg` | GORA68213.05 Code 14 - P&ID MHV Heat rec… | 9893 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 67 | TM01_PID | `GORA68267.03_Code 14 - MHV Water ring piping overview_SWE Shotton_CE.dwg` | GORA68267.03 Code 14 - MHV Water ring pi… | 6328 | 40 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 68 | TM01_PID | `GORB18777.05_Code 14 - P&ID Turboblower & WE Roof heating_SWE Shotton_CE.dwg` | GORB18777.05 Code 14 - P&ID Turboblower … | 5780 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 69 | TM01_PID | `GORB18778.04_SH1(2)_Code 14 - P&ID Ventil Unit SU01_SWE Shotton_CE.dwg` | GORB18778.04 SH1(2) Code 14 - P&ID Venti… | 3422 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 70 | TM01_PID | `GORB18778.04_SH2(2)_Code 14 - P&ID Ventil Unit SU02_SWE Shotton_CE.dwg` | GORB18778.04 SH2(2) Code 14 - P&ID Venti… | 3355 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 71 | TM01_PID | `GORB18779.05_SH1(12)_Code 14 - P&ID Ventil Unit WU01_SWE Shotton_CE.dwg` | GORB18779.05 SH1(12) Code 14 - P&ID Vent… | 4583 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 72 | TM01_PID | `GORB18779.05_SH10(12)_Code 14 - P&ID Ventil Unit WU10_SWE Shotton_CE.dwg` | GORB18779.05 SH10(12) Code 14 - P&ID Ven… | 4576 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 73 | TM01_PID | `GORB18779.05_SH11(12)_Code 14 - P&ID Ventil Unit WU11_SWE Shotton_CE.dwg` | GORB18779.05 SH11(12) Code 14 - P&ID Ven… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 74 | TM01_PID | `GORB18779.05_SH12(12)_Code 14 - P&ID Ventil Unit WU12_SWE Shotton_CE.dwg` | GORB18779.05 SH12(12) Code 14 - P&ID Ven… | 4623 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 75 | TM01_PID | `GORB18779.05_SH2(12)_Code 14 - P&ID Ventil Unit WU02_SWE Shotton_CE.dwg` | GORB18779.05 SH2(12) Code 14 - P&ID Vent… | 4573 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 76 | TM01_PID | `GORB18779.05_SH3(12)_Code 14 - P&ID Ventil Unit WU03_SWE Shotton_CE.dwg` | GORB18779.05 SH3(12) Code 14 - P&ID Vent… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 77 | TM01_PID | `GORB18779.05_SH4(12)_Code 14 - P&ID Ventil Unit WU04_SWE Shotton_CE.dwg` | GORB18779.05 SH4(12) Code 14 - P&ID Vent… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 78 | TM01_PID | `GORB18779.05_SH5(12)_Code 14 - P&ID Ventil Unit WU05_SWE Shotton_CE.dwg` | GORB18779.05 SH5(12) Code 14 - P&ID Vent… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 79 | TM01_PID | `GORB18779.05_SH6(12)_Code 14 - P&ID Ventil Unit WU06_SWE Shotton_CE.dwg` | GORB18779.05 SH6(12) Code 14 - P&ID Vent… | 4585 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 80 | TM01_PID | `GORB18779.05_SH7(12)_Code 14 - P&ID Ventil Unit WU07_SWE Shotton_CE.dwg` | GORB18779.05 SH7(12) Code 14 - P&ID Vent… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 81 | TM01_PID | `GORB18779.05_SH8(12)_Code 14 - P&ID Ventil Unit WU08_SWE Shotton_CE.dwg` | GORB18779.05 SH8(12) Code 14 - P&ID Vent… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 82 | TM01_PID | `GORB18779.05_SH9(12)_Code 14 - P&ID Ventil Unit WU09_SWE Shotton_CE.dwg` | GORB18779.05 SH9(12) Code 14 - P&ID Vent… | 4574 | 5 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 83 | TM01_PID | `GORB18780.03_Code 14 - P&ID Bale pulper Extractor_SWE Shotton_CE.dwg` | GORB18780.03 Code 14 - P&ID Bale pulper … | 1886 | 1 | ⚠️ XDATA present, no named endpoints | GOR Italian |
| 84 | TM01_PID | `GORB18784.04_Code 14 - P&ID Machine Hall Extractors_SWE Shotton_CE.dwg` | GORB18784.04 Code 14 - P&ID Machine Hall… | 2311 | 0 | ⚠️ XDATA present, no named endpoints | GOR Italian |

---

## CHEM_PID  ·  Valmet PS-21

### 1. `PCSG028666.03_Surface_size_preparation.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `jani.linden` |
| Objects | 8529 |
| Entities (model space) | 4199 |
| Layers | 60 |
| Block definitions | 51 |
| Unique attribute tags | 83 |
| App ID fingerprint | PCAD ×19 | GENIUS ×35 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (94 records) |

**Entities:** LINE×1782, TEXT×988, INSERT×935, LWPOLYLINE×320, ARC×116, CIRCLE×39, MTEXT×14, ATTDEF×2

**Layers (60):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `H`, `P-OTHER`, `Valmet`, `T-POS`, `Valmet_border_out`, `Valmet_border_in`, `DEFPOINTS`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid` … +20 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (49):**

  - `MOTOR` (10 entities)
  - `SEK2` (7 entities)
  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `TAKAISKU` (11 entities)
  - `TOIMRAJA` (5 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `POSPRM` (20 entities)
  - `LEROTIN` (2 entities)
  - `TOIMILVK` (10 entities)
  - `KOMPR` (3 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `VAROV` (19 entities)
  - `POSPMM` (17 entities)
  - `TASO` (4 entities)
  - `PUTPOS` (1 entities)
  - `ylaosamerkkiA3` (12 entities)
  - `hdr_inspoint` (3 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `muutostau` (32 entities)
  - `Valmet_china_copyright` (815 entities)
  - `Valmet_copyright` (3 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - … +19 more

**Most-used block inserts:**

  - `PPI_0900A` ×148
  - `PPI_1100A` ×95
  - `N` ×91
  - `PPI_1207A` ×83
  - `VENT` ×78
  - `P7A1304` ×68
  - `VENTK` ×30
  - `PPI_0102B` ×30
  - `PPI_1000A` ×30
  - `PPI_00` ×30
  - `PESUYHDE` ×29
  - `PPI_1302A-25_0` ×28
  - `MOTOR` ×27
  - `TOIMILV` ×22
  - `TOIMILVK` ×22

**Attribute tags & sample values (83 unique tags):**

  - `LINJA` ×139 — `13`
  - `VENIMI` ×138 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×138 — `103`
  - `VEKOKO` ×138 — `x`
  - `VETYYPPI` ×138 — `101`
  - `VEKEMIKAALI` ×138 — `NESTE`
  - `VEVALMISTAJA` ×138 — `xx`
  - `IVENIMI` ×44 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×44 — `408`
  - `IVEKOKO` ×44 — `x`
  - `IVETYYPPI` ×44 — `101`
  - `ILINJA` ×44 — `402`
  - `IVEKEMIKAALI` ×44 — `123`
  - `IVEVALMISTAJA` ×44 — `xx`
  - `MOTOR` ×27 — `MOTOR`
  - `MOTORPOS` ×27 — `MOTORPOS`
  - `POWER` ×27 — `POWER`
  - `RPM` ×27 — `RPM`
  - `CURRENT` ×27 — `CURRENT`
  - `DRIVE` ×27 — `DRIVE`
  - `MOUNTED` ×27 — `MOUNTED`
  - `OSOITE` ×18 — `FRESH WATER`
  - `POSITIO` ×11 — `1407.1`
  - `LAITE` ×11 — `ECCENTRIC SCREW PUMP`
  - `PAINE` ×11 — `4`
  - `TILAVUUS` ×11 — `100`
  - `GALLONS` ×11 — `25.0`
  - `KEMIKAALI` ×11 — `PIG`
  - `DN1` ×11 — `80`
  - `DN2` ×11 — `80`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `15 m³/h` _(layer: T)_
  - `Mass` _(layer: T)_
  - `flow` _(layer: T)_
  - `meter` _(layer: T)_
  - `150 µm` _(layer: T)_
  - `RF-33` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `0.3 m` _(layer: T)_
  - `3` _(layer: T)_
  - `EL.` _(layer: Valmet)_
  - `800 µm` _(layer: T)_
  - `FILTERS` _(layer: T)_
  - `COARSE` _(layer: T)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `ROMANS` (ROMANS.SHX), `SFS` (txt), `Copyright` (romans.shx), `Text3_2` (txt.shx), `ISOCP` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 2. `PCSG028670.03_CPAM.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 4126 |
| Entities (model space) | 1694 |
| Layers | 52 |
| Block definitions | 63 |
| Unique attribute tags | 82 |
| App ID fingerprint | PCAD ×19 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (40 records) |

**Entities:** LINE×613, TEXT×444, INSERT×428, LWPOLYLINE×165, CIRCLE×26, ARC×12, MTEXT×4, ATTDEF×2

**Layers (52):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `P-OTHER`, `Valmet`, `TEXT`, `Valmet_logo_color_green_solid`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de` … +12 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (61):**

  - `MOTOR` (10 entities)
  - `SEK2` (7 entities)
  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `TAKAISKU` (11 entities)
  - `TOIMRAJA` (5 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `POSPRM` (20 entities)
  - `VS` (8 entities)
  - `TOIMILVK` (10 entities)
  - `MOOTTORI` (3 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `A$C52093E87` (1 entities)
  - `A$C15FA388F` (3 entities)
  - `A$C57672F6B` (3 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_1201A` (2 entities)
  - `PPI_0504A-45_0` (6 entities)
  - `A$793EF` (1 entities)
  - `muutostau` (32 entities)
  - `A$796D7` (1 entities)
  - `A$796FC` (1 entities)
  - … +31 more

**Most-used block inserts:**

  - `PPI_0900A` ×58
  - `PPI_1207A` ×43
  - `N` ×41
  - `PPI_1100A` ×38
  - `P7A1304` ×36
  - `VENT` ×33
  - `VENTK` ×18
  - `PPI_0102B` ×14
  - `PPI_1000A` ×14
  - `PPI_00` ×13
  - `PPI_1201A` ×11
  - `PESUYHDE` ×10
  - `PPI_1302A-25_0` ×10
  - `FRESH WATER` ×8
  - `TAKAISKU` ×8

**Attribute tags & sample values (82 unique tags):**

  - `VENIMI` ×65 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×65 — `1002`
  - `VEKOKO` ×65 — `x`
  - `VETYYPPI` ×65 — `101`
  - `LINJA` ×65 — `101`
  - `VEKEMIKAALI` ×65 — `NESTE`
  - `VEVALMISTAJA` ×65 — `xx`
  - `IVENIMI` ×11 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×11 — `108`
  - `IVEKOKO` ×11 — `x`
  - `IVETYYPPI` ×11 — `101`
  - `ILINJA` ×11 — `103`
  - `IVEKEMIKAALI` ×11 — `NESTE`
  - `IVEVALMISTAJA` ×11 — `xx`
  - `OSOITE` ×10 — `SEALING WATER`
  - `KOODI` ×6
  - `MOTOR` ×5 — `MOTOR`
  - `MOTORPOS` ×5 — `MOTORPOS`
  - `POWER` ×5 — `POWER`
  - `RPM` ×5 — `RPM`
  - `CURRENT` ×5 — `CURRENT`
  - `DRIVE` ×5 — `DRIVE`
  - `MOUNTED` ×5 — `MOUNTED`
  - `POSITIO` ×5 — `107.1`
  - `LAITE` ×5 — `ECCENTRIC SCREW PUMP`
  - `PAINE` ×5 — `4`
  - `TILAVUUS` ×5 — `100`
  - `GALLONS` ×5 — `25.0`
  - `KEMIKAALI` ×5 — `PIG`
  - `DN1` ×5 — `80`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `30-40  C` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `150 µm` _(layer: T)_
  - `STAND-BY` _(layer: T)_
  - `WET END CHEMICAL` _(layer: T)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `36-42P502` _(layer: P-PUMP_POS)_
  - `700-1400 lpm` _(layer: P-PUMP_POS)_
  - `4 bar` _(layer: P-PUMP_POS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `ROMANS` (ROMANS.SHX), `Copyright` (romans.shx), `ISOCP` (ARIALN.TTF), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 3. `PCSG028671.02_Bentonite.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 4968 |
| Entities (model space) | 2336 |
| Layers | 51 |
| Block definitions | 66 |
| Unique attribute tags | 83 |
| App ID fingerprint | PCAD ×19 | GENIUS ×3 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (55 records) |

**Entities:** LINE×808, TEXT×638, INSERT×615, LWPOLYLINE×231, CIRCLE×22, ARC×13, ATTDEF×5, MTEXT×4

**Layers (51):**  
`0`, `I`, `T`, `PKV`, `I1`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `I2`, `E`, `PUP`, `26`, `H`, `P-OTHER`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-PUMP_POS` … +11 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (64):**

  - `MOTOR` (10 entities)
  - `SEK2` (7 entities)
  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `TAKAISKU` (11 entities)
  - `TOIMRAJA` (5 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `POSPRM` (20 entities)
  - `TOIMILVK` (10 entities)
  - `PALJER` (22 entities)
  - `MRS` (9 entities)
  - `PI` (2 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `A$C52093E87` (1 entities)
  - `TASO` (4 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_1201A` (2 entities)
  - `PPI_0504A-45_0` (6 entities)
  - `muutostau` (32 entities)
  - `A$70462` (1 entities)
  - `A$7047C` (1 entities)
  - `A$704A1` (1 entities)
  - … +34 more

**Most-used block inserts:**

  - `PPI_0900A` ×73
  - `PPI_1207A` ×71
  - `P7A1304` ×56
  - `PPI_1100A` ×56
  - `PPI_1000A` ×43
  - `N` ×40
  - `PPI_0102B` ×31
  - `VENT` ×30
  - `PPI_00` ×30
  - `TOIMILV` ×21
  - `TOIMILVK` ×19
  - `MOTOR` ×15
  - `PESUYHDE` ×11
  - `TAKAISKU` ×11
  - `PPI_1302A-25_0` ×11

**Attribute tags & sample values (83 unique tags):**

  - `VENIMI` ×61 — `PESUVENTTIILI`
  - `VEPOSITIO` ×61 — `1005`
  - `VEKOKO` ×61 — `32`
  - `VETYYPPI` ×61 — `003`
  - `LINJA` ×61 — `106`
  - `VEKEMIKAALI` ×61 — `PIG`
  - `VEVALMISTAJA` ×61 — `xx`
  - `IVENIMI` ×40 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×40 — `102`
  - `IVEKOKO` ×40 — `x`
  - `IVETYYPPI` ×40 — `101`
  - `ILINJA` ×40 — `102`
  - `IVEKEMIKAALI` ×40 — `NESTE`
  - `IVEVALMISTAJA` ×40 — `xx`
  - `OSOITE` ×16 — `FRESH WATER`
  - `MOTOR` ×15 — `MOTOR`
  - `MOTORPOS` ×15 — `MOTORPOS`
  - `POWER` ×15 — `POWER`
  - `RPM` ×15 — `RPM`
  - `CURRENT` ×15 — `CURRENT`
  - `DRIVE` ×15 — `DRIVE`
  - `MOUNTED` ×15 — `MOUNTED`
  - `POSITIO` ×5 — `107.1`
  - `LAITE` ×5 — `ECCENTRIC SCREW PUMP`
  - `PAINE` ×5 — `4`
  - `TILAVUUS` ×5 — `100`
  - `GALLONS` ×5 — `25.0`
  - `KEMIKAALI` ×5 — `PIG`
  - `DN1` ×5 — `80`
  - `DN2` ×5 — `80`

**Text entity samples (model space):**

  - `STORAGE SILO` _(layer: T)_
  - `1,5 m` _(layer: T)_
  - `3` _(layer: T)_
  - `9,0 m³/h` _(layer: T)_
  - `PI` _(layer: I)_
  - `150 µm` _(layer: T)_
  - `RF-33` _(layer: T)_
  - `POWDER CONSUMPTION` _(layer: T)_
  - `ABOUT 36 m3/day` _(layer: T)_
  - `2,0 m³/h` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `VIBRATION BOTTOM` _(layer: T)_
  - `STATION` _(layer: LA)_
  - `START / STOP` _(layer: I)_
  - `DUST FILTER` _(layer: I)_
  - `HIGH LEVEL` _(layer: I)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ACANSGDT` (amgdt.shx), `ISOCP` (isocp.shx), `Copyright` (romans.shx), `ROMANS` (romans.shx), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 4. `PCSG028672.02_Dye_brown.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 2733 |
| Entities (model space) | 830 |
| Layers | 49 |
| Block definitions | 35 |
| Unique attribute tags | 78 |
| App ID fingerprint | PCAD ×15 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (22 records) |

**Entities:** TEXT×252, INSERT×248, LINE×217, LWPOLYLINE×92, CIRCLE×9, MTEXT×5, ARC×4, ATTDEF×2

**Layers (49):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `Valmet`, `Valmet_logo_color_green_solid`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-OTHER` … +9 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (33):**

  - `MOTOR` (10 entities)
  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `TAKAISKU` (11 entities)
  - `TOIMRAJA` (5 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `POSPRM` (20 entities)
  - `TOIMILVK` (10 entities)
  - `MRS` (9 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `A$C52093E87` (1 entities)
  - `POSPAD` (16 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - … +3 more

**Most-used block inserts:**

  - `PPI_0900A` ×47
  - `P7A1304` ×23
  - `PPI_1100A` ×23
  - `PPI_1207A` ×19
  - `VENT` ×18
  - `N` ×15
  - `VENTK` ×13
  - `PESUYHDE` ×10
  - `PPI_0102B` ×9
  - `PPI_1000A` ×9
  - `PPI_00` ×9
  - `PPI_1302A-25_0` ×7
  - `TOIMILV` ×6
  - `TAKAISKU` ×6
  - `FRESH WATER` ×4

**Attribute tags & sample values (78 unique tags):**

  - `VENIMI` ×47 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×47 — `1003`
  - `VEKOKO` ×47 — `x`
  - `VETYYPPI` ×47 — `101`
  - `LINJA` ×47 — `103`
  - `VEKEMIKAALI` ×47 — `NESTE`
  - `VEVALMISTAJA` ×47 — `xx`
  - `IVENIMI` ×9 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×9 — `101`
  - `IVEKOKO` ×9 — `x`
  - `IVETYYPPI` ×9 — `101`
  - `ILINJA` ×9 — `101`
  - `IVEKEMIKAALI` ×9 — `NESTE`
  - `IVEVALMISTAJA` ×9 — `xx`
  - `OSOITE` ×6 — `PRESSURE AIR`
  - `POSITIO` ×4 — `101.1`
  - `LAITE` ×4 — `DIAPHGRAM PUMP`
  - `PAINE` ×4 — `4`
  - `TILAVUUS` ×4 — `50`
  - `GALLONS` ×4 — `13.0`
  - `KEMIKAALI` ×4 — `NESTE`
  - `DN1` ×4 — `50`
  - `DN2` ×4 — `50`
  - `VARUSTEET` ×4 — `Punostiiv.vesirengas`
  - `MATERIAALI` ×4 — `AISI 316`
  - `KOODIOSA` ×4 — `PAD050`
  - `VARUSKOODI` ×4 — `W`
  - `MOTOR` ×4 — `MOTOR`
  - `MOTORPOS` ×4 — `MOTORPOS`
  - `POWER` ×4 — `POWER`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `{\C2;About 19 m³/d}` _(layer: PR)_
  - `STAND-BY` _(layer: T)_
  - `TRUCK UNLOADING` _(layer: E)_
  - `150 µm` _(layer: T)_
  - `BACK PLY` _(layer: T)_
  - `TOP PLY` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `LOCAL CONTROL BOX` _(layer: I)_
  - `FOR UNLOADING STATION` _(layer: I)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `Copyright` (romans.shx), `ISOCP` (isocp.shx), `ROMANS` (romans.shx), `Text3_2` (txt.shx)

---

### 5. `PCSG028673.02_Defoamer.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 2404 |
| Entities (model space) | 671 |
| Layers | 49 |
| Block definitions | 33 |
| Unique attribute tags | 74 |
| App ID fingerprint | PCAD ×15 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (20 records) |

**Entities:** TEXT×207, INSERT×196, LINE×175, LWPOLYLINE×76, MTEXT×5, CIRCLE×5, ARC×4, ATTDEF×2

**Layers (49):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `Valmet`, `Valmet_logo_color_green_solid`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-OTHER` … +9 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (31):**

  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `TAKAISKU` (11 entities)
  - `TOIMRAJA` (5 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `TOIMILVK` (10 entities)
  - `MRS` (9 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `POSPMM` (17 entities)
  - `A$C52093E87` (1 entities)
  - `POSPAD` (16 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1000A` (1 entities)
  - … +1 more

**Most-used block inserts:**

  - `PPI_0900A` ×33
  - `P7A1304` ×20
  - `PPI_1100A` ×20
  - `PPI_1207A` ×16
  - `VENT` ×12
  - `PESUYHDE` ×10
  - `N` ×9
  - `PPI_0102B` ×9
  - `PPI_1000A` ×9
  - `PPI_00` ×9
  - `TOIMILV` ×6
  - `TAKAISKU` ×6
  - `VENTK` ×5
  - `PPI_0504A-30_0` ×4
  - `FRESH WATER` ×3

**Attribute tags & sample values (74 unique tags):**

  - `VENIMI` ×33 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×33 — `1003`
  - `VEKOKO` ×33 — `x`
  - `VETYYPPI` ×33 — `101`
  - `LINJA` ×33 — `103`
  - `VEKEMIKAALI` ×33 — `NESTE`
  - `VEVALMISTAJA` ×33 — `xx`
  - `IVENIMI` ×9 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×9 — `101`
  - `IVEKOKO` ×9 — `x`
  - `IVETYYPPI` ×9 — `101`
  - `ILINJA` ×9 — `101`
  - `IVEKEMIKAALI` ×9 — `NESTE`
  - `IVEVALMISTAJA` ×9 — `xx`
  - `OSOITE` ×5 — `PRESSURE AIR`
  - `POSITIO` ×4 — `101.1`
  - `LAITE` ×4 — `DIAPHGRAM PUMP`
  - `PAINE` ×4 — `4`
  - `TILAVUUS` ×4 — `50`
  - `GALLONS` ×4 — `13.0`
  - `KEMIKAALI` ×4 — `NESTE`
  - `DN1` ×4 — `50`
  - `DN2` ×4 — `50`
  - `VARUSTEET` ×4
  - `MATERIAALI` ×4 — `AISI 316`
  - `KOODIOSA` ×4 — `PAD050`
  - `VARUSKOODI` ×4
  - `TEKSTI1` ×2 — `APPROACH FLOW`
  - `TEKSTI2` ×2 — `RESERVE TO BE CLARIFIED`
  - `KAAVIO` ×2 — `PI-DIAGRAM STOD206337`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `{\C2;About 4 m³/d}` _(layer: PR)_
  - `STAND-BY` _(layer: T)_
  - `TRUCK UNLOADING` _(layer: E)_
  - `TOP/BACK PLY` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `4-20 mA` _(layer: T)_
  - `LOCAL CONTROL BOX` _(layer: I)_
  - `FOR UNLOADING STATION` _(layer: I)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `Copyright` (romans.shx), `ISOCP` (isocp.shx), `ROMANS` (romans.shx), `Text3_2` (txt.shx)

---

## OCC_PID  ·  Valmet PS-21

### 6. `STOD206340.10 OCC Pulping line 1.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 5410 |
| Entities (model space) | 3216 |
| Layers | 35 |
| Block definitions | 96 |
| Unique attribute tags | 65 |
| App ID fingerprint | PCAD ×28 | GENIUS ×9 | other: MCAD_NO_VIS, ACATTRIBSERVICES, DESIGNERASSEMBLIES |
| Connectivity | ✅ LIN_FROM/LIN_TO (72 records) |

**Title block fields:**

- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLin
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `INF14`: 10
- `INF1`: 04.03.2022
- `INF2`: JLin
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton paper Mill, United Kingdom
- `PROJECT3`: Shotton OCC
- `DRAWINGID`: STOD206340.10
- `SHEET`: 1/1
- `ARKKI`: A1+
- `LYH`: SHOTTON OCC
- `TITLE1`: OCC Pulping line 1
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×1252, TEXT×1116, INSERT×714, LINE×59, CIRCLE×36, SOLID×20, POLYLINE×9, MTEXT×5

**Layers (35):**  
`0`, `PI0ATT`, `TIETOPISTE`, `P-OTHER`, `P-A-SHEET`, `P-INSTRU`, `P-REJECT`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-COOLING_RAW_WATER`, `P-INSTRPOS_TEXTS`, `P-EQUIPMENT_POS`, `P-PUMP_POS`, `P-LINEPOS`, `P-VALVEPOS`, `P-FLOOR`, `P-WATER`, `P-AIR`, `P-MASS1`, `P-CVPOS`, `P-FAN_POS`, `P-INSTRPOS`, `P-FITTINGS`, `T-A-SHEET`, `P-MOTOR_POS`, `P-TANK_POS`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-RAW_WATER`, `P-DELIVERY_LIMIT`, `P-HATCH`, `P-REVISIONS`, `Defpoints`

**Custom linetypes (8):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `KV` — -- -- -- -- -- -- --
  - `PKV` — __ . __ . __ . __
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium

**Block definitions (96):**

  - `tietopis` (1 entities)
  - `PI41` (17 entities)
  - `PI3164` (3 entities)
  - `tailcut` (11 entities)
  - `NUOLI` (1 entities)
  - `convey3` (8 entities)
  - `lab-vas` (8 entities)
  - `PI0NUOVR` (1 entities)
  - `HCCLENC1` (3 entities)
  - `CTS_INFP` (1 entities)
  - `P7A1173` (4 entities)
  - `P7A1252` (3 entities)
  - `P7A1105` (2 entities)
  - `P7A1333` (5 entities)
  - `P7A1305` (1 entities)
  - `P7A1271` (2 entities)
  - `P7A0200` (3 entities)
  - `P7A0217` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1120` (4 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_1202A` (3 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `CV1F534` (4 entities)
  - `CV1F552` (4 entities)
  - `PR1F66A` (3 entities)
  - `PR1F6B3` (3 entities)
  - … +66 more

**Most-used block inserts:**

  - `PPI_1204A` ×93
  - `P7A1305` ×79
  - `PPI_0900A` ×74
  - `PPI_1100A` ×71
  - `P7A1100` ×63
  - `PPI_1000A` ×50
  - `P7A1304` ×37
  - `PPI_0102B` ×33
  - `PPI_1200A` ×20
  - `P7A1120` ×19
  - `PPI_1302A-25_0` ×17
  - `PPI_1504A-25_0` ×10
  - `CTV_M_F2` ×9
  - `PPI_1205A` ×9
  - `PI41` ×8

**Attribute tags & sample values (65 unique tags):**

  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `JLin`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `MOOPOS` ×8 — `691`
  - `MOOLAIT` ×8
  - `MOOVIRTA` ×8
  - `MOOTEHO` ×8
  - `MOOKIER` ×8
  - `MOOJANN` ×8
  - `MOOMASE` ×8
  - `MOOAS` ×8
  - `MOOKYTK` ×8
  - `MOOVALM` ×8
  - `MOOTOIM` ×8
  - `MOOERI1` ×8
  - `MOOERI2` ×8
  - `MOOLISA` ×8
  - `MOOREV` ×8
  - `TEKSTI1` ×6 — `COOLING WATER`
  - `TEKSTI2` ×6 — `650 kPa`
  - `KAAVIO` ×6 — `PI-DIAGRAM XXX`
  - `INFO` ×5 — `+18.000`
  - `A` ×3 — `10`
  - `INF17` ×2
  - `MRK2` ×1 — `01`
  - `KPL2` ×1
  - `PVM2` ×1 — `29.04.2022`

**Text entity samples (model space):**

  - `PULPER GEAR` _(layer: P-TEXT)_
  - `LUBRICATION UNIT` _(layer: P-TEXT)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `COMPR. AIR` _(layer: P-TEXT)_
  - `R1.0` _(layer: P-SYMB)_
  - `R1.4` _(layer: P-SYMB)_
  - `R1.1` _(layer: P-SYMB)_
  - `R1.5` _(layer: P-SYMB)_
  - `R1.3` _(layer: P-SYMB)_
  - `R1.6` _(layer: P-SYMB)_
  - `R1.7` _(layer: P-SYMB)_
  - `C` _(layer: P-DELIVERY_LIMIT)_
  - `V` _(layer: P-DELIVERY_LIMIT)_
  - `DN200` _(layer: P-TEXT)_
  - `SEALING WATER` _(layer: P-TEXT)_
  - `CLEAR FILTRATE 650 kPa` _(layer: P-TEXT)_
  - `WHITE WATER 300 kPa` _(layer: P-TEXT)_
  - `PULPER HATCH` _(layer: P-TEXT)_
  - `E-STOP` _(layer: P-TEXT)_
  - `CB-xxx` _(layer: P-TEXT)_

**Text styles:** `STANDARD` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `SIMPLEX` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 7. `STOD206341.10 OCC Pulping line 2.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 5464 |
| Entities (model space) | 3247 |
| Layers | 35 |
| Block definitions | 96 |
| Unique attribute tags | 65 |
| App ID fingerprint | PCAD ×28 | GENIUS ×9 | other: MCAD_NO_VIS, ACATTRIBSERVICES, DESIGNERASSEMBLIES |
| Connectivity | ✅ LIN_FROM/LIN_TO (74 records) |

**Title block fields:**

- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLin
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `INF14`: 10
- `INF1`: 04.03.2022
- `INF2`: JLin
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton paper Mill, United Kingdom
- `PROJECT3`: Shotton OCC
- `DRAWINGID`: STOD206341.10
- `SHEET`: 1/1
- `ARKKI`: A1+
- `LYH`: SHOTTON OCC
- `TITLE1`: OCC Pulping line 2
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×1253, TEXT×1138, INSERT×723, LINE×58, CIRCLE×36, SOLID×20, POLYLINE×9, MTEXT×5

**Layers (35):**  
`0`, `PI0ATT`, `TIETOPISTE`, `P-OTHER`, `P-A-SHEET`, `P-INSTRU`, `P-REJECT`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-COOLING_RAW_WATER`, `P-INSTRPOS_TEXTS`, `P-EQUIPMENT_POS`, `P-PUMP_POS`, `P-LINEPOS`, `P-VALVEPOS`, `P-FLOOR`, `P-WATER`, `P-AIR`, `P-MASS1`, `P-CVPOS`, `P-FAN_POS`, `P-INSTRPOS`, `P-FITTINGS`, `T-A-SHEET`, `P-MOTOR_POS`, `P-TANK_POS`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-REVISIONS`, `P-RAW_WATER`, `P-DELIVERY_LIMIT`, `P-HATCH`, `Defpoints`

**Custom linetypes (8):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `KV` — -- -- -- -- -- -- --
  - `PKV` — __ . __ . __ . __
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium

**Block definitions (96):**

  - `tietopis` (1 entities)
  - `PI41` (17 entities)
  - `PI3164` (3 entities)
  - `tailcut` (11 entities)
  - `NUOLI` (1 entities)
  - `convey3` (8 entities)
  - `lab-vas` (8 entities)
  - `PI0NUOVR` (1 entities)
  - `HCCLENC1` (3 entities)
  - `CTS_INFP` (1 entities)
  - `P7A1173` (4 entities)
  - `P7A1252` (3 entities)
  - `P7A1105` (2 entities)
  - `P7A1333` (5 entities)
  - `P7A1305` (1 entities)
  - `P7A1271` (2 entities)
  - `P7A0200` (3 entities)
  - `P7A0217` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1120` (4 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_1202A` (3 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `CV1F534` (4 entities)
  - `CV1F552` (4 entities)
  - `PR1F66A` (3 entities)
  - `PR1F6B3` (3 entities)
  - … +66 more

**Most-used block inserts:**

  - `PPI_1204A` ×98
  - `P7A1305` ×82
  - `PPI_0900A` ×74
  - `PPI_1100A` ×72
  - `P7A1100` ×63
  - `PPI_1000A` ×50
  - `P7A1304` ×37
  - `PPI_0102B` ×33
  - `PPI_1200A` ×20
  - `P7A1120` ×19
  - `PPI_1302A-25_0` ×17
  - `PPI_1504A-25_0` ×10
  - `CTV_M_F2` ×9
  - `PPI_1205A` ×9
  - `PI41` ×8

**Attribute tags & sample values (65 unique tags):**

  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `JLin`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `MOOPOS` ×8 — `691`
  - `MOOLAIT` ×8
  - `MOOVIRTA` ×8
  - `MOOTEHO` ×8
  - `MOOKIER` ×8
  - `MOOJANN` ×8
  - `MOOMASE` ×8
  - `MOOAS` ×8
  - `MOOKYTK` ×8
  - `MOOVALM` ×8
  - `MOOTOIM` ×8
  - `MOOERI1` ×8
  - `MOOERI2` ×8
  - `MOOLISA` ×8
  - `MOOREV` ×8
  - `TEKSTI1` ×6 — `COOLING WATER`
  - `TEKSTI2` ×6 — `650 kPa`
  - `KAAVIO` ×6 — `PI-DIAGRAM XXX`
  - `INFO` ×5 — `+18.000`
  - `A` ×5 — `10`
  - `INF17` ×2
  - `MRK2` ×1 — `01`
  - `KPL2` ×1
  - `PVM2` ×1 — `29.04.2022`

**Text entity samples (model space):**

  - `PULPER GEAR` _(layer: P-TEXT)_
  - `LUBRICATION UNIT` _(layer: P-TEXT)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `COMPR. AIR` _(layer: P-TEXT)_
  - `R1.0` _(layer: P-SYMB)_
  - `R2.4` _(layer: P-SYMB)_
  - `R2.1` _(layer: P-SYMB)_
  - `R2.5` _(layer: P-SYMB)_
  - `R2.3` _(layer: P-SYMB)_
  - `R2.6` _(layer: P-SYMB)_
  - `R2.7` _(layer: P-SYMB)_
  - `C` _(layer: P-DELIVERY_LIMIT)_
  - `V` _(layer: P-DELIVERY_LIMIT)_
  - `DN200` _(layer: P-TEXT)_
  - `SEALING WATER` _(layer: P-TEXT)_
  - `CLEAR FILTRATE 650 kPa` _(layer: P-TEXT)_
  - `WHITE WATER 300 kPa` _(layer: P-TEXT)_
  - `PULPER HATCH` _(layer: P-TEXT)_
  - `E-STOP` _(layer: P-TEXT)_
  - `CB-xxx` _(layer: P-TEXT)_

**Text styles:** `STANDARD` (ISOCP.SHX), `ROMANS` (ROMANS.SHX), `SIMPLEX` (ROMANS.SHX), `ISOCP` (isocp.shx), `ARIALN` (ARIALN.TTF), `ARIAL` (arial.ttf), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx)

---

### 8. `STOD206342.10 OCC cleaning and fractionation.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 12771 |
| Entities (model space) | 9284 |
| Layers | 38 |
| Block definitions | 180 |
| Unique attribute tags | 50 |
| App ID fingerprint | PCAD ×29 | GENIUS ×37 | other: FOCUSPI_1_3, FOCUSPI, MPI_1 |
| Connectivity | ✅ LIN_FROM/LIN_TO (252 records) |

**Title block fields:**

- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLin
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `INF14`: 10
- `INF1`: 31.03.2023
- `INF2`: JLin
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton paper Mill, United Kingdom
- `PROJECT3`: Shotton OCC
- `DRAWINGID`: STOD206342.10
- `SHEET`: 1/1
- `ARKKI`: A1+
- `LYH`: SHOTTON OCC
- `TITLE1`: OCC Cleaning and fractionation
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×3440, LWPOLYLINE×2936, INSERT×2799, SOLID×51, LINE×44, CIRCLE×8, MTEXT×5, HATCH×1

**Layers (38):**  
`0`, `TIETOPISTE`, `AM_0`, `AM_BOR`, `PI6LAIT`, `AM_5`, `P-OTHER`, `P-INSTRU`, `P-REJECT`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS_TEXTS`, `P-A-SHEET`, `P-WATER`, `P-LINEPOS`, `Toimitusrajat`, `P-TANK_POS`, `P-AGITATOR_POS`, `P-PUMP_POS`, `P-EQUIPMENT_POS`, `P-MASS1`, `P-VALVEPOS`, `P-CVPOS`, `P-FITTINGS`, `P-FLOOR`, `P-DELIVERY_LIMIT`, `P-INSTRPOS`, `P-EQUIPMENTS`, `P-WHITE_WATER`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-REVISIONS`, `P-RAW_WATER`, `P-HATCH`, `Defpoints`

**Custom linetypes (21):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `ACISOTGL` — _ _ _ _ _
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `PKV` — __ . __ . __ . __
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained

**Block definitions (177):**

  - `tietopis` (1 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `PI3164` (3 entities)
  - `CLEANER2` (31 entities)
  - `AGIT` (2 entities)
  - `FS-LF1` (79 entities)
  - `Vlk_Pos0` (1 entities)
  - `Vlk_Pos1` (7 entities)
  - `Vlk_Pos2` (7 entities)
  - `Vlk_Pos3` (7 entities)
  - `Vlk_Pos4` (11 entities)
  - `Metso_Balloon` (2 entities)
  - `Vlk_Pos` (6 entities)
  - `CTS_INFP` (1 entities)
  - `P7A1252` (3 entities)
  - `P7A1105` (2 entities)
  - `P7A1305` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `P7A1120` (4 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_1202A` (3 entities)
  - `c-sihti` (45 entities)
  - … +147 more

**Most-used block inserts:**

  - `PPI_0900A` ×359
  - `P7A1305` ×348
  - `PPI_1204A` ×344
  - `PPI_1100A` ×247
  - `PPI_0102B` ×188
  - `PPI_1000A` ×157
  - `P7A1304` ×149
  - `P7A1100` ×135
  - `P7A1105` ×104
  - `P7A1252` ×79
  - `PPI_1200A` ×76
  - `P7A1120` ×74
  - `PRN6088` ×68
  - `P7A1300` ×68
  - `P7A13E8` ×34

**Attribute tags & sample values (50 unique tags):**

  - `A` ×14 — `10`
  - `TEKSTI1` ×12 — `BROKE STORAGE TOWER`
  - `TEKSTI2` ×12 — `35-24P514`
  - `KAAVIO` ×12 — `PI-DIAGRAM: STOD206339`
  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `JLin`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `INFO` ×4 — `+9.500`
  - `INF17` ×2
  - `MRK2` ×1 — `01`
  - `KPL2` ×1
  - `PVM2` ×1 — `29.04.2022`
  - `MUU2` ×1 — `JLin`
  - `TAR2` ×1 — `SStr`
  - `MUUTOS2` ×1 — `Updated`
  - `INF15` ×1
  - `INF14` ×1 — `10`
  - `INF1` ×1 — `31.03.2023`
  - `INF2` ×1 — `JLin`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton OCC`
  - `DRAWINGID` ×1 — `STOD206342.10`

**Text entity samples (model space):**

  - `LC-CLEANING` _(layer: P-TEXT)_
  - `FRACTIONATION` _(layer: P-TEXT)_
  - `LONG FIBER FINE SCREENING` _(layer: P-TEXT)_
  - `C` _(layer: P-DELIVERY_LIMIT)_
  - `V` _(layer: P-DELIVERY_LIMIT)_
  - `COARSE SCREENING` _(layer: P-TEXT)_
  - `R3.1` _(layer: P-TEXT)_
  - `1. STAGE REJECT` _(layer: P-TEXT)_
  - `DN 150` _(layer: P-OTHER)_
  - `DN 500` _(layer: P-OTHER)_
  - `DN 80` _(layer: P-OTHER)_
  - `DN 200` _(layer: P-OTHER)_
  - `DN 100` _(layer: P-OTHER)_
  - `DN 400` _(layer: P-OTHER)_
  - `DN 50` _(layer: P-OTHER)_
  - `DN 250` _(layer: P-OTHER)_
  - `DN 300` _(layer: P-OTHER)_
  - `DN 700` _(layer: P-OTHER)_
  - `SEALING  WATER` _(layer: P-TEXT)_
  - `DEAERATION IN THE` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `SIMPLEX` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ACISOGDT` (ARIALN.TTF), `ACISOTS` (ARIALN.TTF), `ACANSGDT` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ARIAL` (arial.ttf), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx)

---

### 9. `STOD206343.10 OCC Thickening.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 12405 |
| Entities (model space) | 8825 |
| Layers | 47 |
| Block definitions | 191 |
| Unique attribute tags | 92 |
| App ID fingerprint | PCAD ×30 | GENIUS ×8 | other: MCAD_NO_VIS, ACATTRIBSERVICES, DESIGNERASSEMBLIES |
| Connectivity | ✅ LIN_FROM/LIN_TO (258 records) |

**Title block fields:**

- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLin
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `INF14`: 10
- `INF1`: 31.03.2022
- `INF2`: JLin
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton paper Mill, United Kingdom
- `PROJECT3`: Shotton OCC
- `DRAWINGID`: STOD206343.10
- `SHEET`: 1/1
- `ARKKI`: A1+
- `LYH`: SHOTTON OCC
- `TITLE1`: OCC Thickening
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×2972, TEXT×2858, INSERT×2353, LINE×551, ARC×43, SOLID×19, CIRCLE×17, SPLINE×8

**Layers (47):**  
`0`, `PI0ATT`, `AM_BOR`, `TIETOPISTE`, `PI3HVENT`, `pi2vprlin_035`, `Toimitusrajat`, `P-OTHER`, `P-A-SHEET`, `P-INSTRU`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS_TEXTS`, `P-TANK_POS`, `P-PUMP_POS`, `P-AGITATOR_POS`, `P-EQUIPMENT_POS`, `P-LINEPOS`, `P-CVPOS`, `P-VALVEPOS`, `P-MASS1`, `P-AIR`, `P-WATER`, `PI6LAIT`, `pi6teoku`, `P-INSTRPOS`, `P-FITTINGS`, `P-FLOOR`, `P-REJECT`, `P-WHITE_WATER`, `P-EQUIPMENT`, `P-MOTOR_POS`, `P-DELIVERY_LIMIT`, `P-EQUIPMENTS`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-REVISIONS` … +7 more

**Custom linetypes (22):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGL` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `KV` — -- -- -- -- -- -- --
  - `PKV` — __ . __ . __ . __
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained

**Block definitions (190):**

  - `PI3211` (19 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `PI41` (17 entities)
  - `PI3164` (3 entities)
  - `PI0NUOVR` (1 entities)
  - `PI3216` (24 entities)
  - `SCREW PRESS` (24 entities)
  - `CTS_INFP` (1 entities)
  - `P7A1252` (3 entities)
  - `P7A1105` (2 entities)
  - `P7A1305` (1 entities)
  - `P7A1215` (2 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `P7A1120` (4 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `CTV_M_E1` (27 entities)
  - `CTV_M_F2` (15 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_1000A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `P7A1304` (1 entities)
  - `CDI` (35 entities)
  - … +160 more

**Most-used block inserts:**

  - `P7A1305` ×304
  - `PPI_0900A` ×285
  - `PPI_1204A` ×256
  - `PPI_1100A` ×255
  - `P7A1100` ×145
  - `PPI_0102B` ×137
  - `P7A1304` ×124
  - `PPI_1000A` ×117
  - `P7A1105` ×60
  - `PPI_1200A` ×49
  - `P7A1120` ×41
  - `PPI_1205A` ×24
  - `P7A1252` ×20
  - `P7A1300` ×19
  - `PPI_0521A-25_0` ×19

**Attribute tags & sample values (92 unique tags):**

  - `TEKSTI1` ×23 — `SEALING WATER`
  - `TEKSTI2` ×23 — `WHITE WATER`
  - `KAAVIO` ×23 — `PI-DIAGRAM RAU8G02317`
  - `A` ×19 — `TP 005`
  - `INFO` ×12 — `+9.500`
  - `MOOPOS` ×11
  - `MOOLAIT` ×11
  - `MOOVIRTA` ×11
  - `MOOTEHO` ×11
  - `MOOKIER` ×11
  - `MOOJANN` ×11
  - `MOOMASE` ×11
  - `MOOAS` ×11
  - `MOOKYTK` ×11
  - `MOOVALM` ×11
  - `MOOTOIM` ×11
  - `MOOERI1` ×11
  - `MOOERI2` ×11
  - `MOOLISA` ×11
  - `MOOREV` ×11
  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `JLin`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `KVENIMI` ×6 — `VALVE`
  - `KVEPOS` ×6 — `110`
  - `KVETYYP` ×6
  - `KVEDN` ×6

**Text entity samples (model space):**

  - `LONG FIBER THICKENING AND DISPERSING` _(layer: P-TEXT)_
  - `PRODUCTION` _(layer: P-TEXT)_
  - `DISPERGER` _(layer: P-TEXT)_
  - `LUBRICATION` _(layer: P-TEXT)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `SHORT FIBER THICKENING` _(layer: P-TEXT)_
  - `C` _(layer: Toimitusrajat)_
  - `V` _(layer: Toimitusrajat)_
  - `1` _(layer: P-OTHER)_
  - `2` _(layer: P-OTHER)_
  - `3` _(layer: P-OTHER)_
  - `4` _(layer: P-OTHER)_
  - `5` _(layer: P-OTHER)_
  - `6` _(layer: P-OTHER)_
  - `7` _(layer: P-OTHER)_
  - `8` _(layer: P-OTHER)_
  - `9` _(layer: P-OTHER)_
  - `10` _(layer: P-OTHER)_
  - `CLEAR FILTRATE 650 kPa` _(layer: P-TEXT)_
  - `SEALING WATER` _(layer: P-TEXT)_

**Text styles:** `STANDARD` (ISOCP.SHX), `ACISOGDT` (amgdt.shx), `ROMANS` (ROMANS.SHX), `ROMA` (romans.shx), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOCP` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ISO` (ISO.shx), `SIMPLEX` (ROMANS.SHX), `ARIAL` (arial.ttf), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx), `MtXpl_f0890111901_shx` (f0890111901.shx), `MtXpl_Arial` (), `MtXpl_isocp3_shx` (ISOCP3.shx)

---

### 10. `STOD206344.13_OCC Reject handling.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `jani.linden` |
| Objects | 8760 |
| Entities (model space) | 5942 |
| Layers | 37 |
| Block definitions | 120 |
| Unique attribute tags | 50 |
| App ID fingerprint | PCAD ×29 | GENIUS ×20 | other: FOCUSPI_1_3, FOCUSPI, AVE_RENDER |
| Connectivity | ✅ LIN_FROM/LIN_TO (140 records) |

**Title block fields:**

- `MRK`: 12
- `PVM`: 31.10.2024
- `MUU`: JLin
- `TAR`: HSoi
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLin
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `INF14`: 13
- `INF1`: 04.03.2022
- `INF2`: JLin
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton paper Mill, United Kingdom
- `PROJECT3`: Shotton OCC
- `DRAWINGID`: STOD206344.13
- `SHEET`: 1/1
- `ARKKI`: A1+
- `LYH`: SHOTTON OCC
- `TITLE1`: OCC Reject handling
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×2164, LWPOLYLINE×1953, INSERT×1598, LINE×104, MTEXT×50, CIRCLE×35, ARC×33, ELLIPSE×3

**Layers (37):**  
`0`, `P-INSTRU`, `P-REJECT`, `P-WATER`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-OTHER`, `P-ADDITIVE`, `P-AIR`, `P-EQUIPMENT_POS`, `P-PUMP_POS`, `P-TANK_POS`, `P-VALVEPOS`, `P-LINEPOS`, `P-CVPOS`, `P-AGITATOR_POS`, `P-EQUIPMENTS`, `P-INSTRPOS_TEXTS`, `P-A-SHEET`, `PDF_Geometry`, `P-FITTINGS`, `P-FLOOR`, `P-DELIVERY_LIMIT`, `P-REVISIONS`, `T-A-SHEET`, `P-MOTOR_POS`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-FEED_WATER`, `P-WHITE_WATER`, `P-HATCH`, `P-MARKBALL`, `P-SENSOR_POS`, `Defpoints`

**Custom linetypes (6):**

  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `PKV` — __ . __ . __ . __

**Block definitions (120):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `PPI_1204A` (6 entities)
  - `C-908D` (8 entities)
  - `P7A1304` (1 entities)
  - `PPI_0700A-25` (4 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_1000A` (1 entities)
  - `PCAD_INF` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PR2A1C3` (3 entities)
  - `P7A1252` (3 entities)
  - `PPI_1320A-25` (6 entities)
  - `PPI_1200A` (1 entities)
  - `P7A1105` (2 entities)
  - `CV303F9` (4 entities)
  - `P7A1212` (2 entities)
  - `CTV_M_E1` (27 entities)
  - `CTV_M_F2` (15 entities)
  - `PPI_0802A-25` (4 entities)
  - `A$14967` (4 entities)
  - `P7A1106` (5 entities)
  - `P7A1A16` (10 entities)
  - `P7A1322` (3 entities)
  - `lab-vas` (8 entities)
  - `P7A13E8` (4 entities)
  - `P7A13B3` (21 entities)
  - … +90 more

**Most-used block inserts:**

  - `PPI_1204A` ×236
  - `P7A1305` ×228
  - `PPI_0900A` ×152
  - `PPI_1100A` ×138
  - `PPI_0102B` ×87
  - `P7A1304` ×84
  - `P7A1100` ×81
  - `P7A13E8` ×48
  - `PPI_1202A` ×40
  - `PPI_1320A-25` ×35
  - `PPI_1200A` ×32
  - `PPI_1504A-25` ×27
  - `p7a1370` ×26
  - `PPI_1000A` ×22
  - `C-908D` ×20

**Attribute tags & sample values (50 unique tags):**

  - `TEKSTI1` ×33 — `SEC.PULPER JUNK BOX`
  - `TEKSTI2` ×33 — `PULPER STATION 1`
  - `KAAVIO` ×33 — `PI-DIAGRAM STOD206340`
  - `MRK` ×12 — `13`
  - `KPL` ×12
  - `PVM` ×12 — `4.6.2025`
  - `MUU` ×12 — `JLin`
  - `TAR` ×12 — `KVil`
  - `MUUTOS` ×12 — `Preliminary`
  - `A` ×7 — `TP 008`
  - `INFO` ×3 — `+`
  - `INF17` ×2
  - `MRK2` ×1 — `01`
  - `KPL2` ×1
  - `PVM2` ×1 — `29.04.2022`
  - `MUU2` ×1 — `JLin`
  - `TAR2` ×1 — `SStr`
  - `MUUTOS2` ×1 — `Updated`
  - `INF15` ×1
  - `INF14` ×1 — `13`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `JLin`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton OCC`
  - `DRAWINGID` ×1 — `STOD206344.13`

**Text entity samples (model space):**

  - `SAND AND GRIT REJECTS` _(layer: P-TEXT)_
  - `PULPING STATION 1` _(layer: P-TEXT)_
  - `REJECT` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `PULPING STATION 2` _(layer: P-TEXT)_
  - `CONVEYOR 1` _(layer: P-TEXT)_
  - `EMERGENCY STOP` _(layer: P-TEXT)_
  - `SHREDDER 3` _(layer: P-TEXT)_
  - `SEALING WATER` _(layer: P-TEXT)_
  - `HYDRAULIC UNIT` _(layer: P-TEXT)_
  - `SHEDDER 2` _(layer: P-TEXT)_
  - `R3.1` _(layer: P-OTHER)_
  - `R2.4, R2.5` _(layer: P-OTHER)_
  - `R2.1` _(layer: P-OTHER)_
  - `R1.2, R1.3` _(layer: P-OTHER)_
  - `R2.2, R2.3` _(layer: P-OTHER)_
  - `R3.4` _(layer: P-OTHER)_
  - `R1.7` _(layer: P-OTHER)_
  - `R2.7` _(layer: P-OTHER)_

**Text styles:** `STANDARD` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ARIAL` (arial.ttf), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx)

---

### 11. `STOD212164.03 OCC Utility Pipe Routes.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 195065 |
| Entities (model space) | 74684 |
| Layers | 124 |
| Block definitions | 328 |
| Unique attribute tags | 36 |
| App ID fingerprint | PCAD ×22 | GENIUS ×29 | other: CTS_INFO, CTS_SHEET, CTS_TXT |
| Connectivity | ✅ LIN_FROM/LIN_TO (111 records) |

**Title block fields:**

- `INF14`: 03
- `INF1`: 20.01.2023
- `INF2`: KLei
- `INF3`: 20.01.2023
- `INF4`: JLin
- `INF5`: 20.01.2023
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton OCC
- `DRAWINGID`: STOD212164.03
- `SHEET`: 1/1
- `ARKKI`: A0+
- `LYH`: SHOTTON OCC
- `TITLE1`: OCC UTILITY PIPE ROUTES
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C

**Entities:** LINE×36955, LWPOLYLINE×19727, ARC×5851, SPLINE×4702, ELLIPSE×4331, TEXT×1137, INSERT×872, CIRCLE×744

**Layers (124):**  
`0`, `T-A-SHEET`, `PIPING`, `TEXT`, `Dimensions`, `Levels`, `Floor Loading`, `T-LINES`, `T-EQUIP`, `T-LinesNro`, `_Existing Building`, `T-EQUIPMENT`, `AM_0`, `AM_4`, `1`, `M_EQU_TH`, `YTTERG-LMEK0`, `MECHEQPT`, `Tanks & Vessels`, `Platforms`, `T-DIM`, `T-FOUNDATION`, `T-TANKS`, `AM_7`, `AM_8`, `AM_3`, `MEK0-7`, `MEK0-0`, `GEV_FROZEN`, `CENN`, `0N`, `7AN`, `BHII`, `4`, `7A`, `7`, `CON1`, `THLI`, `BHMM`, `PESÄ-0` … +84 more

**Custom linetypes (36):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `DASH3` — DASH3
  - `DASH4` — DASH4
  - `DDASH1` — DDASH1
  - `GTCHAIN` — GTCHAIN
  - `PHANTOMX2` — ____________    ____    ____    ____________   
  - `DASHDOTX2` — Dash dot (2x) ____  .  ____  .  ____  .  ___
  - `solid` — solid
  - `voith_solid_0_18_1_0_010000` — voith_solid_0_18_1_0_010000
  - `AM_ISO02W050` — ValmetIso __ __ __ __ __ __ __ __ __ __ __
  - `GEN3A` —  - - - - -
  - `DASH_DOT` — Dash dot _._._._._._._._._._._._._._._.
  - `BORDER` — __ __ . __ __ . __ __ . __ __ . __ __ . __ __
  - `AM_ISO08W050x2` — MetsoIso __ . __ . __ . __ . __ . __
  - `AM_ISO08W050` — MetsoIso ____ . ____ . ____ . ____ . ____ . ___
  - `AM_ISO02W050x2` — ValmetIso _ _ _ _ _ _ _ _ _ _ _ _
  - `CHAIN` — Chain ____ _ ____ _ ____ _ ____ _ ____ _ ____
  - `GEN7` — ____ . ____ . ____ . ____ . ____ . ____ . ____

**Block definitions (328):**

  - `Syöttöpää HC250 päältä` (37 entities)
  - `RP DN100 HCb 250` (80 entities)
  - `Iso nuoli` (5 entities)
  - `A$361F9` (38 entities)
  - `A$4BD89` (2536 entities)
  - `A$4DBD8` (1473 entities)
  - `A$4F9F4` (1473 entities)
  - `JAPESAPK_1392` (163 entities)
  - `PUSKIN_M10_4443` (13 entities)
  - `A$C0EDD0CE8` (90 entities)
  - `A$C6C4F6286` (31 entities)
  - `A$C39927DE1` (238 entities)
  - `A$C3E4F3939` (42 entities)
  - `A$C2DD217C9` (8 entities)
  - `A$C009D254E` (1 entities)
  - `A$C1CA34307` (45 entities)
  - `Syöttöpää HC370 päältä` (45 entities)
  - `Kilvet Pä` (21 entities)
  - `A$8C845` (179 entities)
  - `A$8C9FA` (84 entities)
  - `A$8CEB4` (94 entities)
  - `A$8CFD8` (94 entities)
  - `A$CB569` (1 entities)
  - `VALMET_R_OTS` (409 entities)
  - `LG-FMPCH` (7 entities)
  - `FMS_T70_E` (29 entities)
  - `CTS_INFP` (1 entities)
  - `CTS_INFT` (1 entities)
  - `A$C4FD74240` (112 entities)
  - `A$C80f85b92` (14 entities)
  - … +298 more

**Most-used block inserts:**

  - `P7A1100` ×193
  - `PPI_0900A` ×191
  - `P7A1304` ×86
  - `PPI_1100A` ×83
  - `RPALLO0` ×27
  - `A$CEA16CC20_X_X_X` ×24
  - `PPI_1302A-25_0` ×16
  - `PPI_0700A-25_0` ×13
  - `A$FE234_X_X_X` ×10
  - `A$BA226_X_X_X` ×10
  - `PPI_052AA-25_0` ×10
  - `A$361F9` ×8
  - `A$FE3F4_X_X_X` ×6
  - `A$CBF6E_X_X_X` ×4
  - `A$C3058ED67_X_X_X` ×4

**Attribute tags & sample values (36 unique tags):**

  - `A` ×27 — `2.2`
  - `INF17` ×2
  - `INFO` ×2 — `+20.650`
  - `NAME` ×2 — `/ME-00108540_CFXMain_2023-01-13`
  - `INF15` ×1
  - `INF14` ×1 — `03`
  - `INF1` ×1 — `20.01.2023`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `20.01.2023`
  - `INF4` ×1 — `JLin`
  - `INF5` ×1 — `20.01.2023`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton OCC`
  - `DRAWINGID` ×1 — `STOD212164.03`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A0+`
  - `LYH` ×1 — `SHOTTON OCC`
  - `TITLE1` ×1 — `OCC UTILITY PIPE ROUTES`
  - `TITLE2` ×1
  - `REFERENCE` ×1
  - `SUPERSEDES` ×1
  - `WORK` ×1
  - `CAD` ×1 — `AutoCAD`
  - `PROCUCT` ×1 — `PI-DIAGRAM`
  - `SCALE` ×1
  - `WGHT` ×1
  - `DESD` ×1
  - `DESDDATE` ×1

**Text entity samples (model space):**

  - `{\l\fArial|b0|i0;\T1;Document\~status}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Key}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Pcs}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Date}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Name}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Checked}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Changes}` _(layer: T-A-SHEET)_
  - `CERTIFIED 22.12.2023` _(layer: T-A-SHEET)_
  - `Updated` _(layer: T-A-SHEET)_
  - `00` _(layer: T-A-SHEET)_
  - `20.01.2023` _(layer: T-A-SHEET)_
  - `KLei` _(layer: T-A-SHEET)_
  - `JLin` _(layer: T-A-SHEET)_
  - `\P` _(layer: T-A-SHEET)_
  - `SEALING WATER` _(layer: T-POS)_
  - `FRESH WATER` _(layer: T-POS)_
  - `MILL AIR` _(layer: T-POS)_
  - `INSTRUMENT AIR` _(layer: T-POS)_
  - `COOLING WATER PM TO OCC` _(layer: T-POS)_
  - `SPRING-CLOSED` _(layer: P-TEXT)_

**Text styles:** `Standard` (txt), `ISOCP` (isocp.shx), `ARIAL` (arial.ttf), `ARIALN` (ARIALN.TTF), `SFS` (TXT.SHX), `HTX11` (O8111901), `HTX24` (FLB11203), `NBM` (romans.shx), `f0890111901` (f0890111901), `XT03_5` (isocp.shx), `STANDARD2` (romans.shx), `SLDTEXTSTYLE0` (GOTHICB.TTF), `ROMANS` (ROMANS.SHX), `AUDIT_D_220106164814-0` (ARIALN.TTF), `PDF Arial` (arial.ttf)

---

## PM03_PID  ·  Valmet PS-21 / Flow-diagram sub-type

### 12. `PCSG028667.02_sizing_agent.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 2390 |
| Entities (model space) | 666 |
| Layers | 49 |
| Block definitions | 31 |
| Unique attribute tags | 81 |
| App ID fingerprint | PCAD ×15 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (16 records) |

**Entities:** TEXT×207, LINE×187, INSERT×185, LWPOLYLINE×68, CIRCLE×8, ARC×4, MTEXT×4, ATTDEF×2

**Layers (49):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-OTHER` … +9 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (29):**

  - `MOTOR` (10 entities)
  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `POSPRM` (20 entities)
  - `TOIMILVK` (10 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `A$C52093E87` (1 entities)
  - `POSPAD` (16 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-45_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1000A` (1 entities)
  - `PPI_00` (1 entities)

**Most-used block inserts:**

  - `PPI_0900A` ×33
  - `PPI_1207A` ×19
  - `P7A1304` ×17
  - `PPI_1100A` ×17
  - `VENT` ×12
  - `VENTK` ×11
  - `PESUYHDE` ×10
  - `PPI_1000A` ×9
  - `N` ×7
  - `PPI_0102B` ×7
  - `PPI_00` ×7
  - `TOIMILV` ×6
  - `PPI_0504A-45_0` ×4
  - `POSPRM` ×3
  - `MOTOR` ×3

**Attribute tags & sample values (81 unique tags):**

  - `VENIMI` ×33 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×33 — `1003`
  - `VEKOKO` ×33 — `x`
  - `VETYYPPI` ×33 — `101`
  - `LINJA` ×33 — `103`
  - `VEKEMIKAALI` ×33 — `NESTE`
  - `VEVALMISTAJA` ×33 — `xx`
  - `IVENIMI` ×9 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×9 — `31`
  - `IVEKOKO` ×9 — `x`
  - `IVETYYPPI` ×9 — `101`
  - `ILINJA` ×9 — `31`
  - `IVEKEMIKAALI` ×9 — `NESTE`
  - `IVEVALMISTAJA` ×9 — `xx`
  - `POSITIO` ×4 — `17.1`
  - `LAITE` ×4 — `ECCENTRIC SCREW PUMP`
  - `PAINE` ×4 — `4`
  - `TILAVUUS` ×4 — `100`
  - `GALLONS` ×4 — `25.0`
  - `KEMIKAALI` ×4 — `PIG`
  - `DN1` ×4 — `80`
  - `DN2` ×4 — `80`
  - `VARUSTEET` ×4 — `Punostiiv.vesirengas`
  - `MATERIAALI` ×4 — `AISI 316`
  - `KOODIOSA` ×4 — `PRA100`
  - `VARUSKOODI` ×4 — `W`
  - `MOTOR` ×3 — `MOTOR`
  - `MOTORPOS` ×3 — `MOTORPOS`
  - `POWER` ×3 — `POWER`
  - `RPM` ×3 — `RPM`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `{\C2;About 6,0 m³/d}` _(layer: PR)_
  - `STAND-BY` _(layer: T)_
  - `150 µm` _(layer: T)_
  - `TRUCK UNLOADING` _(layer: E)_
  - `OR CONTAINER` _(layer: E)_
  - `EQUIPMENT AND MATERIALS, PURCHASER DELIVERY` _(layer: T)_
  - `FIELD INSTRUMENTATION, VALMET DELIVERY` _(layer: I)_
  - `EQUIPMENT, VALMET DELIVERY` _(layer: Valmet)_
  - `LOCAL CONTROL BOX` _(layer: I)_
  - `FOR UNLOADING STATION` _(layer: I)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `35-38P501` _(layer: P-PUMP_POS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `Copyright` (romans.shx), `ROMANS` (ROMANS.SHX), `ISOCP` (ARIALN.TTF), `Text3_2` (txt.shx)

---

### 13. `PCSG028668.02_PAC.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 2222 |
| Entities (model space) | 578 |
| Layers | 48 |
| Block definitions | 30 |
| Unique attribute tags | 74 |
| App ID fingerprint | PCAD ×15 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (17 records) |

**Entities:** LINE×177, TEXT×171, INSERT×154, LWPOLYLINE×59, MTEXT×5, CIRCLE×5, ARC×4, ATTDEF×2

**Layers (48):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-OTHER` … +8 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (28):**

  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `TOIMILVK` (10 entities)
  - `WECOSOITE 2` (7 entities)
  - `FRESH WATER` (7 entities)
  - `VAROV` (19 entities)
  - `POSPMM` (17 entities)
  - `A$C52093E87` (1 entities)
  - `POSPAD` (16 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1000A` (1 entities)
  - `PPI_00` (1 entities)

**Most-used block inserts:**

  - `PPI_0900A` ×25
  - `P7A1304` ×17
  - `PPI_1100A` ×17
  - `PPI_1207A` ×14
  - `PESUYHDE` ×10
  - `PPI_1000A` ×9
  - `VENT` ×8
  - `N` ×7
  - `TOIMILV` ×6
  - `VENTK` ×5
  - `PPI_0102B` ×5
  - `PPI_00` ×5
  - `PPI_0504A-30_0` ×4
  - `POSPMM` ×3
  - `TOIMILVK` ×3

**Attribute tags & sample values (74 unique tags):**

  - `VENIMI` ×25 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×25 — `1001`
  - `VEKOKO` ×25 — `x`
  - `VETYYPPI` ×25 — `101`
  - `LINJA` ×25 — `101`
  - `VEKEMIKAALI` ×25 — `NESTE`
  - `VEVALMISTAJA` ×25 — `xx`
  - `IVENIMI` ×9 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×9 — `101`
  - `IVEKOKO` ×9 — `x`
  - `IVETYYPPI` ×9 — `101`
  - `ILINJA` ×9 — `101`
  - `IVEKEMIKAALI` ×9 — `NESTE`
  - `IVEVALMISTAJA` ×9 — `xx`
  - `POSITIO` ×4 — `101.1`
  - `LAITE` ×4 — `DIAPHGRAM PUMP`
  - `PAINE` ×4 — `4`
  - `TILAVUUS` ×4 — `50`
  - `GALLONS` ×4 — `13.0`
  - `KEMIKAALI` ×4 — `NESTE`
  - `DN1` ×4 — `50`
  - `DN2` ×4 — `50`
  - `VARUSTEET` ×4
  - `MATERIAALI` ×4 — `AISI 316`
  - `KOODIOSA` ×4 — `PAD050`
  - `VARUSKOODI` ×4
  - `OSOITE` ×3 — `PRESSURE AIR`
  - `TEKSTI1` ×2 — `SUPPLY SYSTEM`
  - `TEKSTI2` ×2 — `BOTTOM`
  - `KAAVIO` ×2 — `PI-DIAGRAM PCSG028678`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `{\C2;About 2 m³/d}` _(layer: PR)_
  - `{\C2;FRP PLASTIC}` _(layer: PR)_
  - `TRUCK UNLOADING` _(layer: E)_
  - `OR CONTAINER` _(layer: E)_
  - `EQUIPMENT AND MATERIALS, PURCHASER DELIVERY` _(layer: T)_
  - `FIELD INSTRUMENTATION, VALMET DELIVERY` _(layer: I)_
  - `EQUIPMENT, VALMET DELIVERY` _(layer: Valmet)_
  - `4-20 mA` _(layer: T)_
  - `LOCAL CONTROL BOX` _(layer: I)_
  - `FOR UNLOADING STATION` _(layer: I)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `35-39P501` _(layer: P-PUMP_POS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `Copyright` (romans.shx), `ROMANS` (ROMANS.SHX), `ISOCP` (ARIALN.TTF), `Text3_2` (txt.shx)

---

### 14. `PCSG028669.02_Defoamer_and_biocide.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 2466 |
| Entities (model space) | 785 |
| Layers | 46 |
| Block definitions | 25 |
| Unique attribute tags | 73 |
| App ID fingerprint | PCAD ×19 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (17 records) |

**Entities:** LINE×332, TEXT×197, INSERT×169, LWPOLYLINE×76, SPLINE×4, MTEXT×3, ARC×2, ATTDEF×2

**Layers (46):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `P-OTHER`, `P-PUMP_POS`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de` … +6 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (23):**

  - `TOIMILV` (13 entities)
  - `VENT` (11 entities)
  - `VENTK` (8 entities)
  - `PESUYHDE` (12 entities)
  - `VAROV` (19 entities)
  - `POSPMM` (17 entities)
  - `A$C52093E87` (1 entities)
  - `VENTTIILI` (4 entities)
  - `KASIV` (6 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_00` (1 entities)
  - `PPI_1000A` (1 entities)

**Most-used block inserts:**

  - `PPI_0900A` ×36
  - `P7A1304` ×18
  - `PPI_1100A` ×18
  - `PESUYHDE` ×16
  - `PPI_1207A` ×12
  - `VENTK` ×8
  - `VENT` ×8
  - `PPI_0102B` ×8
  - `PPI_00` ×8
  - `POSPMM` ×6
  - `PPI_0504A-30_0` ×6
  - `TOIMILV` ×4
  - `VAROV` ×4
  - `C-85D9` ×4
  - `PPI_1000A` ×4

**Attribute tags & sample values (73 unique tags):**

  - `VENIMI` ×36 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×36 — `1001`
  - `VEKOKO` ×36 — `x`
  - `VETYYPPI` ×36 — `101`
  - `LINJA` ×36 — `101`
  - `VEKEMIKAALI` ×36 — `NESTE`
  - `VEVALMISTAJA` ×36 — `xx`
  - `POSITIO` ×6 — `801.1`
  - `LAITE` ×6 — `DOSING PUMP`
  - `PAINE` ×6 — `4.0`
  - `TILAVUUS` ×6 — `1.5`
  - `GALLONS` ×6 — `0.4`
  - `KEMIKAALI` ×6 — `BIOCIDE`
  - `DN1` ×6 — `15`
  - `DN2` ×6 — `15`
  - `VARUSTEET` ×6
  - `MATERIAALI` ×6 — `AISI 316`
  - `KOODIOSA` ×6 — `PMM1.5`
  - `VARUSKOODI` ×6
  - `IVENIMI` ×4 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×4 — `31`
  - `IVEKOKO` ×4 — `x`
  - `IVETYYPPI` ×4 — `101`
  - `ILINJA` ×4 — `31`
  - `IVEKEMIKAALI` ×4 — `NESTE`
  - `IVEVALMISTAJA` ×4 — `xx`
  - `TEKSTI1` ×4 — `SUPPLY SYSTEM`
  - `TEKSTI2` ×4 — `TOP`
  - `KAAVIO` ×4 — `PI-DIAGRAM PCSG028678`
  - `PRODUCT` ×1 — `PCS`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `SAFETY BUND` _(layer: T)_
  - `CONTAINER` _(layer: E)_
  - `BIOCIDE` _(layer: E)_
  - `100 %%%` _(layer: E)_
  - `DEFOAMER` _(layer: E)_
  - `EQUIPMENT AND MATERIALS, PURCHASER DELIVERY` _(layer: T)_
  - `FIELD INSTRUMENTATION, VALMET DELIVERY` _(layer: I)_
  - `EQUIPMENT, VALMET DELIVERY` _(layer: Valmet)_
  - `4-20 mA` _(layer: T)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `35-40P501` _(layer: P-PUMP_POS)_
  - `10 lph` _(layer: P-PUMP_POS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ACANSGDT` (amgdt.shx), `ROMANS` (ROMANS.SHX), `Copyright` (romans.shx), `ISOCP` (ARIALN.TTF), `Text3_2` (txt.shx)

---

### 15. `PCSG028674.02_Biocide and hypochloride.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kai.kuoppa` |
| Objects | 1961 |
| Entities (model space) | 471 |
| Layers | 48 |
| Block definitions | 40 |
| Unique attribute tags | 75 |
| App ID fingerprint | PCAD ×15 | other: RAK, ACAUTHENVIRON, GradientColor1ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (9 records) |

**Entities:** LINE×220, TEXT×99, INSERT×95, LWPOLYLINE×30, ARC×9, CIRCLE×7, MTEXT×6, SPLINE×2

**Layers (48):**  
`0`, `I`, `T`, `PKV`, `RA`, `HY`, `LO`, `PR`, `VEP`, `LAP`, `E`, `PUP`, `26`, `KV`, `L`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-OTHER`, `P-PUMP_POS`, `P-TANK_POS`, `P-EQUIPMENT_POS` … +8 more

**Custom linetypes (3):**

  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 

**Block definitions (40):**

  - `MOTOR` (10 entities)
  - `VENT` (11 entities)
  - `N` (1 entities)
  - `K` (6 entities)
  - `VENTK` (8 entities)
  - `PESUYHDE` (12 entities)
  - `KASIV` (6 entities)
  - `TAKAISKU` (11 entities)
  - `A$C52093E87` (1 entities)
  - `POSPKM` (16 entities)
  - `VS` (8 entities)
  - `FRESH WATER` (7 entities)
  - `VENTTIILI` (4 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_1302A-30_0` (4 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_00` (1 entities)
  - `P7A1214` (2 entities)
  - … +10 more

**Most-used block inserts:**

  - `PPI_0900A` ×10
  - `P7A1304` ×9
  - `PPI_1100A` ×9
  - `N` ×8
  - `PPI_1207A` ×7
  - `VENTK` ×4
  - `PPI_1000A` ×4
  - `VENT` ×3
  - `PPI_0102B` ×3
  - `PPI_00` ×3
  - `P7A1372` ×3
  - `K` ×2
  - `PESUYHDE` ×2
  - `FRESH WATER` ×2
  - `P7A1214` ×2

**Attribute tags & sample values (75 unique tags):**

  - `VENIMI` ×10 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×10 — `1009`
  - `VEKOKO` ×10 — `x`
  - `VETYYPPI` ×10 — `101`
  - `LINJA` ×10 — `107`
  - `VEKEMIKAALI` ×10 — `NESTE`
  - `VEVALMISTAJA` ×10 — `xx`
  - `A` ×3 — `02`
  - `OSOITE` ×2 — `WARM WATER`
  - `MOTOR` ×1 — `MOTOR`
  - `MOTORPOS` ×1 — `MOTORPOS`
  - `POWER` ×1 — `POWER`
  - `RPM` ×1 — `RPM`
  - `CURRENT` ×1 — `CURRENT`
  - `DRIVE` ×1 — `DRIVE`
  - `MOUNTED` ×1 — `MOUNTED`
  - `POSITIO` ×1 — `101.1`
  - `LAITE` ×1 — `CENTRIFUGAL PUMP`
  - `PAINE` ×1 — `4`
  - `TILAVUUS` ×1 — `300`
  - `GALLONS` ×1 — `75.0`
  - `KEMIKAALI` ×1 — `NESTE`
  - `DN1` ×1 — `125`
  - `DN2` ×1 — `125`
  - `VARUSTEET` ×1 — `Dynaseal-tiiviste`
  - `MATERIAALI` ×1 — `AISI 316`
  - `KOODIOSA` ×1 — `PKK300`
  - `VARUSKOODI` ×1 — `D`
  - `PRODUCT` ×1 — `PCS`
  - `SUBPROJECT_2` ×1

**Text entity samples (model space):**

  - `DOSING UNIT` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `{\C2;About 2 m³/d}` _(layer: PR)_
  - `{\C2;FRP PLASTIC}` _(layer: PR)_
  - `SAFETY BUND` _(layer: T)_
  - `CONTAINER` _(layer: E)_
  - `BIOCIDE` _(layer: E)_
  - `100 %%%` _(layer: E)_
  - `LOCAL CONTROL BOX` _(layer: I)_
  - `FOR UNLOADING STATION` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `35-46P501` _(layer: P-PUMP_POS)_
  - `400 lpm` _(layer: P-PUMP_POS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `Copyright` (romans.shx), `ROMANS` (ROMANS.SHX), `ISOCP` (isocp.shx), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 16. `PCSG028675.03_Biocide_and_hypochloride_dosing.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 2704 |
| Entities (model space) | 629 |
| Layers | 45 |
| Block definitions | 50 |
| Unique attribute tags | 82 |
| App ID fingerprint | PCAD ×15 | other: RAK, ACAUTHENVIRON, GradientColor1ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (12 records) |

**Entities:** LINE×226, INSERT×188, TEXT×140, LWPOLYLINE×69, MTEXT×4, ATTDEF×2

**Layers (45):**  
`0`, `I`, `T`, `PKV`, `RA`, `HY`, `LO`, `PR`, `VEP`, `LAP`, `PUP`, `26`, `L`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-OTHER`, `P-PUMP_POS`, `P-TANK_POS`, `P-EQUIPMENT_POS`, `P-INSTRPOS_TEXTS`, `P-LINEPOS` … +5 more

**Custom linetypes (2):**

  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __

**Block definitions (50):**

  - `MOTOR` (10 entities)
  - `VENT` (11 entities)
  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `K` (6 entities)
  - `VENTK` (8 entities)
  - `PESUYHDE` (12 entities)
  - `TAKAISKU` (11 entities)
  - `MRS` (9 entities)
  - `TOIMILVK` (10 entities)
  - `POSPMM` (17 entities)
  - `VAROV` (19 entities)
  - `POSPKM` (16 entities)
  - `HYO` (7 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `A$D973` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `A$E0BF` (1 entities)
  - … +20 more

**Most-used block inserts:**

  - `PPI_0900A` ×22
  - `PPI_1207A` ×20
  - `VENT` ×14
  - `PESUYHDE` ×14
  - `PPI_0102B` ×13
  - `P7A1304` ×11
  - `PPI_1100A` ×11
  - `N` ×10
  - `C-85D9` ×8
  - `TOIMILV` ×7
  - `TOIMILVK` ×6
  - `P7A1372` ×6
  - `VAROV` ×4
  - `MOTOR` ×3
  - `PPI_0504A-30_0` ×3

**Attribute tags & sample values (82 unique tags):**

  - `VENIMI` ×36 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×36 — `1004`
  - `VEKOKO` ×36 — `x`
  - `VETYYPPI` ×36 — `101`
  - `LINJA` ×36 — `1020`
  - `VEKEMIKAALI` ×36 — `NESTE`
  - `VEVALMISTAJA` ×36 — `xx`
  - `IVENIMI` ×13 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×13 — `103`
  - `IVEKOKO` ×13 — `x`
  - `IVETYYPPI` ×13 — `101`
  - `ILINJA` ×13 — `101`
  - `IVEKEMIKAALI` ×13 — `NESTE`
  - `IVEVALMISTAJA` ×13 — `xx`
  - `TEKSTI1` ×8 — `BIOCIDE AND HYPO.`
  - `TEKSTI2` ×8 — `SODIUM HYPOCHLORIDE`
  - `KAAVIO` ×8 — `PI-DIAGRAM PCSG028674`
  - `A` ×6 — `03`
  - `MOTOR` ×3 — `MOTOR`
  - `MOTORPOS` ×3 — `MOTORPOS`
  - `POWER` ×3 — `POWER`
  - `RPM` ×3 — `RPM`
  - `CURRENT` ×3 — `CURRENT`
  - `DRIVE` ×3 — `DRIVE`
  - `MOUNTED` ×3 — `MOUNTED`
  - `POSITIO` ×3 — `101.1`
  - `LAITE` ×3 — `CENTRIFUGAL PUMP`
  - `PAINE` ×3 — `4`
  - `TILAVUUS` ×3 — `300`
  - `GALLONS` ×3 — `75.0`

**Text entity samples (model space):**

  - `4-20 mA` _(layer: T)_
  - `DAMPENER` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `QI` _(layer: I)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `35-47T601` _(layer: P-TANK_POS)_
  - `WATER TANK` _(layer: P-TANK_POS)_
  - `2.1 m3` _(layer: P-TANK_POS)_
  - `35-47-003` _(layer: P-VALVEPOS)_
  - `001-40` _(layer: P-VALVEPOS)_
  - `35-47-004` _(layer: P-VALVEPOS)_
  - `080-25` _(layer: P-VALVEPOS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `Copyright` (romans.shx), `ISOCP` (isocp.shx), `ROMANS` (romans.shx), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 17. `PCSG028676.03_Micropolymer_and_wire_conditioning.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 2871 |
| Entities (model space) | 897 |
| Layers | 50 |
| Block definitions | 35 |
| Unique attribute tags | 75 |
| App ID fingerprint | PCAD ×19 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (30 records) |

**Entities:** TEXT×261, INSERT×257, LINE×256, LWPOLYLINE×115, MTEXT×4, ARC×2, ATTDEF×2

**Layers (50):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `P-OTHER`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de` … +10 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (33):**

  - `TOIMILV` (13 entities)
  - `N` (1 entities)
  - `VENT` (11 entities)
  - `TAKAISKU` (11 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `MRS` (9 entities)
  - `FRESH WATER` (7 entities)
  - `VAROV` (19 entities)
  - `POSPMM` (17 entities)
  - `A$C52093E87` (1 entities)
  - `A$C15FA388F` (3 entities)
  - `KASIV` (6 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `A$6C650` (1 entities)
  - `A$6C6E6` (12 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - … +3 more

**Most-used block inserts:**

  - `PPI_0900A` ×58
  - `PPI_1100A` ×29
  - `P7A1304` ×28
  - `PESUYHDE` ×18
  - `VENT` ×16
  - `PPI_0102B` ×12
  - `PPI_1207A` ×12
  - `PPI_00` ×12
  - `VENTK` ×10
  - `N` ×8
  - `POSPMM` ×6
  - `PPI_0504A-30_0` ×6
  - `VAROV` ×4
  - `TAKAISKU` ×4
  - `K` ×4

**Attribute tags & sample values (75 unique tags):**

  - `VENIMI` ×52 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×52 — `1001`
  - `VEKOKO` ×52 — `x`
  - `VETYYPPI` ×52 — `101`
  - `LINJA` ×52 — `101`
  - `VEKEMIKAALI` ×52 — `NESTE`
  - `VEVALMISTAJA` ×52 — `xx`
  - `POSITIO` ×6 — `801.1`
  - `LAITE` ×6 — `DOSING PUMP`
  - `PAINE` ×6 — `4.0`
  - `TILAVUUS` ×6 — `1.5`
  - `GALLONS` ×6 — `0.4`
  - `KEMIKAALI` ×6 — `BIOCIDE`
  - `DN1` ×6 — `15`
  - `DN2` ×6 — `15`
  - `VARUSTEET` ×6
  - `MATERIAALI` ×6 — `AISI 316`
  - `KOODIOSA` ×6 — `PMM1.5`
  - `VARUSKOODI` ×6
  - `TEKSTI1` ×4 — `SHOWER WATER SYSTEM`
  - `TEKSTI2` ×4 — `BOTTOM WIRE`
  - `KAAVIO` ×4 — `PI-DIAGRAM RAU8G02312`
  - `IVENIMI` ×2 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×2 — `101`
  - `IVEKOKO` ×2 — `x`
  - `IVETYYPPI` ×2 — `101`
  - `ILINJA` ×2 — `101`
  - `IVEKEMIKAALI` ×2 — `NESTE`
  - `IVEVALMISTAJA` ×2 — `xx`
  - `OSOITE` ×2 — `WARM WATER`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `CONTAINER` _(layer: E)_
  - `WIRE CONDITIONING` _(layer: E)_
  - `MICROPOLYMER SILICA` _(layer: E)_
  - `100 %%%` _(layer: E)_
  - `4-20 mA` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `LI` _(layer: I)_
  - `PI` _(layer: I)_
  - `TOP PLY` _(layer: E)_
  - `BACK PLY` _(layer: E)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ACANSGDT` (amgdt.shx), `ROMANS` (ROMANS.SHX), `Copyright` (romans.shx), `ISOCP` (isocp.shx), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 18. `PCSG028677.03_Wire_and_felt_cleaning_agents.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 2936 |
| Entities (model space) | 911 |
| Layers | 47 |
| Block definitions | 29 |
| Unique attribute tags | 64 |
| App ID fingerprint | PCAD ×19 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (23 records) |

**Entities:** LINE×276, TEXT×267, INSERT×250, LWPOLYLINE×110, MTEXT×4, ARC×2, ATTDEF×2

**Layers (47):**  
`0`, `I`, `T`, `PKV`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `E`, `F`, `D`, `U`, `PUP`, `26`, `P-OTHER`, `Valmet`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid`, `Valmet_logo_space_around_logo`, `Valmet_tb_text_en`, `Valmet_tb_text_fr`, `Valmet_tb_text_de`, `P-PUMP_POS` … +7 more

**Custom linetypes (5):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (27):**

  - `N` (1 entities)
  - `VENT` (11 entities)
  - `VENTK` (8 entities)
  - `K` (6 entities)
  - `PESUYHDE` (12 entities)
  - `VAROV` (19 entities)
  - `POSPMM` (17 entities)
  - `A$C52093E87` (1 entities)
  - `A$C15FA388F` (3 entities)
  - `KASIV` (6 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `PPI_0504A-30_0` (6 entities)
  - `muutostau` (32 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `P7A1304` (1 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_00` (1 entities)
  - `A$6D584` (6 entities)
  - `P7A1372` (4 entities)
  - `P7A1369` (4 entities)

**Most-used block inserts:**

  - `PPI_0900A` ×66
  - `PESUYHDE` ×28
  - `PPI_1100A` ×23
  - `P7A1304` ×21
  - `VENT` ×20
  - `VENTK` ×12
  - `PPI_0102B` ×10
  - `PPI_1207A` ×10
  - `PPI_00` ×10
  - `POSPMM` ×8
  - `PPI_0504A-30_0` ×8
  - `VAROV` ×6
  - `N` ×6
  - `K` ×4
  - `P7A1369` ×3

**Attribute tags & sample values (64 unique tags):**

  - `VENIMI` ×66 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×66 — `1001`
  - `VEKOKO` ×66 — `x`
  - `VETYYPPI` ×66 — `101`
  - `LINJA` ×66 — `101`
  - `VEKEMIKAALI` ×66 — `NESTE`
  - `VEVALMISTAJA` ×66 — `xx`
  - `POSITIO` ×8 — `801.1`
  - `LAITE` ×8 — `DOSING PUMP`
  - `PAINE` ×8 — `4.0`
  - `TILAVUUS` ×8 — `1.5`
  - `GALLONS` ×8 — `0.4`
  - `KEMIKAALI` ×8 — `BIOCIDE`
  - `DN1` ×8 — `15`
  - `DN2` ×8 — `15`
  - `VARUSTEET` ×8
  - `MATERIAALI` ×8 — `AISI 316`
  - `KOODIOSA` ×8 — `PMM1.5`
  - `VARUSKOODI` ×8
  - `A` ×6 — `03`
  - `PRODUCT` ×1 — `PCS`
  - `SUBPROJECT_2` ×1
  - `DESC` ×1 — `WIRE AND FELT CLEANING AGENTS`
  - `DESCR_2` ×1 — `FLOWSHEET`
  - `REFERENCE` ×1
  - `HBLK_DR_BYLONG` ×1 — `S. Ruippo`
  - `HBLK_CHK_BYLONG` ×1 — `J. Arola`
  - `HBLK_APP_BYLONG` ×1 — `K. Kultalahti`
  - `CUST_LOC` ×1 — `Shotton Paper Mill, United Kingdom`
  - `CUST_POS` ×1 — `Shotton PM3`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `CONTAINER` _(layer: E)_
  - `WIRE CLEANING AGENT` _(layer: E)_
  - `4-20 mA` _(layer: T)_
  - `PURCHASER DELIVERY` _(layer: T)_
  - `EQUIPMENT - VALMET DELIVERY` _(layer: Valmet)_
  - `EQUIPMENT AND MATERIALS :` _(layer: T)_
  - `INSTRUMENTATION - VALMET DELIVERY` _(layer: I)_
  - `WET END CHEMICAL` _(layer: T)_
  - `100 %%%` _(layer: E)_
  - `FELT CLEANING AGENT` _(layer: E)_
  - `PI` _(layer: I)_
  - `LI` _(layer: I)_
  - `Signature` _(layer: P-OTHER)_
  - `Date` _(layer: P-OTHER)_
  - `CERTIFIED` _(layer: P-OTHER)_
  - `35-49P501` _(layer: P-PUMP_POS)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `ARIAL` (arial.ttf), `ACANSGDT` (amgdt.shx), `ROMANS` (ROMANS.SHX), `Copyright` (romans.shx), `ISOCP` (isocp.shx), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 19. `PCSG028678.03_Optisizer_hard_with_spray_supply_system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 8470 |
| Entities (model space) | 4747 |
| Layers | 56 |
| Block definitions | 60 |
| Unique attribute tags | 82 |
| App ID fingerprint | PCAD ×16 | other: RAK, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (134 records) |

**Entities:** LINE×1748, TEXT×1194, INSERT×1129, LWPOLYLINE×415, ARC×188, CIRCLE×42, SPLINE×22, MTEXT×5

**Layers (56):**  
`0`, `I`, `T`, `R`, `RA`, `HY`, `LA`, `LO`, `PR`, `VEP`, `LAP`, `E`, `F`, `D`, `U`, `PUP`, `P`, `H`, `26`, `ER`, `P-OTHER`, `Valmet`, `HYV`, `T-POS`, `TEXT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid`, `Valmet_logo_grayscale_gray_solid`, `Valmet_logo_grayscale_gray_borders`, `Valmet_logo_black_solid` … +16 more

**Custom linetypes (4):**

  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (58):**

  - `N` (1 entities)
  - `TOIMILV` (13 entities)
  - `TAKAISKU` (11 entities)
  - `TOIMILVK` (10 entities)
  - `VENT` (11 entities)
  - `MOTOR` (10 entities)
  - `VENTK` (8 entities)
  - `PESUYHDE` (12 entities)
  - `K` (6 entities)
  - `TOIMRAJA` (5 entities)
  - `MRS` (9 entities)
  - `PI` (2 entities)
  - `WECOSOITE 2` (7 entities)
  - `A$C52093E87` (1 entities)
  - `PALJE` (10 entities)
  - `PRM` (8 entities)
  - `POSPKM` (16 entities)
  - `SEK` (5 entities)
  - `PAINALV` (13 entities)
  - `WECOSOITE 4` (7 entities)
  - `PUTPOS` (1 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `VALMET_LOGO` (376 entities)
  - `Valmet_TB01` (193 entities)
  - `CTS_INFP` (1 entities)
  - `C-85D9` (8 entities)
  - `A$159B0` (5 entities)
  - `A$159E1` (5 entities)
  - `A$15A12` (5 entities)
  - `P7A1305` (1 entities)
  - … +28 more

**Most-used block inserts:**

  - `PPI_1100A` ×135
  - `P7A1304` ×133
  - `PPI_1207A` ×128
  - `PPI_0900A` ×127
  - `PPI_1000A` ×100
  - `N` ×91
  - `VENT` ×70
  - `TOIMILVK` ×56
  - `TOIMILV` ×40
  - `VENTK` ×31
  - `PPI_0102B` ×28
  - `PPI_00` ×27
  - `PPI_1302A-25_0` ×18
  - `MOTOR` ×16
  - `TAKAISKU` ×14

**Attribute tags & sample values (82 unique tags):**

  - `LINJA` ×131 — `101`
  - `VENIMI` ×127 — `LÄPPÄVENTTIILI`
  - `VEPOSITIO` ×127 — `1001`
  - `VEKOKO` ×127 — `x`
  - `VETYYPPI` ×127 — `101`
  - `VEKEMIKAALI` ×127 — `NESTE`
  - `VEVALMISTAJA` ×127 — `xx`
  - `IVENIMI` ×96 — `LÄPPÄVENTTIILI`
  - `IVEPOSITIO` ×96 — `101`
  - `IVEKOKO` ×96 — `x`
  - `IVETYYPPI` ×96 — `101`
  - `ILINJA` ×96 — `101`
  - `IVEKEMIKAALI` ×96 — `NESTE`
  - `IVEVALMISTAJA` ×96 — `xx`
  - `MOTOR` ×16 — `MOTOR`
  - `MOTORPOS` ×16 — `MOTORPOS`
  - `POWER` ×16 — `POWER`
  - `RPM` ×16 — `RPM`
  - `CURRENT` ×16 — `CURRENT`
  - `DRIVE` ×16 — `DRIVE`
  - `MOUNTED` ×16 — `MOUNTED`
  - `A` ×12 — `03`
  - `TEKSTI1` ×11 — `SURFACE SIZE PREP.`
  - `TEKSTI2` ×11 — `PRESSURE LINE`
  - `KAAVIO` ×11 — `PI-DIAGRAM PCSG028666`
  - `OSOITE` ×6 — `HOT WATER`
  - `POSITIO` ×2 — `101.1`
  - `LAITE` ×2 — `CENTRIFUGAL PUMP`
  - `PAINE` ×2 — `4`
  - `TILAVUUS` ×2 — `600`

**Text entity samples (model space):**

  - `TIIVISTEVESI` _(layer: F)_
  - `SEALING WATER` _(layer: U)_
  - `SPERRWASSER` _(layer: D)_
  - `TÄTNINGSVATTEN` _(layer: R)_
  - `VARMVATTEN` _(layer: R)_
  - `LÄMMIN VESI` _(layer: F)_
  - `WARMWASSER` _(layer: D)_
  - `WARM WATER` _(layer: U)_
  - `\pxqc;{\fArial|b0|i0|c0|p34;\C2;OPTISCREEN STRAINER COARSE SCREEN}` _(layer: PR)_
  - `WASHING WATER` _(layer: T)_
  - `DILUTION` _(layer: E)_
  - `15 bar` _(layer: E)_
  - `SUPPLY SCREENS - TOP` _(layer: E)_
  - `CYCLONE` _(layer: E)_
  - `SCRUBBER` _(layer: E)_
  - `BOTTOM` _(layer: E)_
  - `TOP` _(layer: E)_
  - `DRAIN OR` _(layer: E)_
  - `PULPER` _(layer: E)_
  - `L200-2` _(layer: E)_

**Text styles:** `STANDARD` (TXT.shx), `SANDARD` (txt.shx), `STYLE1` (swissbo.ttf), `ARIAL` (arial.ttf), `ARIAL_BOLD` (arialbd.ttf), `ACANSGDT` (amgdt.shx), `SFS` (txt.shx), `Copyright` (romans.shx), `ROMANS` (ROMANS.SHX), `ISOCP` (isocp.shx), `Text3_2` (txt.shx), `CTS_REV` (isocp.shx)

---

### 20. `RAU6401403_03_FLOW_DIAGRAM_OCPRO.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet flow-diagram sub-type |
| DWG version | 33 |
| Last saved by | `jklohenoti` |
| Objects | 69171 |
| Entities (model space) | 35255 |
| Layers | 53 |
| Block definitions | 109 |
| Unique attribute tags | 107 |
| App ID fingerprint | GENIUS ×7 | other: DCO15, FOCUSPI_1_3, FOCUSPI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×31998, ARC×1842, TEXT×426, INSERT×405, MTEXT×160, ATTDEF×90, TRACE×84, CIRCLE×78

**Layers (53):**  
`0`, `TEXT_1`, `DEFPOINTS`, `TEXT`, `26`, `PI0ATT`, `PI3VENT`, `PI4INST`, `PI4IVIIV`, `PI4ITXT`, `PI2VLMPRLIN_035`, `PI1POSI`, `TEKSTIT`, `PI1MERK`, `PI2PVAR`, `PI0LATTIA`, `PI0KOR`, `PI2VLAPRLIN_035`, `PI2VPRLIN`, `PI5LAITE`, `PI2VPRLIN_035`, `PI2PRLIN2_035`, `1`, `PI2IPRLIN`, `KATKO`, `TEKSTIT___1`, `Valmet_border_out`, `Valmet_border_in`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `Valmet_logo_grayscale_gray2_borders`, `Valmet_logo_grayscale_gray2_solid`, `Valmet_logo_grayscale_lightgray_borders`, `Valmet_logo_grayscale_lightgray_solid` … +13 more

**Custom linetypes (19):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `KV` — -- -- -- -- -- -- --
  - `AMCONSTR` — _______________________
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `ACAD_ISO10W100` — ISO dash dot __ . __ . __ . __ . __ . __ . __ .
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGL` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `PKV` — __ . __ . __ . __
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (106):**

  - `HDR_INSPOINT` (3 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `MUUTOSTAU` (32 entities)
  - `PI321` (22 entities)
  - `PI322` (24 entities)
  - `PI3IVO` (22 entities)
  - `PI3ANT` (19 entities)
  - `PI0NUOPR` (20 entities)
  - `PI0KORK` (4 entities)
  - `PI0KAI2` (6 entities)
  - `POSLA` (5 entities)
  - `PI0PSIVE` (5 entities)
  - `PI0PSKVE` (5 entities)
  - `PI314` (2 entities)
  - `A$C341527A9` (1068 entities)
  - `A$C08F840E4` (39 entities)
  - `A$C6C812CF7` (39 entities)
  - `A$C2A1C2963` (10 entities)
  - `METSO_LOGO_LEIMAT` (810 entities)
  - `CERTIFIED_EN` (12 entities)
  - `A$C4B4543CA` (30 entities)
  - `A$C4AB37708` (30 entities)
  - `PIPE STANDART` (180 entities)
  - `A$C13774846` (59 entities)
  - `A$C0AA13B8D` (7 entities)
  - `OCPRO pumppuyjsikkö` (45 entities)
  - `venttiilikotelo1` (72 entities)
  - `GROUP NUMBER` (3 entities)
  - `alaosamerkki` (12 entities)
  - `VALMET_LOGO` (376 entities)
  - … +76 more

**Most-used block inserts:**

  - `PI0NUOPR` ×96
  - `PI0KAI2` ×29
  - `KP` ×29
  - `PI0KORK` ×21
  - `Strecher energy chain` ×13
  - `HP` ×12
  - `HEAD` ×12
  - `A$C4E794BB9` ×12
  - `New_cyclone` ×12
  - `POSLA` ×12
  - `Handvalve` ×12
  - `GROUP NUMBER` ×5
  - `venttiilikotelo2` ×4
  - `A$C2A1C2963` ×4
  - `BLOW CLEANING_14734887_1.1_RAUH441052` ×4

**Attribute tags & sample values (107 unique tags):**

  - `PUTOSAS` ×96
  - `PUTLINJ` ×96
  - `PUTAINE` ×96 — `- ei määritetty -`
  - `PUTAILY` ×96
  - `PUTVIRT` ×96
  - `PUTKAP` ×96
  - `PUTTIH` ×96
  - `PUTDN` ×96
  - `PUTPN` ×96
  - `PUTMATE` ×96
  - `PUTPAIN` ×96
  - `PUTLAMM` ×96
  - `PUTMIST` ×96
  - `PUTMIHI` ×96
  - `PUTERI1` ×96
  - `PUTERI2` ×96
  - `PUTLISA` ×96
  - `AIR_OUTLET` ×22 — `ø22`
  - `AIR_OUTLET_NA` ×22
  - `KORKEUS` ×21 — `MACHINE LEVEL`
  - `Ø10X1` ×18 — `ø10x1`
  - `OD3/8"X0,035` ×18 — `OD 3/8"x0,035`
  - `Ø22X2` ×16 — `ø22x2`
  - `OD3/4"X0,065` ×16
  - `LP_VACUUM_LINE` ×12 — `ø10`
  - `LP_VACUUM_LINE_NA` ×12 — `3/8"NPT`
  - `LP_OUTLET` ×12 — `ø15`
  - `LP_OUTLET_NA` ×12 — `1/2"NPT`
  - `Ø15X1,5` ×12 — `ø15x1,5`
  - `OD1/2"X0,049` ×12 — `OD 1/2"x0,049`

**Text entity samples (model space):**

  - `Ø12x3 seamless` _(layer: TEKSTIT)_
  - `OPTICEANER PRO PIPING SIZE` _(layer: TEKSTIT)_
  - `1100 L/ min / UNIT @ 6 BAR` _(layer: TEKSTIT)_
  - `COMPRESSED AIR CONSUPTION` _(layer: TEKSTIT)_
  - `PIPE SIZE (DN)` _(layer: TEKSTIT)_
  - `OCPro PCS.` _(layer: TEKSTIT)_
  - `5` _(layer: TEKSTIT)_
  - `1` _(layer: TEKSTIT)_
  - `2` _(layer: TEKSTIT)_
  - `3` _(layer: TEKSTIT)_
  - `4` _(layer: TEKSTIT)_
  - `7` _(layer: TEKSTIT)_
  - `6` _(layer: TEKSTIT)_
  - `25` _(layer: TEKSTIT)_
  - `8` _(layer: TEKSTIT)_
  - `9` _(layer: TEKSTIT)_
  - `10` _(layer: TEKSTIT)_
  - `11` _(layer: TEKSTIT)_
  - `32` _(layer: TEKSTIT)_
  - `40` _(layer: TEKSTIT)_

**Text styles:** `STANDARD` (isocp.shx), `TEXT` (romans.shx), `TEXT3_2` (txt.shx), `ROMANS` (romans.shx), `ARIAL` (txt), `ACANSGDT` (amgdt.shx), `Copyright` (romans.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACANSTS` (romans.shx)

---

### 21. `RAU6401404_01_FLOW_DIAGRAM_DOUBLEJET_TAIL_JET_P.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet flow-diagram sub-type |
| DWG version | 33 |
| Last saved by | `jklohenoti` |
| Objects | 8290 |
| Entities (model space) | 483 |
| Layers | 58 |
| Block definitions | 57 |
| Unique attribute tags | 83 |
| App ID fingerprint | PCAD ×2 | GENIUS ×10 | other: FOCUSPI_1_3, FOCUSPI, MPI_1 |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SRVAS`: V
- `SROIK`: C

**Entities:** ARC×161, LINE×101, MTEXT×96, INSERT×40, LWPOLYLINE×29, ATTDEF×20, TEXT×13, CIRCLE×10

**Layers (58):**  
`0`, `arkkiulkoreuna`, `arkkisisareuna`, `DEFPOINTS`, `TEXT`, `26`, `PI0ATT`, `PI3VENT`, `PI4INST`, `PI4IVIIV`, `PI4ITXT`, `PI1POSI`, `pi0lattia`, `Tekstit`, `pi1merk`, `pi0kor`, `pi2vlaprlin_035`, `PI5LAITE`, `TEXT_1`, `pi3vlavent`, `pi6vlalaite`, `pi5vlapump`, `pi2vlapvar`, `pi2vlmprlin_035`, `pi5pump`, `pi2pvar`, `pi6laite`, `AM_6`, `pi2vprlin_035`, `AM_5`, `Valmet_border_out`, `Valmet_border_in`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders` … +18 more

**Custom linetypes (18):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `KV` — -- -- -- -- -- -- --
  - `PKV` — __ . __ . __ . __
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGL` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _

**Block definitions (55):**

  - `alaosamerkki` (12 entities)
  - `hdr_inspoint` (3 entities)
  - `BILL_OF_MAT_LINE1` (6 entities)
  - `muutostau` (32 entities)
  - `copyright` (3 entities)
  - `PI321` (22 entities)
  - `PI3I` (17 entities)
  - `PI0NUOPR` (20 entities)
  - `pi3ivo` (22 entities)
  - `pi3ant` (19 entities)
  - `pi0psive` (5 entities)
  - `PI3117` (9 entities)
  - `pi0kork` (4 entities)
  - `PI660O22` (14 entities)
  - `pi0kai2` (6 entities)
  - `posla` (5 entities)
  - `PI3223` (28 entities)
  - `PI3215A` (22 entities)
  - `pi0pspum` (15 entities)
  - `PI32121` (24 entities)
  - `PI32122` (31 entities)
  - `PI512` (21 entities)
  - `Metso_TB01` (914 entities)
  - `PI3319` (17 entities)
  - `PI3224` (32 entities)
  - `PI322` (24 entities)
  - `pi3ivh` (22 entities)
  - `pi3ik` (17 entities)
  - `pi3iv` (18 entities)
  - `pi3ia` (19 entities)
  - … +25 more

**Most-used block inserts:**

  - `posla` ×12
  - `PI0NUOPR` ×8
  - `PI321` ×3
  - `Positio` ×3
  - `pi0kork` ×2
  - `pi0kai2` ×2
  - `PIPE STANDART` ×1
  - `ylaosamerkkiA3` ×1
  - `hdr_inspoint` ×1
  - `muutostau` ×1
  - `Valmet_china_copyright` ×1
  - `Valmet_copyright` ×1
  - `Valmet_TB01` ×1
  - `approved_en` ×1
  - `PI3117` ×1

**Attribute tags & sample values (83 unique tags):**

  - `POSINO` ×12 — `xxxxxxxx`
  - `PUTOSAS` ×8
  - `PUTLINJ` ×8
  - `PUTAINE` ×8 — `- ei määritetty -`
  - `PUTAILY` ×8
  - `PUTVIRT` ×8
  - `PUTKAP` ×8
  - `PUTTIH` ×8
  - `PUTDN` ×8
  - `PUTPN` ×8
  - `PUTMATE` ×8
  - `PUTPAIN` ×8
  - `PUTLAMM` ×8
  - `PUTMIST` ×8
  - `PUTMIHI` ×8
  - `PUTERI1` ×8
  - `PUTERI2` ×8
  - `PUTLISA` ×8
  - `KVENIMI` ×3 — `Venttiili`
  - `KVEPOS` ×3
  - `KVETYYP` ×3 — `BA`
  - `KVEDN` ×3
  - `KVEPN` ×3
  - `KVEMAT` ×3
  - `KVELIIT` ×3
  - `KVEPITU` ×3
  - `KVEERI1` ×3
  - `KVEKVAS` ×3
  - `KVEPUPO` ×3
  - `KVEAILY` ×3

**Text entity samples (model space):**

  - `BOILER FEED WATER/CONDESATE` _(layer: PI1POSI)_
  - `FS` _(layer: PI1POSI)_
  - `4` _(layer: PI1POSI)_
  - `DOUBLE JET \P11th DRYER GROUP` _(layer: PI1POSI)_
  - `INLET` _(layer: Tekstit)_
  - `Ø8` _(layer: Tekstit)_
  - `\A1;%%C8x2 SEAMLESS` _(layer: Tekstit)_
  - `WATER JET CUTTERS HP UNIT 600bar` _(layer: pi3vlavent)_
  - `DOUBLE JET \P7th DRYER GROUP` _(layer: PI1POSI)_
  - `INSTRUMENT AIR` _(layer: PI1POSI)_
  - `5-9 bar` _(layer: Tekstit)_
  - `Ø10X1` _(layer: Tekstit)_
  - `5` _(layer: PI1POSI)_
  - `Abs. encoder cooling air rubber hose %%C3/8` _(layer: Tekstit)_
  - `HP WATER OUT Ø10` _(layer: Tekstit)_
  - `TAILJET P` _(layer: PI1POSI)_
  - `TP316L %%C10x2 SML` _(layer: Tekstit)_
  - `%%C10` _(layer: Tekstit)_
  - `HP WATER IN Ø8` _(layer: Tekstit)_
  - `{\LDELIVERY LIMITS:}` _(layer: TEXT_1)_

**Text styles:** `Standard` (romans.shx), `Text3_2` (romans.shx), `ROMANS` (romans.shx), `ROMA` (roma), `TEXT` (romans.shx), `ACISOGDT` (amgdt.shx), `ACANSGDT` (amgdt.shx), `Annotative` (txt), `Copyright` (romans.shx), `ACANSTS` (romans.shx), `ACISOTS` (isocp.shx)

---

### 22. `RAU8F00290.10_Steam and Condensate.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `samuli.autio` |
| Objects | 25884 |
| Entities (model space) | 20014 |
| Layers | 61 |
| Block definitions | 202 |
| Unique attribute tags | 119 |
| App ID fingerprint | PCAD ×32 | GENIUS ×1 | other: CTS_INFO, CTS_SHEET, CTS-SMBNIMI |
| Connectivity | ✅ LIN_FROM/LIN_TO (857 records) |

**Title block fields:**

- `INF14`: 10
- `INF1`: 04.03.2022
- `INF2`: MKat
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8F00290.10
- `SHEET`: 1/1
- `ARKKI`: A1+
- `LYH`: SHOTTONPM3
- `TITLE1`: Steam and Condensate System
- `CAD`: AutoCAD
- `MRK`: 10
- `PVM`: 03.04.2024
- `MUU`: SAut
- `TAR`: JMus
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: MKat
- `TAR2`: SStr
- `MUUTOS2`: Updated

**Entities:** LWPOLYLINE×7784, INSERT×5856, TEXT×4935, ATTDEF×748, CIRCLE×284, MTEXT×134, ARC×125, LINE×109

**Layers (61):**  
`0`, `P-OTHER`, `P-INSTRU`, `P-PUMPS`, `P-VENTS`, `P-VALVEPOS`, `P-LINEPOS`, `P-EQUIPMENT_POS`, `P-INSTRPOS`, `P-PUMP_POS`, `P-COND`, `P-CVPOS`, `P-TANK_POS`, `PI0ATT`, `P-A-SHEET`, `P-INSTRPOS_TEXTS`, `ASHADE`, `KUIVATUSSYLINTERIT`, `VAC-TELAT`, `VESIKIERROT`, `SAATOVENTTIILIT`, `KASIVENTTIILIT`, `PUMPUT`, `METALLILETKUT`, `NAKOLASIT`, `KURISTINLEVYT`, `VEDENEROTTIMET`, `LAITTEISTO`, `PUTKIKARTIOT`, `BALANSSI`, `ILMAPUTKET`, `HOYRYRYHMIEN NIMET`, `zzzzzz`, `zz`, `HOYRYPATTERIT`, `KAYTOT`, `yyyy`, `yyyyy`, `ins_025_muov`, `laitteisto_txt` … +21 more

**Custom linetypes (8):**

  - `DASHDOT2` — _._._._._._._._._._._._._._._._._._._._._._._._
  - `KV` — -- -- -- -- -- -- --
  - `PKV` — __ . __ . __ . __
  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __

**Block definitions (202):**

  - `PPI_1100A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `CTS_INFP` (1 entities)
  - `PPI_1000A` (1 entities)
  - `CTS_USER_ID` (1 entities)
  - `P7A1214` (2 entities)
  - `P7A0200` (3 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_1207A` (6 entities)
  - `P7A1271` (2 entities)
  - `PCAD_INF` (1 entities)
  - `P7A1208` (5 entities)
  - `AVE_RENDER` (0 entities)
  - `AVE_GLOBAL` (0 entities)
  - `RM_SDB` (23 entities)
  - `CTS_INFS` (1 entities)
  - `PI321` (4 entities)
  - `PI51` (3 entities)
  - `PI314` (2 entities)
  - `LAI2587` (4 entities)
  - `FLEXIBLE-JOINT` (8 entities)
  - `PI321O06` (6 entities)
  - `PI313` (4 entities)
  - `LPoist` (2 entities)
  - `ARROW` (2 entities)
  - `levylammonvaihdin` (17 entities)
  - `höyrypatteri` (7 entities)
  - `PI660O22` (14 entities)
  - `DRIVE-SHAFT` (3 entities)
  - … +172 more

**Most-used block inserts:**

  - `PPI_0900A` ×1055
  - `PPI_1100A` ×756
  - `P7A1100` ×624
  - `P7A1325` ×258
  - `ARROW` ×256
  - `PPI_0103B` ×236
  - `P7A1305` ×220
  - `PPI_1207A` ×170
  - `FLEXIBLE-JOINT` ×139
  - `A$A7D25` ×128
  - `PPI_1000A` ×115
  - `PRO66DD` ×111
  - `P7A1215` ×104
  - `LPoist` ×103
  - `PPI_1200A` ×102

**Attribute tags & sample values (119 unique tags):**

  - `SYM_WIDTH` ×469 — `5.00`
  - `FC` ×243 — `T100`
  - `A` ×44 — `TP 002`
  - `TEKSTI1` ×35 — `SLP SUPPLY`
  - `TEKSTI2` ×35 — `FROM POWER PLANT`
  - `KAAVIO` ×35 — `PCSG028678`
  - `MRK` ×14 — `00`
  - `KPL` ×14
  - `PVM` ×14 — `04.03.2022`
  - `MUU` ×14 — `MKat`
  - `TAR` ×14 — `SStr`
  - `MUUTOS` ×14 — `Preliminary`
  - `KVENIMI` ×13 — `Shut-off valve`
  - `KVEPOS` ×13 — `17512`
  - `KVETYYP` ×13
  - `KVEDN` ×13 — `15`
  - `KVEPN` ×13
  - `KVEMAT` ×13
  - `KVELIIT` ×13
  - `KVEPITU` ×13
  - `KVEERI1` ×13
  - `KVEKVAS` ×13
  - `KVEPUPO` ×13
  - `KVEAILY` ×13
  - `KVETIH` ×13
  - `KVEVIR` ×13
  - `KVEKPAI` ×13
  - `KVEKLAT` ×13
  - `KVEPERO` ×13
  - `KVELISA` ×13

**Text entity samples (model space):**

  - `p=20 kPa(g)` _(layer: BALANSSI)_
  - `+50 kPa(g)` _(layer: TEXT)_
  - `set p.` _(layer: TEXT)_
  - `7,5 bar (g)` _(layer: TEXT)_
  - `min 2 m` _(layer: P-OTHER)_
  - `p=450 kPa(g)` _(layer: BALANSSI)_
  - `SG1B` _(layer: HOYRYRYHMIEN NIMET)_
  - `SG1C` _(layer: HOYRYRYHMIEN NIMET)_
  - `SG1A` _(layer: HOYRYRYHMIEN NIMET)_
  - `SG2A` _(layer: HOYRYRYHMIEN NIMET)_
  - `SG2B` _(layer: HOYRYRYHMIEN NIMET)_
  - `35 ºC` _(layer: BALANSSI)_
  - `70 ºC` _(layer: BALANSSI)_
  - `8 (12) l/s` _(layer: BALANSSI)_
  - `p=80 kPa(g)` _(layer: BALANSSI)_
  - `OptiSizer` _(layer: P-OTHER)_
  - `HEATING` _(layer: P-OTHER)_
  - `ST` _(layer: P-DELIVERY_LIMIT)_
  - `SS` _(layer: P-DELIVERY_LIMIT)_
  - `WALKWAY 1` _(layer: P-OTHER)_

**Text styles:** `STANDARD` (ARIALN.TTF), `ISO` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ASHADE` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ROMA` (ARIALN.TTF), `MODESTD` (ARIALN.TTF), `SFS` (ARIALN.TTF), `MODESTD085` (ARIALN.TTF), `LEGIBLE` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 23. `RAU8G02312.11 Shower Water system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 18590 |
| Entities (model space) | 10444 |
| Layers | 49 |
| Block definitions | 218 |
| Unique attribute tags | 83 |
| App ID fingerprint | PCAD ×35 | GENIUS ×4 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (446 records) |

**Title block fields:**

- `INF14`: 11
- `INF1`: 04.03.2022
- `INF2`: JLep
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02312.11
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: Shower Water system
- `CAD`: AutoCAD
- `MRK`: 11
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLep
- `TAR2`: SStr
- `MUUTOS2`: Certified
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×3600, INSERT×3103, TEXT×3032, MTEXT×473, LINE×141, CIRCLE×43, POLYLINE×22, ATTDEF×20

**Layers (49):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-WATER`, `P-SYMB`, `P-VENTS`, `P-TANK_POS`, `P-PUMPS`, `P-INSTRU`, `P-PUMP_POS`, `P-INSTRPOS`, `P-TEXT`, `P-FLOOR`, `P-CVPOS`, `P-VALVEPOS`, `PI0ATT`, `P-EQUIPMENTS`, `P-LINEPOS`, `P-EQUIPMENT_POS`, `P-STEAM2`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `P-DELIVERY_LIMIT`, `P-REVISIONS`, `pi1merk`, `TEXT_1`, `pi6vlaite`, `Tekstit`, `P-FEED_WATER`, `P-WHITE_WATER`, `P-WARM_WATER`, `P-NUMBER`, `P-HOT_WATER`, `P-STEAM1`, `P-COND`, `P-WARM_WATER_SHOWER_3BAR`, `P-WARM_WATER_SHOWER_25BAR`, `P-WARM_WATER_SHOWER_35BAR`, `P-COND_SHOWER_35BAR`, `P_SUPER_CLEAR_FILTRATE_SHOWER_12BAR` … +9 more

**Custom linetypes (9):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `KV` — -- -- -- -- -- -- --
  - `PKV` — __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium

**Block definitions (218):**

  - `P7A1305` (1 entities)
  - `PPI_0102B` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1304` (1 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `P7A1206` (4 entities)
  - `P7A1303` (1 entities)
  - `PPI_1000A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1255` (2 entities)
  - `PR260AB` (3 entities)
  - `PR260CE` (3 entities)
  - `P7A1333` (5 entities)
  - `PR262A0` (3 entities)
  - `P7A1214` (2 entities)
  - `PR7715E` (3 entities)
  - `P7A1220` (4 entities)
  - `P7A1212` (2 entities)
  - `P7A2105` (15 entities)
  - `P7A1210` (1 entities)
  - `C-85BC` (8 entities)
  - `P7A1315` (4 entities)
  - `PR61300` (3 entities)
  - `P7A1113` (3 entities)
  - `C-5A07` (8 entities)
  - … +188 more

**Most-used block inserts:**

  - `PPI_1100A` ×432
  - `PPI_0900A` ×405
  - `P7A1305` ×363
  - `P7A1100` ×305
  - `P7A1304` ×156
  - `PPI_1000A` ×138
  - `p7a1370` ×126
  - `PPI_1207A` ×123
  - `PI660O19` ×122
  - `PIPOS3` ×96
  - `PPI_0102B` ×69
  - `P7A1220` ×57
  - `PPI_1204A` ×41
  - `P7A1106` ×28
  - `PPI_1200A` ×28

**Attribute tags & sample values (83 unique tags):**

  - `LAINIMI` ×122 — `Omalaite 19`
  - `LAIPOS` ×122 — `74`
  - `LAIKAPA` ×122
  - `LAIMTEH` ×122
  - `LAIKIER` ×122
  - `LAIJANN` ×122
  - `LAIMASE` ×122
  - `LAIERI1` ×122
  - `LAIERI2` ×122
  - `LAIERI3` ×122
  - `LAIERI4` ×122
  - `LAILISA` ×122
  - `POSINO` ×104 — `74`
  - `TEKSTI1` ×40 — `FRESH WATER`
  - `TEKSTI2` ×40 — `TOWER`
  - `KAAVIO` ×40 — `PI-DIAGRAM RAU8G02314`
  - `A` ×26 — `11`
  - `MRK` ×11 — `00`
  - `KPL` ×11
  - `PVM` ×11 — `04.03.2022`
  - `MUU` ×11 — `JLep`
  - `TAR` ×11 — `SStr`
  - `MUUTOS` ×11 — `Preliminary`
  - `MOMENTARYMAX.` ×10 — `15,3`
  - `CONTINUOUSMAX.` ×10 — `6,8`
  - `CONTINUOUSREGULAR` ×10 — `9,7`
  - `INFO` ×8 — `+0.000`
  - `PUTOSAS` ×7
  - `PUTLINJ` ×7
  - `PUTAINE` ×7 — `- ei määritetty -`

**Text entity samples (model space):**

  - `PI-DIAGRAM STOD206338` _(layer: P-TEXT)_
  - `10 bar` _(layer: P-TEXT)_
  - `SUPER CLEAR FILTRATE PUMP 35-25P511` _(layer: P-TEXT)_
  - `ØX mm` _(layer: P-TEXT)_
  - `WARM WATER` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `SHOWER WATER` _(layer: P-TEXT)_
  - `TRIM WATER MODULE` _(layer: P-TEXT)_
  - `C` _(layer: P-DELIVERY_LIMIT)_
  - `V` _(layer: P-DELIVERY_LIMIT)_
  - `25 µm` _(layer: P-TEXT)_
  - `%%CX mm` _(layer: P-TEXT)_
  - `PM3` _(layer: P-TEXT)_
  - `CHEMICAL PREPARATION` _(layer: P-TEXT)_
  - `WARM FRESH WATER` _(layer: P-TEXT)_
  - `SUPER CLEAR FILTRATE` _(layer: P-TEXT)_
  - `3 bar` _(layer: P-TEXT)_
  - `25 bar` _(layer: P-TEXT)_
  - `12 bar` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (romans.shx), `ISOCP` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `MONOTXT` (romans.shx), `ARIAL` (arial.ttf), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx), `MtXpl_Arial Narrow` (ARIALN.TTF), `MtXpl_Arial` (txt.shx), `MtXpl_f0890111901_shx` (txt.shx)

---

### 24. `RAU8G02313.11 Vacuum system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 8417 |
| Entities (model space) | 5612 |
| Layers | 34 |
| Block definitions | 116 |
| Unique attribute tags | 67 |
| App ID fingerprint | PCAD ×30 | GENIUS ×3 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (224 records) |

**Title block fields:**

- `INF14`: 11
- `INF1`: 04.03.2022
- `INF2`: JLep
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02313.11
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: Vacuum system
- `CAD`: AutoCAD
- `MRK`: 11
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 13.03.2022
- `MUU2`: JLep
- `TAR2`: SStr
- `MUUTOS2`: Preliminary
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×2130, LWPOLYLINE×1778, INSERT×1605, LINE×69, CIRCLE×10, ARC×9, MTEXT×7, POLYLINE×4

**Layers (34):**  
`0`, `P-A-SHEET`, `P-FLOOR`, `P-OTHER`, `P-WATER`, `P-SYMB`, `P-VENTS`, `P-TEXT`, `P-TANK_POS`, `P-PUMPS`, `P-INSTRU`, `P-INSTRPOS`, `P-PUMP_POS`, `P-LINEPOS`, `P-VALVEPOS`, `P-CVPOS`, `P-VACUUM`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `PI0ATT`, `pi1merk`, `P-FAN_POS`, `P-MACHINE`, `P-DELIVERY_LIMIT`, `P-EQUIPMENT_POS`, `P-AIR`, `P-EQUIPMENTS`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-OIL`, `P-SEALING_WATER`, `P-REVISIONS`, `Defpoints`

**Custom linetypes (7):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `PKV` — __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium

**Block definitions (116):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A1100` (2 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `P7A1106` (5 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0102B` (1 entities)
  - `P7A0200` (3 entities)
  - `PPI_1100A` (1 entities)
  - `PPI_1000A` (1 entities)
  - `P7A1304` (1 entities)
  - `P7A0217` (3 entities)
  - `P7A1210` (1 entities)
  - `PCAD_INF` (1 entities)
  - `CTS_INFI` (1 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `pi0nuopr` (20 entities)
  - `PI3162` (2 entities)
  - `PRMB0BE` (3 entities)
  - `CVMB0D8` (4 entities)
  - `PRMB0FF` (3 entities)
  - `CVMB137` (4 entities)
  - `CVMB5B7` (4 entities)
  - `PRMB933` (3 entities)
  - `CVMB966` (4 entities)
  - `PRMBDAE` (3 entities)
  - `CVMBDEF` (4 entities)
  - `CVMBE02` (4 entities)
  - … +86 more

**Most-used block inserts:**

  - `PPI_1100A` ×192
  - `P7A1305` ×185
  - `PPI_0102B` ×170
  - `p7a1370` ×144
  - `PPI_1207A` ×130
  - `PPI_0900A` ×109
  - `P7A1304` ×101
  - `P7A1100` ×75
  - `PPI_1200A` ×59
  - `PPI_1000A` ×44
  - `PPI_2100A` ×33
  - `PPI_0700A-25_0` ×27
  - `P7A0200` ×20
  - `CVMB5B7` ×20
  - `P7A1210` ×19

**Attribute tags & sample values (67 unique tags):**

  - `A` ×12 — `11`
  - `MRK` ×11 — `00`
  - `KPL` ×11
  - `PVM` ×11 — `04.03.2022`
  - `MUU` ×11 — `JLep`
  - `TAR` ×11 — `SStr`
  - `MUUTOS` ×11 — `Preliminary`
  - `TEKSTI1` ×9 — `WHITE WATER TOWER`
  - `TEKSTI2` ×9 — `35-25P506`
  - `KAAVIO` ×9 — `PI-DIAGRAM STOD206338`
  - `PUTOSAS` ×7
  - `PUTLINJ` ×7
  - `PUTAINE` ×7 — `- ei määritetty -`
  - `PUTAILY` ×7
  - `PUTVIRT` ×7
  - `PUTKAP` ×7
  - `PUTTIH` ×7
  - `PUTDN` ×7
  - `PUTPN` ×7
  - `PUTMATE` ×7
  - `PUTPAIN` ×7
  - `PUTLAMM` ×7
  - `PUTMIST` ×7
  - `PUTMIHI` ×7
  - `PUTERI1` ×7
  - `PUTERI2` ×7
  - `PUTLISA` ×7
  - `INFO` ×3 — `+8.500`
  - `INF17` ×2
  - `INF15` ×1

**Text entity samples (model space):**

  - `SUCTION UNIT CHAMBER 1` _(layer: P-TEXT)_
  - `SUCTION UNIT CHAMBER 2` _(layer: P-TEXT)_
  - `CURVED SUCTION BOX CHAMBER 2` _(layer: P-TEXT)_
  - `COUCH ROLL CHAMBER 2` _(layer: P-TEXT)_
  - `COUCH ROLL CHAMBER 1` _(layer: P-TEXT)_
  - `HIGH-VACUUM SUCTION BOX` _(layer: P-TEXT)_
  - `VACUSHOE CHAMBER 1` _(layer: P-TEXT)_
  - `VACUSHOE CHAMBER 2` _(layer: P-TEXT)_
  - `PICK-UP SUCTION ROLL` _(layer: P-TEXT)_
  - `PICK-UP FELT UHLE BOXES` _(layer: P-TEXT)_
  - `1ST TRANSFER SUCTION ROLL` _(layer: P-TEXT)_
  - `1ST PRESS BOTTOM FELT UHLE BOXES` _(layer: P-TEXT)_
  - `1ST FELT SUCTION ROLL` _(layer: P-TEXT)_
  - `2ND TRANSFER SUCTION ROLL` _(layer: P-TEXT)_
  - `FORMER, LOW VACUUM` _(layer: P-TEXT)_
  - `FORMER, INTERMEDIATE VACUUM` _(layer: P-TEXT)_
  - `OUTER WIRE CHANNEL` _(layer: P-TEXT)_
  - `INNER WIRE CHANNEL` _(layer: P-TEXT)_
  - `SUCTION UNIT CHAMBER 1  SAMPLE 10 %` _(layer: P-TEXT)_
  - `VACUSHOE CHAMBER 1 SAMPLE 10 %` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 25. `RAU8G02314.09 Fresh and Cooling Water system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 242142 |
| Entities (model space) | 7418 |
| Layers | 142 |
| Block definitions | 259 |
| Unique attribute tags | 55 |
| App ID fingerprint | PCAD ×32 | GENIUS ×22 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (72 records) |

**Title block fields:**

- `INF14`: 09
- `INF1`: 04.03.2022
- `INF2`: KLei
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02314.09
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTON PM3
- `TITLE1`: Fresh and Cooling Water system
- `CAD`: AutoCAD
- `MRK`: 09
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: KLei
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×2769, LINE×2315, TEXT×1130, INSERT×778, SPLINE×189, ARC×106, CIRCLE×100, POINT×14

**Layers (142):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-INSTRU`, `P-WATER`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-TANK_POS`, `P-FLOOR`, `P-VALVEPOS`, `P-LINEPOS`, `P-EQUIPMENTS`, `P-PUMP_POS`, `P-CVPOS`, `P-EQUIPMENT_POS`, `P-DELIVERY_LIMIT`, `P-BRANCH`, `P-VALVEPOS_STARTUP`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `P-REVISIONS`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `Defpoints`, `C_WAL_FI`, `M_TNK_FI`, `M_TNK_TH`, `M_EQU_FI`, `C_COL_TH`, `M_STL_FI`, `C_MOD_FI`, `AM_0`, `Text`, `M_STL_TH`, `AM_7`, `A_FRM_FI` … +102 more

**Custom linetypes (38):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `PKV` — __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — ValmetIso __ __ __ __ __ __ __ __ __ __ __
  - `DDASH1` — ____ _ ____ _ ____ _  ____ _ ____ _ ____ _
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `SOLID` — _____________________________
  - `DDASH3` — ____________________  _  __________________
  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `IMPORT-GEN7A` — 
  - `DDASH2` — __________  _  __________  _  _________  _
  - `DURCHG` — DURCHG
  - `DASH3` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ _
  - `CONTINOUS` — Solid line
  - `CONTINUA` — Linea continua

**Block definitions (259):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `PPI_1204A` (6 entities)
  - `P7A1303` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1304` (1 entities)
  - `PPI_0101B` (2 entities)
  - `PPI_1000A` (1 entities)
  - `P7A1315` (4 entities)
  - `P7A1333` (5 entities)
  - `P7A1A16` (10 entities)
  - `p7a1370` (2 entities)
  - `PCAD_INF` (1 entities)
  - `P7A1383` (3 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PI3117` (9 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1209A` (6 entities)
  - `PPI_1201A` (2 entities)
  - `PPI_1202A` (3 entities)
  - `PPI_1200A` (1 entities)
  - `PR-S777` (3 entities)
  - `P7A1118` (2 entities)
  - `CV-S7B6` (4 entities)
  - `P7A1229` (3 entities)
  - `CV-S7F3` (5 entities)
  - … +229 more

**Most-used block inserts:**

  - `PPI_052AA-25_0` ×87
  - `COLUM_N$` ×58
  - `PPI_0700A-25_0` ×45
  - `PPI_0900A` ×40
  - `RPALLO0` ×40
  - `A$C5E972AA4` ×39
  - `PPI_1100A` ×28
  - `PPI_1204A` ×22
  - `P7A1305` ×22
  - `P7A1100` ×22
  - `PPI_1302A-25_0` ×19
  - `PPI_0802A-25_0` ×19
  - `PPI_0102B` ×17
  - `P7A1369` ×12
  - `P7A1304` ×11

**Attribute tags & sample values (55 unique tags):**

  - `A` ×62 — `TP 001`
  - `COLUMN_NR` ×58 — `A`
  - `POSITIO` ×39 — `35-48T601`
  - `TEKSTI1` ×14 — `DEAERATOR CONDENSER`
  - `KAAVIO` ×14 — `PI-DIAGRAM STOD206337`
  - `TEKSTI2` ×11 — `AND VACUUM PUMPS`
  - `TYPE` ×10 — `EQUI`
  - `NAME` ×10 — `/3125E001_F`
  - `REF` ×10 — `=27277/84839`
  - `MRK` ×9 — `00`
  - `KPL` ×9
  - `PVM` ×9 — `04.03.2022`
  - `MUU` ×9 — `KLei`
  - `TAR` ×9 — `SStr`
  - `MUUTOS` ×9 — `Preliminary`
  - `INF17` ×2
  - `INFO` ×1 — `+0.000`
  - `INF15` ×1
  - `INF14` ×1 — `09`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `RAU8G02314.09`
  - `SHEET` ×1 — `1/1`

**Text entity samples (model space):**

  - `SEALING WATER PUMPS` _(layer: P-TEXT)_
  - `MAX` _(layer: P-TEXT)_
  - `SETPOINT TO PROCESS COOLING` _(layer: P-TEXT)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `PI-DIAGRAM RAU8G02317` _(layer: P-TEXT)_
  - `OCC` _(layer: P-TEXT)_
  - `PM3` _(layer: P-TEXT)_
  - `MILL SITE` _(layer: P-TEXT)_
  - `{\l\fArial|b0|i0;\T1;PLANT}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;3D\~MODEL}` _(layer: T-A-SHEET)_
  - `{\l\Ff0890111901.shx|b0|i0;\T1;True\P\l\Ff0890111901.shx|b0|i0;\T1;north}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Document\~status}` _(layer: T-A-SHEET)_
  - `CERTIFIED \~\~\~\~\~\~\~\~   22.12.2023` _(layer: T-A-SHEET)_
  - `FRESH WATER QUALITY REQUIREMENTS:` _(layer: P-TEXT)_
  - `Maximum particle size` _(layer: P-TEXT)_
  - `Pressure` _(layer: P-TEXT)_
  - `pH` _(layer: P-TEXT)_
  - `Suspended solids (SS)` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `MODESTD` (legible.shx), `ROMANT` (ROMANT.shx), `BasementLevel_S1$0$STANDARD` (ARIALN.TTF), `hz2` (romans99.shx), `SLDTEXTSTYLE18` (TXT), `ISO` (isocp.shx), `CTS_REV` (isocp.shx)

---

### 26. `RAU8G02315.10 Compressed Air system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 74303 |
| Entities (model space) | 7314 |
| Layers | 139 |
| Block definitions | 232 |
| Unique attribute tags | 53 |
| App ID fingerprint | PCAD ×28 | GENIUS ×22 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (15 records) |

**Title block fields:**

- `INF14`: 10
- `INF1`: 04.03.2022
- `INF2`: KLei
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02315.10
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTON PM3
- `TITLE1`: Compressed Air System
- `CAD`: AutoCAD
- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: KLei
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×2795, LINE×2338, TEXT×896, INSERT×829, SPLINE×189, CIRCLE×127, ARC×105, POINT×14

**Layers (139):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-INSTRU`, `P-REJECT`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-TANK_POS`, `P-VALVEPOS`, `P-LINEPOS`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `P-PRESSURIZED_AIR`, `P-CVPOS`, `T-A-SHEET`, `P-PUMPS`, `P-PUMP_POS`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-EQUIPMENTS`, `Defpoints`, `C_WAL_FI`, `M_TNK_FI`, `M_TNK_TH`, `M_EQU_FI`, `C_COL_TH`, `M_STL_FI`, `C_MOD_FI`, `AM_0`, `Text`, `M_STL_TH`, `AM_7`, `A_FRM_FI`, `M_TNK_TX`, `AM_3`, `M_EQU_TX`, `M_TNN_TH`, `M_TNN_FI` … +99 more

**Custom linetypes (38):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `PKV` — __ . __ . __ . __
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — ValmetIso __ __ __ __ __ __ __ __ __ __ __
  - `DDASH1` — ____ _ ____ _ ____ _  ____ _ ____ _ ____ _
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `SOLID` — _____________________________
  - `DDASH3` — ____________________  _  __________________
  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `IMPORT-GEN7A` — 
  - `DDASH2` — __________  _  __________  _  _________  _
  - `DURCHG` — DURCHG
  - `DASH3` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ _
  - `CONTINOUS` — Solid line
  - `CONTINUA` — Linea continua

**Block definitions (232):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A1100` (2 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `P7A1333` (5 entities)
  - `P7A1115` (10 entities)
  - `L_MILL_CONS` (6 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1304` (1 entities)
  - `P7A1207` (3 entities)
  - `PCAD_INF` (1 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `CTV_M_E1` (27 entities)
  - `KIPAS_VIITTA` (9 entities)
  - `CTS_RUB` (1 entities)
  - `CVR6F4E` (4 entities)
  - `PPI_0102B` (1 entities)
  - `PPI_1000A` (1 entities)
  - `VALMET_R_OTS` (409 entities)
  - `PI3117` (9 entities)
  - `PR-S777` (3 entities)
  - `P7A1106` (5 entities)
  - `P7A1118` (2 entities)
  - `P7A1A16` (10 entities)
  - `CV-S7B6` (4 entities)
  - `P7A1229` (3 entities)
  - `CV-S7F3` (5 entities)
  - `P7A1223` (5 entities)
  - … +202 more

**Most-used block inserts:**

  - `P7A1100` ×100
  - `PPI_1100A` ×88
  - `PPI_0900A` ×88
  - `PPI_052AA-25_0` ×87
  - `COLUM_N$` ×58
  - `PPI_0700A-25_0` ×45
  - `A$C5E972AA4` ×39
  - `P7A1304` ×22
  - `PPI_0802A-25_0` ×19
  - `PPI_1302A-25_0` ×17
  - `P7A1305` ×11
  - `PPI_1204A` ×10
  - `A$Cb4457391` ×10
  - `CTV_M_F2` ×9
  - `A$C3bf28058` ×5

**Attribute tags & sample values (53 unique tags):**

  - `COLUMN_NR` ×58 — `A`
  - `POSITIO` ×39 — `35-48T601`
  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `KLei`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `TYPE` ×10 — `EQUI`
  - `NAME` ×10 — `/3125E001_F`
  - `REF` ×10 — `=27277/84839`
  - `TEKSTI1` ×3 — `TO OCC`
  - `TEKSTI2` ×3
  - `KAAVIO` ×3 — `PI DIAGRAM`
  - `INF17` ×2
  - `INF15` ×1
  - `INF14` ×1 — `10`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `RAU8G02315.10`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A1`
  - `LYH` ×1 — `SHOTTON PM3`

**Text entity samples (model space):**

  - `{\l\fArial|b0|i0;\T1;PLANT}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;3D\~MODEL}` _(layer: T-A-SHEET)_
  - `{\l\Ff0890111901.shx|b0|i0;\T1;True\P\l\Ff0890111901.shx|b0|i0;\T1;north}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Document\~status}` _(layer: T-A-SHEET)_
  - `CERTIFIED  \~\~\~\~\~\~\~\~\~\~22.12.2023` _(layer: T-A-SHEET)_
  - `COMPRESSOR SUPPLIER DELIVERY` _(layer: P-OTHER)_
  - `MILL AIR NETWORK` _(layer: P-OTHER)_
  - `CHEMICAL FILTERING` _(layer: P-OTHER)_
  - `PI` _(layer: P-INSTRPOS_TEXTS)_
  - `9253` _(layer: P-INSTRPOS_TEXTS)_
  - `35-03` _(layer: P-INSTRPOS_TEXTS)_
  - `9252` _(layer: P-INSTRPOS_TEXTS)_
  - `9251` _(layer: P-INSTRPOS_TEXTS)_
  - `501` _(layer: P-INSTRPOS_TEXTS)_
  - `PC` _(layer: P-INSTRPOS_TEXTS)_
  - `500` _(layer: P-INSTRPOS_TEXTS)_
  - `VALVE NORMALLY CLOSED` _(layer: P-OTHER)_
  - `HOSE` _(layer: P-OTHER)_
  - `%%UINSTRUMENTS:` _(layer: P-OTHER)_
  - `%%UPUMP DATA:` _(layer: P-OTHER)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `MODESTD` (legible.shx), `ROMANT` (ROMANT.shx), `BasementLevel_S1$0$STANDARD` (ARIALN.TTF), `hz2` (romans99.shx), `SLDTEXTSTYLE18` (TXT), `CTS_REV` (isocp.shx), `ISO` (isocp.shx)

---

### 27. `RAU8G02316.10 Instrument Air.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 159633 |
| Entities (model space) | 6843 |
| Layers | 141 |
| Block definitions | 238 |
| Unique attribute tags | 54 |
| App ID fingerprint | PCAD ×28 | GENIUS ×22 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (13 records) |

**Title block fields:**

- `INF14`: 10
- `INF1`: 04.03.2022
- `INF2`: KLei
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02316.10
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTON PM3
- `TITLE1`: Instrument Air
- `CAD`: AutoCAD
- `SRVAS`: V
- `SROIK`: C
- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: KLei
- `TAR2`: SStr
- `MUUTOS2`: Updated

**Entities:** LWPOLYLINE×2598, LINE×2319, TEXT×789, INSERT×714, SPLINE×189, ARC×105, CIRCLE×95, POINT×14

**Layers (141):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-INSTRU`, `P-REJECT`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-VALVEPOS`, `P-MASS1`, `P-LINEPOS`, `P-MASS_UNPOS`, `P-VENTS_STARTUP`, `P-INSTRPOS_TEXTS`, `P-INSTRUMENT_AIR`, `P-PUMPS`, `P-PUMP_POS`, `P-FITTINGS`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-TANK_POS`, `P-PRESSURIZED_AIR`, `P-EQUIPMENTS`, `Defpoints`, `C_WAL_FI`, `M_TNK_FI`, `M_TNK_TH`, `M_EQU_FI`, `C_COL_TH`, `M_STL_FI`, `C_MOD_FI`, `AM_0`, `Text`, `M_STL_TH`, `AM_7`, `A_FRM_FI`, `M_TNK_TX`, `AM_3` … +101 more

**Custom linetypes (38):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `PKV` — __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — ValmetIso __ __ __ __ __ __ __ __ __ __ __
  - `DDASH1` — ____ _ ____ _ ____ _  ____ _ ____ _ ____ _
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `SOLID` — _____________________________
  - `DDASH3` — ____________________  _  __________________
  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `IMPORT-GEN7A` — 
  - `DDASH2` — __________  _  __________  _  _________  _
  - `DURCHG` — DURCHG
  - `DASH3` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ _
  - `CONTINOUS` — Solid line
  - `CONTINUA` — Linea continua

**Block definitions (238):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A1100` (2 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `P7A1333` (5 entities)
  - `P7A1115` (10 entities)
  - `PI-T-F754` (4 entities)
  - `L_MILL_CONS` (6 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1304` (1 entities)
  - `P7A1207` (3 entities)
  - `PR11A5B` (3 entities)
  - `PCAD_INF` (1 entities)
  - `CTV_M_E1` (27 entities)
  - `CTS_RUB` (1 entities)
  - `PI3117` (9 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1207A` (6 entities)
  - `PPI_1209A` (6 entities)
  - `PPI_1201A` (2 entities)
  - `PPI_1202A` (3 entities)
  - `PR-S777` (3 entities)
  - `P7A1106` (5 entities)
  - `P7A1118` (2 entities)
  - `P7A1A16` (10 entities)
  - `CV-S7B6` (4 entities)
  - `P7A1229` (3 entities)
  - `CV-S7F3` (5 entities)
  - `P7A1223` (5 entities)
  - … +208 more

**Most-used block inserts:**

  - `PPI_052AA-25_0` ×87
  - `PPI_0900A` ×76
  - `P7A1100` ×72
  - `COLUM_N$` ×58
  - `PPI_0700A-25_0` ×44
  - `A$C5E972AA4` ×39
  - `P7A1372` ×22
  - `PPI_0802A-25_0` ×19
  - `PPI_1302A-25_0` ×17
  - `PPI_1100A` ×13
  - `P7A1369` ×11
  - `A$Cb4457391` ×10
  - `P7A1304` ×9
  - `CTV_M_F2` ×9
  - `P7A1305` ×7

**Attribute tags & sample values (54 unique tags):**

  - `COLUMN_NR` ×58 — `A`
  - `POSITIO` ×39 — `35-48T601`
  - `A` ×33 — `10`
  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `KLei`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `TYPE` ×10 — `EQUI`
  - `NAME` ×10 — `/3125E001_F`
  - `REF` ×10 — `=27277/84839`
  - `TEKSTI1` ×4 — `COMPRESSED AIR`
  - `TEKSTI2` ×4
  - `KAAVIO` ×4 — `PID RAU8G02315`
  - `INF17` ×2
  - `INF15` ×1
  - `INF14` ×1 — `10`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `RAU8G02316.10`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A1`

**Text entity samples (model space):**

  - `{\l\fArial|b0|i0;\T1;PLANT}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;3D\~MODEL}` _(layer: T-A-SHEET)_
  - `{\l\Ff0890111901.shx|b0|i0;\T1;True\P\l\Ff0890111901.shx|b0|i0;\T1;north}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Document\~status}` _(layer: T-A-SHEET)_
  - `CERTIFIED \~\~\~\~\~\~\~\~\~\~ 22.12.2023` _(layer: T-A-SHEET)_
  - `VALVE NORMALLY CLOSED` _(layer: P-OTHER)_
  - `HOSE` _(layer: P-OTHER)_
  - `%%UINSTRUMENTS:` _(layer: P-OTHER)_
  - `%%UPUMP DATA:` _(layer: P-OTHER)_
  - `STEAM TRAP` _(layer: P-OTHER)_
  - `AIR VENT` _(layer: P-OTHER)_
  - `METAL HOSE` _(layer: P-OTHER)_
  - `SAFETY VALVE` _(layer: P-OTHER)_
  - `ORIFICE PLATE` _(layer: P-OTHER)_
  - `%%ULEGENDS:` _(layer: P-OTHER)_
  - `CONTROL ROOM INSTRUMENT WITH DCS CONTROL` _(layer: P-OTHER)_
  - `CONTROL ROOM INSTRUMENT WITH MCS CONTROL` _(layer: P-OTHER)_
  - `CONTROL ROOM INSTRUMENT` _(layer: P-OTHER)_
  - `LOCAL CONTROL PANEL INSTRUMENT` _(layer: P-OTHER)_
  - `LOCALLY MOUNTED INSTRUMENT` _(layer: P-OTHER)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `CTS_REV` (isocp.shx), `MODESTD` (legible.shx), `ROMANT` (ROMANT.shx), `BasementLevel_S1$0$STANDARD` (ARIALN.TTF), `hz2` (romans99.shx), `SLDTEXTSTYLE18` (TXT), `ISO` (isocp.shx)

---

### 28. `RAU8G02317.09 Sealing Water system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 11997 |
| Entities (model space) | 7767 |
| Layers | 139 |
| Block definitions | 248 |
| Unique attribute tags | 59 |
| App ID fingerprint | PCAD ×28 | GENIUS ×22 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (15 records) |

**Title block fields:**

- `INF14`: 09
- `INF1`: 04.03.2022
- `INF2`: KLei
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02317.09
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTON PM3
- `TITLE1`: Sealing Water system
- `CAD`: AutoCAD
- `MRK`: 09
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: KLei
- `TAR2`: SStr
- `MUUTOS2`: Updated
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×2797, LINE×2338, TEXT×1484, INSERT×717, SPLINE×189, ARC×105, CIRCLE×101, POINT×14

**Layers (139):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-INSTRU`, `P-WATER`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-TANK_POS`, `P-FLOOR`, `P-PUMP_POS`, `P-VALVEPOS`, `P-LINEPOS`, `P-EQUIPMENT_POS`, `P-CVPOS`, `P-INSTRPOS_TEXTS`, `P-DELIVERY_LIMIT`, `P-SEALING_WATER`, `P-REVISIONS`, `T-A-SHEET`, `P-FITTINGS`, `FIMPEC_COLOR`, `FIMPEC_BW`, `Defpoints`, `C_WAL_FI`, `M_TNK_FI`, `M_TNK_TH`, `M_EQU_FI`, `C_COL_TH`, `M_STL_FI`, `C_MOD_FI`, `AM_0`, `Text`, `M_STL_TH`, `AM_7`, `A_FRM_FI`, `M_TNK_TX`, `AM_3` … +99 more

**Custom linetypes (38):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `PKV` — __ . __ . __ . __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — ValmetIso __ __ __ __ __ __ __ __ __ __ __
  - `DDASH1` — ____ _ ____ _ ____ _  ____ _ ____ _ ____ _
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `SOLID` — _____________________________
  - `DDASH3` — ____________________  _  __________________
  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `IMPORT-GEN7A` — 
  - `DDASH2` — __________  _  __________  _  _________  _
  - `DURCHG` — DURCHG
  - `DASH3` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ _
  - `CONTINOUS` — Solid line
  - `CONTINUA` — Linea continua

**Block definitions (248):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `PPI_1204A` (6 entities)
  - `P7A1303` (1 entities)
  - `PRADF16` (3 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1206` (4 entities)
  - `PRADF6C` (3 entities)
  - `PRADF87` (3 entities)
  - `P7A1304` (1 entities)
  - `CVWE5AE` (4 entities)
  - `P7A1315` (4 entities)
  - `L_RIVI` (6 entities)
  - `PPI_1000A` (1 entities)
  - `PR21484` (2 entities)
  - `PR2148E` (2 entities)
  - `PR31D1A` (3 entities)
  - `PR1416C` (3 entities)
  - `PCAD_INF` (1 entities)
  - `PR1414D` (5 entities)
  - `p7a1370` (2 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PPI_1302A-25_0` (4 entities)
  - `P7A1106` (5 entities)
  - `KIPAS_VIITTA_M` (8 entities)
  - `KIPAS_VIITTA` (9 entities)
  - `PPI_0521A-25_0` (7 entities)
  - … +218 more

**Most-used block inserts:**

  - `RPALLO0` ×92
  - `PPI_052AA-25_0` ×87
  - `COLUM_N$` ×58
  - `PPI_0700A-25_0` ×42
  - `A$C5E972AA4` ×39
  - `PPI_0900A` ×29
  - `PPI_1302A-25_0` ×19
  - `PPI_0802A-25_0` ×19
  - `PPI_1100A` ×15
  - `P7A1369` ×14
  - `P7A1100` ×12
  - `A$Cb4457391` ×10
  - `PPI_1204A` ×8
  - `CTV_M_F2` ×8
  - `P7A0200` ×6

**Attribute tags & sample values (59 unique tags):**

  - `A` ×106 — `1.1`
  - `COLUMN_NR` ×58 — `A`
  - `POSITIO` ×39 — `35-48T601`
  - `NAME` ×13 — `/3125E001_F`
  - `TYPE` ×10 — `EQUI`
  - `REF` ×10 — `=27277/84839`
  - `MRK` ×9 — `00`
  - `KPL` ×9
  - `PVM` ×9 — `04.03.2022`
  - `MUU` ×9 — `KLei`
  - `TAR` ×9 — `SStr`
  - `MUUTOS` ×9 — `Preliminary`
  - `TEKSTI1` ×5 — `FRESH WATER`
  - `KAAVIO` ×5 — `PI-DIAGRAM RAU8G02314`
  - `TEKSTI2` ×4 — `PM3`
  - `NO.` ×3
  - `LINE_POSITION` ×3
  - `LEVEL` ×3
  - `HAND_VALVE` ×3
  - `INF17` ×2
  - `INFO` ×1 — `+0.000`
  - `INF15` ×1
  - `INF14` ×1 — `09`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`

**Text entity samples (model space):**

  - `STOP` _(layer: P-TEXT)_
  - `SEALING WATER` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `OCC` _(layer: P-TEXT)_
  - `PM3` _(layer: P-TEXT)_
  - `PI-DIAGRAM RAU8G02314` _(layer: P-TEXT)_
  - `COOLING WATER PUMP` _(layer: P-TEXT)_
  - `{\l\fArial|b0|i0;\T1;PLANT}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;3D\~MODEL}` _(layer: T-A-SHEET)_
  - `{\l\Ff0890111901.shx|b0|i0;\T1;True\P\l\Ff0890111901.shx|b0|i0;\T1;north}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;Document\~status}` _(layer: T-A-SHEET)_
  - `CERTIFIED \~\~\~\~\~\~\~\~\~\~ 22.12.2023` _(layer: T-A-SHEET)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `35-17L001` _(layer: P-EQUIPMENT_POS)_
  - `SEALING WATER FILTER 1` _(layer: P-EQUIPMENT_POS)_
  - `50 µm` _(layer: P-EQUIPMENT_POS)_
  - `35-17L002` _(layer: P-EQUIPMENT_POS)_
  - `FILTER 2 50 µm` _(layer: P-EQUIPMENT_POS)_
  - `NO` _(layer: P-TEXT)_
  - `POSITION` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `MODESTD` (legible.shx), `ROMANT` (ROMANT.shx), `BasementLevel_S1$0$STANDARD` (ARIALN.TTF), `hz2` (romans99.shx), `SLDTEXTSTYLE18` (TXT), `ISO` (isocp.shx), `CTS_REV` (isocp.shx)

---

### 29. `RAU8G02327.09 Heating water.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 14356 |
| Entities (model space) | 12611 |
| Layers | 35 |
| Block definitions | 95 |
| Unique attribute tags | 46 |
| App ID fingerprint | PCAD ×28 | other: CTS_INFO, CTS_SHEET, CTS_TXT |
| Connectivity | ✅ LIN_FROM/LIN_TO (112 records) |

**Title block fields:**

- `INF14`: 09
- `INF1`: 13.05.2022
- `INF2`: JPul
- `INF3`: 13.05.2022
- `INF4`: SStr
- `INF5`: 13.05.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02327.09
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: Heating Water system
- `CAD`: AutoCAD
- `MRK`: 09
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: UPDATED
- `MRK2`: 01
- `PVM2`: 15.06.2022
- `MUU2`: JPul
- `TAR2`: SStr
- `MUUTOS2`: UPDATED
- `SRVAS`: V
- `SROIK`: C

**Entities:** LWPOLYLINE×4826, INSERT×3896, TEXT×3449, CIRCLE×240, LINE×196, MTEXT×4

**Layers (35):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-AIR`, `P-INSTRPOS`, `P-PUMPS`, `P-VENTS`, `P-SYMB`, `P-DELIVERY_LIMIT`, `P-EQUIPMENT_POS`, `P-INSTRU`, `P-HEATING_WATER`, `P-TEXT`, `P-PUMP_POS`, `P-EQUIPMENTS`, `P-CHEM_PURE_WATER`, `P-CHEMICAL`, `P-TANK_POS`, `P-LINEPOS`, `P-VALVEPOS`, `P-WARM_WATER`, `P-CVPOS`, `P-INSTRPOS_TEXTS`, `P-FAN_POS`, `P-FITTINGS`, `P-STEAM1`, `P-WATER`, `P-COND`, `P-REVISIONS`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-UNIT`, `P-MARKBALL`, `Defpoints`

**Custom linetypes (8):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `PKV` — __ . __ . __ . __

**Block definitions (95):**

  - `CTS_INFP` (1 entities)
  - `PPI_1200A` (1 entities)
  - `P7A1325` (5 entities)
  - `P7A1100` (2 entities)
  - `P7A5102` (8 entities)
  - `P7A0200` (3 entities)
  - `P7A1305` (1 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_0101B` (2 entities)
  - `P7A1172` (3 entities)
  - `P7A1106` (5 entities)
  - `P7A1105` (2 entities)
  - `P7A1209` (15 entities)
  - `P7A1212` (2 entities)
  - `P7A1A16` (10 entities)
  - `P7A0020` (6 entities)
  - `P7A1208` (5 entities)
  - `P7A1214` (2 entities)
  - `P7A0140` (3 entities)
  - `P7A1383` (3 entities)
  - `PR1B232` (3 entities)
  - `PR1B240` (3 entities)
  - `CV1B2FB` (4 entities)
  - `P7A1188` (3 entities)
  - `PR1B57A` (3 entities)
  - `P7A1341` (13 entities)
  - `PPI_0400A-25` (7 entities)
  - `PPI_0700A-25` (4 entities)
  - `P7A1215` (2 entities)
  - `P7A1210` (1 entities)
  - … +65 more

**Most-used block inserts:**

  - `PPI_0900A` ×628
  - `P7A1305` ×615
  - `P7A1210` ×336
  - `PPI_0101B` ×269
  - `P7A1100` ×268
  - `PPI_1204A` ×204
  - `P7A0214` ×144
  - `PPI_060AA-25` ×144
  - `P7A1172` ×136
  - `P7A1212` ×114
  - `PPI_1100A` ×111
  - `P7A5102` ×96
  - `PPI_1200A` ×90
  - `P7A1304` ×76
  - `PRR4AF3` ×72

**Attribute tags & sample values (46 unique tags):**

  - `MRK` ×9 — `00`
  - `KPL` ×9
  - `PVM` ×9 — `13.05.2022`
  - `MUU` ×9 — `JPul`
  - `TAR` ×9 — `SStr`
  - `MUUTOS` ×9 — `UPDATED`
  - `A` ×6 — `09`
  - `INF17` ×2
  - `INF15` ×1
  - `INF14` ×1 — `09`
  - `INF1` ×1 — `13.05.2022`
  - `INF2` ×1 — `JPul`
  - `INF3` ×1 — `13.05.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `13.05.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `RAU8G02327.09`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A1`
  - `LYH` ×1 — `SHOTTONPM3`
  - `TITLE1` ×1 — `Heating Water system`
  - `TITLE2` ×1
  - `REFERENCE` ×1
  - `SUPERSEDES` ×1
  - `WORK` ×1
  - `CAD` ×1 — `AutoCAD`
  - `PROCUCT` ×1

**Text entity samples (model space):**

  - `VALMET` _(layer: P-OTHER)_
  - `PM3` _(layer: P-OTHER)_
  - `+54°C` _(layer: P-TEXT)_
  - `+34°C` _(layer: P-TEXT)_
  - `RESERVATION FOR` _(layer: P-OTHER)_
  - `BIOCIDE FEED` _(layer: P-OTHER)_
  - `OPENING PRESSURE +6,0 BAR` _(layer: P-TEXT)_
  - `CAPACITY 2,6 kg water/s` _(layer: P-SYMB)_
  - `+200%%DC` _(layer: P-TEXT)_
  - `+230%%DC` _(layer: P-TEXT)_
  - `EXPANSION VOL. 0,95 m3` _(layer: P-TEXT)_
  - `INITIAL PRESSURE 2,0 BAR` _(layer: P-TEXT)_
  - `STEAM / WATER` _(layer: P-SYMB)_
  - `STEAM RAU8F00286` _(layer: P-TEXT)_
  - `6,6 kg/s` _(layer: P-TEXT)_
  - `80 % WATER / 20% GLYCOL` _(layer: P-TANK_POS)_
  - `(TOTAL)` _(layer: P-TEXT)_
  - `A` _(layer: P-VALVEPOS)_
  - `204,2 l/s  2,12 m/s  96 Pa/m` _(layer: P-TEXT)_
  - `DN350, (16128 kW)` _(layer: P-TEXT)_

**Text styles:** `Standard` (txt), `ROMANS` (ROMANS.SHX), `ARIALN` (ARIALN.TTF), `ARIAL` (arial.ttf), `AUDIT_D_220106164814-0` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 30. `RAU8G02334.07 Connections Between Departments.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 1424 |
| Entities (model space) | 379 |
| Layers | 15 |
| Block definitions | 13 |
| Unique attribute tags | 43 |
| App ID fingerprint | PCAD ×16 | other: CTS_INFO, CTS_SHEET, GradientColor1ACI |
| Connectivity | ✅ LIN_FROM/LIN_TO (84 records) |

**Title block fields:**

- `INF14`: 07
- `INF1`: 15.06.2022
- `INF2`: KLei
- `INF3`: 15.06.2022
- `INF4`: SStr
- `INF5`: 15.06.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02334.07
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTON PM3
- `TITLE1`: CONNECTIONS BETWEEN DEPARTMENTS
- `CAD`: AutoCAD
- `MRK`: 07
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 19.08.2022
- `MUU2`: KLei
- `TAR2`: SStr
- `MUUTOS2`: Updated

**Entities:** TEXT×153, INSERT×142, LWPOLYLINE×78, LINE×4, MTEXT×2

**Layers (15):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-BUILDING`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-MASS1`, `P-LINEPOS`, `P-SYMB`, `P-TEXT`, `P-DELIVERY_LIMIT`, `P-REVISIONS`, `P-WATER`, `Defpoints`

**Custom linetypes (6):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __

**Block definitions (13):**

  - `CTS_INFP` (1 entities)
  - `FMS_T70_E` (29 entities)
  - `LG-FMPCH` (7 entities)
  - `VALMET_R_OTS` (409 entities)
  - `CTV_M_E1` (27 entities)
  - `SYMBOL4` (44 entities)
  - `CTS_INFT` (1 entities)
  - `SYMBOL3` (43 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1305` (1 entities)
  - `P7A1372` (4 entities)
  - `CTV_M_F2` (15 entities)
  - `CTS_RUB` (1 entities)

**Most-used block inserts:**

  - `PPI_1100A` ×83
  - `P7A1305` ×46
  - `CTV_M_F2` ×6
  - `CTS_INFP` ×1
  - `FMS_T70_E` ×1
  - `VALMET_R_OTS` ×1
  - `SYMBOL4` ×1
  - `SYMBOL3` ×1
  - `CTV_M_E1` ×1
  - `CTS_RUB` ×1

**Attribute tags & sample values (43 unique tags):**

  - `MRK` ×7 — `00`
  - `KPL` ×7
  - `PVM` ×7 — `15.06.2022`
  - `MUU` ×7 — `KLei`
  - `TAR` ×7 — `SStr`
  - `MUUTOS` ×7 — `Preliminary`
  - `INF17` ×2
  - `INF15` ×1
  - `INF14` ×1 — `07`
  - `INF1` ×1 — `15.06.2022`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `15.06.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `15.06.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `RAU8G02334.07`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A1`
  - `LYH` ×1 — `SHOTTON PM3`
  - `TITLE1` ×1 — `CONNECTIONS BETWEEN DEPARTMENTS`
  - `TITLE2` ×1
  - `REFERENCE` ×1
  - `SUPERSEDES` ×1
  - `WORK` ×1
  - `CAD` ×1 — `AutoCAD`
  - `PROCUCT` ×1
  - `SCALE` ×1

**Text entity samples (model space):**

  - `STEAM` _(layer: P-TEXT)_
  - `CONDENSATE` _(layer: P-TEXT)_
  - `WHITE WATER` _(layer: P-TEXT)_
  - `COMPRESSED AIR` _(layer: P-TEXT)_
  - `INSTRUMENT AIR` _(layer: P-TEXT)_
  - `SF STOCK` _(layer: P-TEXT)_
  - `BROKE FROM BROKE TOWER` _(layer: P-TEXT)_
  - `BROKE REJECT TANK` _(layer: P-TEXT)_
  - `LF STOCK` _(layer: P-TEXT)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `CHEMICAL BUILDING` _(layer: P-TEXT)_
  - `PM3` _(layer: P-TEXT)_
  - `OCC` _(layer: P-TEXT)_
  - `COMBINED HEAT POWER` _(layer: P-TEXT)_
  - `BOILER BUILDING` _(layer: P-TEXT)_
  - `DYE BROWN` _(layer: P-TEXT)_
  - `BENTONITE` _(layer: P-TEXT)_
  - `CPAM` _(layer: P-TEXT)_
  - `SURFACE SIZE` _(layer: P-TEXT)_
  - `FRESH WATER` _(layer: P-TEXT)_

**Text styles:** `Standard` (arial.ttf), `ISOCP` (isocp.shx), `ARIAL` (arial.ttf), `ARIALN` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx), `ROMANS` (ROMANS.SHX)

---

### 31. `RAU8G02456.00 Washing water utility pipe route.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `kaisa.leino` |
| Objects | 38841 |
| Entities (model space) | 1129 |
| Layers | 131 |
| Block definitions | 220 |
| Unique attribute tags | 45 |
| App ID fingerprint | PCAD ×15 | GENIUS ×22 | other: CTS_INFO, CTS_SHEET, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `MRK`: 02
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: UPDATED
- `MRK2`: 01
- `SRVAS`: V
- `SROIK`: C
- `INF14`: 00
- `INF1`: 04.03.2022
- `INF2`: KLei
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: RAU8G02456.00
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTON PM3
- `TITLE1`: Washing water pipe route
- `CAD`: AutoCAD

**Entities:** TEXT×424, LWPOLYLINE×327, INSERT×281, LINE×45, CIRCLE×44, MTEXT×5, POLYLINE×3

**Layers (131):**  
`0`, `P-A-SHEET`, `P-OTHER`, `Defpoints`, `P-TANK_POS`, `P-PUMP_POS`, `C_WAL_FI`, `M_TNK_FI`, `M_TNK_TH`, `M_EQU_FI`, `C_COL_TH`, `M_STL_FI`, `C_MOD_FI`, `AM_0`, `Text`, `M_STL_TH`, `AM_7`, `A_FRM_FI`, `M_TNK_TX`, `AM_3`, `M_EQU_TX`, `M_TNN_TH`, `M_TNN_FI`, `L17`, `MUOTOV`, `MITOITUS`, `Lüftung_airinotec-air_AM_1`, `T-TEXT`, `T-FOUNDATION`, `T-STAIRWAY`, `T-EQUIP`, `T-TANKS`, `T-STEELSTR`, `T-DIM`, `T-CHANNEL`, `AM_8`, `LA`, `PKV`, `MI`, `T-EQUIPMENT` … +91 more

**Custom linetypes (38):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — ValmetIso __ __ __ __ __ __ __ __ __ __ __
  - `DDASH1` — ____ _ ____ _ ____ _  ____ _ ____ _ ____ _
  - `CENTERX2` — ________  __  ________  __  ________  __  _____
  - `SOLID` — _____________________________
  - `DDASH3` — ____________________  _  __________________
  - `DASHEDX2` — ____  ____  ____  ____  ____  ____  ____  ____ 
  - `IMPORT-GEN7A` — 
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `DDASH2` — __________  _  __________  _  _________  _
  - `DURCHG` — DURCHG
  - `DASH3` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ _
  - `CONTINOUS` — Solid line
  - `CONTINUA` — Linea continua
  - `GESTR2` — -isb cad-
  - `DASH4` — ___  ___  ___  ___  ___  ___  ___  ___  ___

**Block definitions (220):**

  - `CTS_INFP` (1 entities)
  - `A$9427F` (2 entities)
  - `A$1684AE` (5825 entities)
  - `A$C3bf28058` (99 entities)
  - `PPI_052AA-25_0` (4 entities)
  - `A$DC5CC` (1 entities)
  - `A$C63626245` (23 entities)
  - `A$C7f793316` (125 entities)
  - `COLUM_N$` (2 entities)
  - `cond unit` (6 entities)
  - `BasementLevel_S1$0$76429#94529` (53 entities)
  - `A$2966C1` (1359 entities)
  - `Päälauhdesäiliö_8m3` (174 entities)
  - `A$A0509` (128 entities)
  - `A$A113E` (157 entities)
  - `A$38E68` (129 entities)
  - `A$40EAC` (133 entities)
  - `A$C4402237f` (137 entities)
  - `A$1BC72` (153 entities)
  - `A$C50e7ef41` (136 entities)
  - `A$C14ddfd30` (125 entities)
  - `A$C294cf055` (105 entities)
  - `A$Cdc21502a` (99 entities)
  - `A$Cb4457391` (68 entities)
  - `A$C3c686691` (22 entities)
  - `A$C5ab06758` (25 entities)
  - `A$C2734936a` (9328 entities)
  - `fdfdsa` (76 entities)
  - `A$Cf60057c5` (11338 entities)
  - `A$C32576` (17 entities)
  - … +190 more

**Most-used block inserts:**

  - `P7A1100` ×74
  - `PPI_0900A` ×71
  - `PPI_1100A` ×71
  - `A$3BF68` ×24
  - `CTV_M_F2` ×7
  - `PR-S8AD` ×2
  - `P7A1305` ×2
  - `P7A1304` ×2
  - `CTS_INFP` ×1
  - `A$3A8EA` ×1
  - `CTV_M_E1` ×1
  - `PI3117` ×1
  - `PR-S777` ×1
  - `P7A1106` ×1
  - `P7A1118` ×1

**Attribute tags & sample values (45 unique tags):**

  - `MRK` ×8 — `00`
  - `KPL` ×8
  - `PVM` ×8 — `22.12.2023`
  - `MUU` ×8 — `JLin`
  - `TAR` ×8 — `SStr`
  - `MUUTOS` ×8 — `UPDATED`
  - `INF17` ×2
  - `MRK2` ×1 — `01`
  - `KPL2` ×1
  - `PVM2` ×1
  - `MUU2` ×1
  - `TAR2` ×1
  - `MUUTOS2` ×1
  - `SRVAS` ×1 — `V`
  - `SROIK` ×1 — `C`
  - `INF15` ×1
  - `INF14` ×1 — `00`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `KLei`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `RAU8G02456.00`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A1`
  - `LYH` ×1 — `SHOTTON PM3`

**Text entity samples (model space):**

  - `VALVE NORMALLY CLOSED` _(layer: P-OTHER)_
  - `HOSE` _(layer: P-OTHER)_
  - `%%UINSTRUMENTS:` _(layer: P-OTHER)_
  - `%%UPUMP DATA:` _(layer: P-OTHER)_
  - `STEAM TRAP` _(layer: P-OTHER)_
  - `AIR VENT` _(layer: P-OTHER)_
  - `METAL HOSE` _(layer: P-OTHER)_
  - `SAFETY VALVE` _(layer: P-OTHER)_
  - `ORIFICE PLATE` _(layer: P-OTHER)_
  - `%%ULEGENDS:` _(layer: P-OTHER)_
  - `CONTROL ROOM INSTRUMENT WITH DCS CONTROL` _(layer: P-OTHER)_
  - `CONTROL ROOM INSTRUMENT WITH MCS CONTROL` _(layer: P-OTHER)_
  - `CONTROL ROOM INSTRUMENT` _(layer: P-OTHER)_
  - `LOCAL CONTROL PANEL INSTRUMENT` _(layer: P-OTHER)_
  - `LOCALLY MOUNTED INSTRUMENT` _(layer: P-OTHER)_
  - `QUALITY CONTROL SYSTEM (QCS)` _(layer: P-OTHER)_
  - `HAND VALVE` _(layer: P-OTHER)_
  - `CHECK VALVE` _(layer: P-OTHER)_
  - `PRESSURE REDUCING VALVE` _(layer: P-OTHER)_
  - `%%UDELIVERY LIMITS:` _(layer: P-OTHER)_

**Text styles:** `Standard` (arial.ttf), `ROMANS` (ROMANS.SHX), `ISOCP` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `MODESTD` (legible.shx), `ROMANT` (ROMANT.shx), `BasementLevel_S1$0$STANDARD` (ARIALN.TTF), `hz2` (romans99.shx), `SLDTEXTSTYLE18` (TXT), `ISO` (isocp.shx), `ARIALN` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF)

---

### 32. `STOD206336.11 Stock Preparation and Mixing area.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 7627 |
| Entities (model space) | 4816 |
| Layers | 33 |
| Block definitions | 118 |
| Unique attribute tags | 69 |
| App ID fingerprint | PCAD ×36 | GENIUS ×2 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (150 records) |

**Title block fields:**

- `TUNNUS`: LI
- `INF14`: 11
- `INF1`: 04.03.2022
- `INF2`: JLep
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: STOD206336.11
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: Stock Preparation and Mixing area
- `CAD`: AutoCAD
- `MRK`: 11
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLep
- `TAR2`: SStr
- `MUUTOS2`: Certified
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×1686, INSERT×1580, LWPOLYLINE×1492, LINE×41, CIRCLE×8, MTEXT×5, POLYLINE×4

**Layers (33):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-WATER`, `P-SYMB`, `P-VENTS`, `P-TANK_POS`, `P-PUMPS`, `P-INSTRU`, `P-PUMP_POS`, `P-INSTRPOS`, `P-TEXT`, `P-FLOOR`, `P-VALVEPOS`, `P-REJECT`, `PI0ATT`, `P-EQUIPMENTS`, `P-EQUIPMENT_POS`, `P-MASS1`, `P-CVPOS`, `P-ADDITIVE`, `P-LINEPOS`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `P-AGITATOR_POS`, `P-SEALING_WATER`, `P-WHITE_WATER`, `T-A-SHEET`, `P-DELIVERY_LIMIT`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-REVISIONS`, `Defpoints`

**Custom linetypes (8):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `PKV` — __ . __ . __ . __

**Block definitions (118):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `PPI_0102B` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1304` (1 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `P7A1303` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_0100X` (19 entities)
  - `P7A1105` (2 entities)
  - `P7A1252` (3 entities)
  - `P7A1120` (4 entities)
  - `P7A1212` (2 entities)
  - `PPI_1000A` (1 entities)
  - `P7A1309` (2 entities)
  - `P7A1300` (3 entities)
  - `PPI_1100A` (1 entities)
  - `PCAD_INF` (1 entities)
  - `C-85D9` (8 entities)
  - `P7A1210` (1 entities)
  - `CTS_INFT` (1 entities)
  - `PRXA1B2` (3 entities)
  - `PRNF3CE` (3 entities)
  - `CTS_INFI` (1 entities)
  - `P7A1315` (4 entities)
  - `PPI_0700A-25_0` (4 entities)
  - `PPI_0802A-25_0` (4 entities)
  - … +88 more

**Most-used block inserts:**

  - `P7A1305` ×187
  - `PPI_0900A` ×186
  - `PPI_1204A` ×158
  - `PPI_1100A` ×152
  - `P7A1304` ×98
  - `P7A1100` ×85
  - `PPI_0102B` ×74
  - `PRXA1B2` ×68
  - `PPI_1000A` ×62
  - `PPI_1200A` ×51
  - `A$5232E` ×30
  - `P7A1120` ×26
  - `P7A1309` ×24
  - `PPI_0100X` ×21
  - `P7A1105` ×20

**Attribute tags & sample values (69 unique tags):**

  - `A` ×28 — `11`
  - `TEKSTI1` ×22 — `35-25FFC-513`
  - `TEKSTI2` ×22 — `SAVE ALL SWEETENER FLOW`
  - `KAAVIO` ×22 — `PI DIAGRAM STOD206338`
  - `ANTNIMI` ×21
  - `ANTPOS` ×21 — `1107`
  - `ANTPNIM` ×21
  - `ANTDN` ×21
  - `ANTPN` ×21
  - `ANTMAT` ×21
  - `ANTLIIT` ×21
  - `ANTPITU` ×21
  - `ANTERI1` ×21
  - `ANTPHAV` ×21
  - `ANTSIPO` ×21
  - `ANTAILY` ×21
  - `ANTTIH` ×21
  - `ANTALUE` ×21
  - `ANTKPAI` ×21
  - `ANTLMP` ×21
  - `ANTYLAM` ×21
  - `ANTLISA` ×21
  - `MRK` ×11 — `00`
  - `KPL` ×11
  - `PVM` ×11 — `04.03.2022`
  - `MUU` ×11 — `JLep`
  - `TAR` ×11 — `SStr`
  - `MUUTOS` ×11 — `Preliminary`
  - `TUNNUS` ×9 — `PI`
  - `INFO` ×3 — `+0.000`

**Text entity samples (model space):**

  - `SETPOINT` _(layer: P-TEXT)_
  - `STOCK RECIPE` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `STOCK TO FORMER` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `-4- () []` _(layer: P-LINEPOS)_
  - `BASIS WEIGHT` _(layer: P-TEXT)_
  - `CONTROL` _(layer: P-TEXT)_
  - `FROM QCS` _(layer: P-TEXT)_
  - `S` _(layer: P-TEXT)_
  - `SEALING WATER` _(layer: P-LINEPOS)_
  - `START SEQUENCE` _(layer: P-TEXT)_
  - `GEAR` _(layer: P-TEXT)_
  - `COOLING WATER` _(layer: P-TEXT)_
  - `STOCK TOWER DILUTION` _(layer: P-TEXT)_
  - `PM3` _(layer: P-OTHER)_
  - `COOLING WATER RETURN` _(layer: P-TEXT)_
  - `C` _(layer: P-DELIVERY_LIMIT)_
  - `V` _(layer: P-DELIVERY_LIMIT)_
  - `VFD` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `MtXpl_isocp_shx` (ARIALN.TTF), `ISO` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 33. `STOD206337.11 Approach Flow System.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 8684 |
| Entities (model space) | 4584 |
| Layers | 36 |
| Block definitions | 142 |
| Unique attribute tags | 50 |
| App ID fingerprint | PCAD ×35 | GENIUS ×2 | other: CTS_INFO, CTS_SHEET, CTS_INF_BLK |
| Connectivity | ✅ LIN_FROM/LIN_TO (118 records) |

**Title block fields:**

- `INF14`: 11
- `INF1`: 04.03.2022
- `INF2`: JLep
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: STOD206337.11
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: Approach Flow System
- `CAD`: AutoCAD
- `MRK`: 11
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLep
- `TAR2`: SStr
- `MUUTOS2`: Certified
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×1530, LWPOLYLINE×1509, INSERT×1468, LINE×49, POLYLINE×9, CIRCLE×8, ARC×6, MTEXT×5

**Layers (36):**  
`0`, `P-A-SHEET`, `P-OTHER`, `P-WATER`, `P-SYMB`, `P-VENTS`, `P-TANK_POS`, `P-PUMPS`, `P-INSTRU`, `P-PUMP_POS`, `P-INSTRPOS`, `P-TEXT`, `P-FLOOR`, `P-VALVEPOS`, `P-REJECT`, `P-EQUIPMENTS`, `P-EQUIPMENT_POS`, `P-MASS1`, `P-AIR`, `P-CVPOS`, `P-ADDITIVE`, `P-LINEPOS`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `P-DELIVERY_LIMIT`, `MACHINE`, `P-REVISIONS`, `P-STEAM1`, `P-MOTOR_POS`, `P-SEALING_WATER`, `P-LOW_P_STEAM`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-PTERMINAL_POS`, `Defpoints`

**Custom linetypes (7):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `PKV` — __ . __ . __ . __

**Block definitions (142):**

  - `CTS_INFP` (1 entities)
  - `P7A1305` (1 entities)
  - `PPI_0102B` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1304` (1 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `P7A1303` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1207A` (6 entities)
  - `P7A1105` (2 entities)
  - `P7A1252` (3 entities)
  - `PR15BC0` (3 entities)
  - `PR2BF0E` (3 entities)
  - `PR37724` (3 entities)
  - `PR3773D` (3 entities)
  - `P7A1212` (2 entities)
  - `CV37766` (4 entities)
  - `PR377BA` (3 entities)
  - `PR377CC` (3 entities)
  - `CV377E1` (4 entities)
  - `CV37838` (4 entities)
  - `CV37858` (4 entities)
  - `PR20A4F` (3 entities)
  - `P7A1333` (5 entities)
  - `CV378D0` (4 entities)
  - `PPI_1000A` (1 entities)
  - `PR3793E` (3 entities)
  - … +112 more

**Most-used block inserts:**

  - `PPI_0900A` ×178
  - `P7A1305` ×177
  - `PPI_1100A` ×116
  - `PPI_1204A` ×114
  - `p7a1370` ×95
  - `P7A1100` ×93
  - `PPI_0102B` ×77
  - `P7A1304` ×48
  - `P7A1210` ×43
  - `PPI_1000A` ×39
  - `PPI_1200A` ×39
  - `P7A1212` ×31
  - `P7A1309` ×25
  - `P7A1300` ×20
  - `PPI_1700A` ×20

**Attribute tags & sample values (50 unique tags):**

  - `TEKSTI1` ×33 — `CPAM`
  - `TEKSTI2` ×33 — `35-26T601`
  - `KAAVIO` ×33 — `PI-DIAGRAM PCSG028670`
  - `INFO` ×11 — `+0.000`
  - `MRK` ×11 — `00`
  - `KPL` ×11
  - `PVM` ×11 — `04.03.2022`
  - `MUU` ×11 — `JLep`
  - `TAR` ×11 — `SStr`
  - `MUUTOS` ×11 — `Preliminary`
  - `A` ×9 — `11`
  - `INF17` ×2
  - `INF15` ×1
  - `INF14` ×1 — `11`
  - `INF1` ×1 — `04.03.2022`
  - `INF2` ×1 — `JLep`
  - `INF3` ×1 — `04.03.2022`
  - `INF4` ×1 — `SStr`
  - `INF5` ×1 — `04.03.2022`
  - `INF6` ×1 — `HSoi`
  - `PROJECT1` ×1 — `Shotton Mill Ltd`
  - `PROJECT2` ×1 — `Shotton Paper Mill, United Kingdom`
  - `PROJECT3` ×1 — `Shotton PM3`
  - `DRAWINGID` ×1 — `STOD206337.11`
  - `SHEET` ×1 — `1/1`
  - `ARKKI` ×1 — `A1`
  - `LYH` ×1 — `SHOTTONPM3`
  - `TITLE1` ×1 — `Approach Flow System`
  - `TITLE2` ×1
  - `REFERENCE` ×1

**Text entity samples (model space):**

  - `SEALING WATER` _(layer: P-LINEPOS)_
  - `S` _(layer: P-TEXT)_
  - `WATER TO FORMER` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `DILUTION CIRCULATION` _(layer: P-TEXT)_
  - `DEAERATION` _(layer: P-TEXT)_
  - `DILUTION CLEANING` _(layer: P-TEXT)_
  - `CHEMICAL CLEANING` _(layer: P-TEXT)_
  - `STOCK TO FORMER` _(layer: P-TEXT)_
  - `DILUTION HEADER` _(layer: P-TEXT)_
  - `BACK PLY HEADER` _(layer: P-TEXT)_
  - `TOP PLY HEADER` _(layer: P-TEXT)_
  - `PCSG016682A` _(layer: P-EQUIPMENT_POS)_
  - `30325TC-238` _(layer: P-TEXT)_
  - `DN65` _(layer: P-TEXT)_
  - `PI-DIAGRAM` _(layer: P-EQUIPMENT_POS)_
  - `PRESSURE SETPOINT` _(layer: P-TEXT)_
  - `HEADBOX BACK PLY FLOW` _(layer: P-TEXT)_
  - `RM3` _(layer: P-TEXT)_

**Text styles:** `Standard` (ARIALN.TTF), `ROMANS` (romans.shx), `ISOCP` (ARIALN.TTF), `ARIAL` (arial.ttf), `ARIALN` (ARIALN.TTF), `MtXpl_isocp_shx` (isocp.shx), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (f0890111901), `CTS_REV` (isocp.shx)

---

### 34. `STOD206338.11_White Water system.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `jani.linden` |
| Objects | 4929 |
| Entities (model space) | 2588 |
| Layers | 36 |
| Block definitions | 110 |
| Unique attribute tags | 68 |
| App ID fingerprint | PCAD ×33 | other: FOCUSPI_1_3, FOCUSPI, DCO15 |
| Connectivity | ✅ LIN_FROM/LIN_TO (101 records) |

**Title block fields:**

- `INF14`: 11
- `INF1`: 04.03.2022
- `INF2`: JLep
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: STOD206338.11
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: White Water System
- `CAD`: AutoCAD
- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLep
- `TAR2`: SStr
- `MUUTOS2`: Certified
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×920, LWPOLYLINE×806, INSERT×788, LINE×49, CIRCLE×12, MTEXT×5, POLYLINE×4, HATCH×3

**Layers (36):**  
`0`, `PI0ATT`, `P-INSTRU`, `P-MASS1`, `P-REJECT`, `P-WATER`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-OTHER`, `P-PUMP_POS`, `P-VALVEPOS`, `P-LINEPOS`, `P-TANK_POS`, `P-CVPOS`, `P-AGITATOR_POS`, `P-EQUIPMENT_POS`, `P-INSTRPOS_TEXTS`, `P-ADDITIVE`, `P-FLOOR`, `P-FITTINGS`, `P-A-SHEET`, `P-DELIVERY_LIMIT`, `P-SEALING_WATER`, `P-WHITE_WATER`, `P-WARM_WATER`, `P-MOTOR_POS`, `T-A-SHEET`, `P-REVISIONS`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-HATCH`, `P-SENSOR_POS`, `Defpoints`

**Custom linetypes (7):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium
  - `PKV` — __ . __ . __ . __

**Block definitions (110):**

  - `PPI_0100B` (19 entities)
  - `CTS_INFP` (1 entities)
  - `P7A1105` (2 entities)
  - `P7A1252` (3 entities)
  - `P7A1333` (5 entities)
  - `P7A1305` (1 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `P7A1120` (4 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1304` (1 entities)
  - `PPI_1000A` (1 entities)
  - `PR75B27` (3 entities)
  - `PCAD_INF` (1 entities)
  - `PPI_0102B` (1 entities)
  - `P7A1309` (2 entities)
  - `PR5634E` (3 entities)
  - `PR5636E` (3 entities)
  - `PRA71D2` (3 entities)
  - `PRA7204` (3 entities)
  - `P7A1210` (1 entities)
  - `PR490AD` (3 entities)
  - `CV49BB0` (4 entities)
  - `PPI_1205A` (7 entities)
  - `CV5A71C` (4 entities)
  - `CV5A730` (4 entities)
  - … +80 more

**Most-used block inserts:**

  - `PPI_0900A` ×102
  - `P7A1305` ×100
  - `PPI_1100A` ×100
  - `P7A1100` ×48
  - `PPI_1204A` ×43
  - `P7A1304` ×33
  - `PPI_0102B` ×33
  - `PPI_1000A` ×29
  - `P7A0200` ×16
  - `P7A13E8` ×16
  - `PRA71D2` ×15
  - `KIPAS_VIITTA` ×15
  - `PPI_0521A-25_0` ×15
  - `P7A1252` ×13
  - `PPI_1200A` ×12

**Attribute tags & sample values (68 unique tags):**

  - `TEKSTI1` ×30 — `OCC MAKE-UP WATER`
  - `TEKSTI2` ×30 — `THICKENING`
  - `KAAVIO` ×30 — `PI-DIAGRAM STOD206343`
  - `MRK` ×10 — `11`
  - `KPL` ×10
  - `PVM` ×10 — `4.6.2025`
  - `MUU` ×10 — `JLin`
  - `TAR` ×10 — `KVil`
  - `MUUTOS` ×10 — `Updated`
  - `INFO` ×2 — `+0.000`
  - `INF17` ×2
  - `A` ×2 — `11`
  - `ANTNIMI` ×1
  - `ANTPOS` ×1
  - `ANTPNIM` ×1
  - `ANTDN` ×1
  - `ANTPN` ×1
  - `ANTMAT` ×1
  - `ANTLIIT` ×1
  - `ANTPITU` ×1
  - `ANTERI1` ×1
  - `ANTPHAV` ×1
  - `ANTSIPO` ×1
  - `ANTAILY` ×1
  - `ANTTIH` ×1
  - `ANTALUE` ×1
  - `ANTKPAI` ×1
  - `ANTLMP` ×1
  - `ANTYLAM` ×1
  - `ANTLISA` ×1

**Text entity samples (model space):**

  - `LOCAL/` _(layer: P-TEXT)_
  - `SHOWER` _(layer: P-TEXT)_
  - `JOG` _(layer: P-TEXT)_
  - `700x700` _(layer: P-TEXT)_
  - `WATER` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `DISC FILTER` _(layer: P-TEXT)_
  - `WHITE` _(layer: P-TEXT)_
  - `REMOTE` _(layer: P-TEXT)_
  - `S` _(layer: P-TEXT)_
  - `35-26LC526` _(layer: P-TEXT)_
  - `VACUUM SYSTEM` _(layer: P-TEXT)_
  - `PI-DIAGRAM RAU8G02313` _(layer: P-TEXT)_
  - `C` _(layer: P-DELIVERY_LIMIT)_
  - `V` _(layer: P-DELIVERY_LIMIT)_
  - `PM3` _(layer: P-TEXT)_
  - `MILL SITE` _(layer: P-TEXT)_
  - `{\l\fArial|b0|i0;\T1;PLANT}` _(layer: T-A-SHEET)_
  - `{\l\fArial|b0|i0;\T1;3D\~MODEL}` _(layer: T-A-SHEET)_

**Text styles:** `Standard` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ARIAL` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `CTS_REV` (isocp.shx)

---

### 35. `STOD206339.10 Broke System.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | Valmet PS-21 |
| DWG version | 33 |
| Last saved by | `nina.niittykumpu` |
| Objects | 11376 |
| Entities (model space) | 6806 |
| Layers | 38 |
| Block definitions | 184 |
| Unique attribute tags | 69 |
| App ID fingerprint | PCAD ×32 | GENIUS ×8 | other: FOCUSPI_1_3, FOCUSPI, FOCUSPI_1_1_RAIMO_TAMMERO |
| Connectivity | ✅ LIN_FROM/LIN_TO (215 records) |

**Title block fields:**

- `INF14`: 10
- `INF1`: 04.03.2022
- `INF2`: JLep
- `INF3`: 04.03.2022
- `INF4`: SStr
- `INF5`: 04.03.2022
- `INF6`: HSoi
- `PROJECT1`: Shotton Mill Ltd
- `PROJECT2`: Shotton Paper Mill, United Kingdom
- `PROJECT3`: Shotton PM3
- `DRAWINGID`: STOD206339.10
- `SHEET`: 1/1
- `ARKKI`: A1
- `LYH`: SHOTTONPM3
- `TITLE1`: Broke System
- `CAD`: AutoCAD
- `MRK`: 10
- `PVM`: 22.12.2023
- `MUU`: JLin
- `TAR`: SStr
- `MUUTOS`: Updated
- `MRK2`: 01
- `PVM2`: 29.04.2022
- `MUU2`: JLep
- `TAR2`: SStr
- `MUUTOS2`: Certified
- `TUNNUS`: PI
- `SRVAS`: V
- `SROIK`: C

**Entities:** TEXT×2423, LWPOLYLINE×2174, INSERT×2058, LINE×85, CIRCLE×42, MTEXT×18, SPLINE×4, ARC×2

**Layers (38):**  
`0`, `PI0ATT`, `P-INSTRU`, `P-MASS1`, `P-REJECT`, `P-WATER`, `P-PUMPS`, `P-SYMB`, `P-TEXT`, `P-VENTS`, `P-INSTRPOS`, `P-OTHER`, `P-AIR`, `P-TANK_POS`, `P-PUMP_POS`, `P-VALVEPOS`, `P-CVPOS`, `P-LINEPOS`, `P-EQUIPMENT_POS`, `P-AGITATOR_POS`, `P-FLOOR`, `P-INSTRPOS_TEXTS`, `P-FITTINGS`, `P-A-SHEET`, `P-EQUIPMENTS`, `P-FILTERED_WATER`, `P-SEALING_WATER`, `P-COOLING_WATER`, `P-WHITE_WATER`, `P-MOTOR_POS`, `P-DELIVERY_LIMIT`, `P-REVISIONS`, `P-ADDITIVE`, `T-A-SHEET`, `FIMPEC_COLOR`, `FIMPEC_BW`, `P-PTERMINAL_POS`, `Defpoints`

**Custom linetypes (6):**

  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __
  - `PKV` — __ . __ . __ . __
  - `DASHEDX2` — Dashed (2x) ____  ____  ____  ____  ____  ___
  - `8001.Solid` — Solid
  - `8004.Chained` — Chained
  - `8011.Solid-Medium` — Solid-Medium

**Block definitions (184):**

  - `PPI_0100X` (19 entities)
  - `CTS_INFP` (1 entities)
  - `P7A1105` (2 entities)
  - `P7A1252` (3 entities)
  - `P7A1305` (1 entities)
  - `P7A1271` (2 entities)
  - `P7A0200` (3 entities)
  - `P7A1100` (2 entities)
  - `P7A1106` (5 entities)
  - `P7A1120` (4 entities)
  - `PPI_1204A` (6 entities)
  - `PPI_1200A` (1 entities)
  - `PPI_0900A` (1 entities)
  - `PPI_1000A` (1 entities)
  - `PPI_1100A` (1 entities)
  - `P7A1304` (1 entities)
  - `PCAD_INF` (1 entities)
  - `PPI_0102B` (1 entities)
  - `PR46FDB` (3 entities)
  - `PR46FE9` (3 entities)
  - `PR47035` (3 entities)
  - `P7A1212` (2 entities)
  - `P7A1210` (1 entities)
  - `PPI_1205A` (7 entities)
  - `CTS_INFT` (1 entities)
  - `CVN0F33` (4 entities)
  - `CTS_INFI` (1 entities)
  - `PR5645E` (3 entities)
  - `PR19081` (3 entities)
  - `P7A1360` (5 entities)
  - … +154 more

**Most-used block inserts:**

  - `P7A1305` ×289
  - `PPI_0900A` ×227
  - `PPI_1100A` ×215
  - `PPI_1204A` ×177
  - `P7A1304` ×133
  - `P7A1100` ×109
  - `PPI_1000A` ×94
  - `PPI_1200A` ×86
  - `P7A1105` ×49
  - `PPI_0100X` ×46
  - `PPI_0102B` ×45
  - `p7a1370` ×42
  - `PPI_1202A` ×36
  - `P7A1369` ×32
  - `P7A1372` ×28

**Attribute tags & sample values (69 unique tags):**

  - `A` ×60 — `10`
  - `ANTNIMI` ×46
  - `ANTPOS` ×46 — `1107`
  - `ANTPNIM` ×46
  - `ANTDN` ×46
  - `ANTPN` ×46
  - `ANTMAT` ×46
  - `ANTLIIT` ×46
  - `ANTPITU` ×46
  - `ANTERI1` ×46
  - `ANTPHAV` ×46
  - `ANTSIPO` ×46
  - `ANTAILY` ×46
  - `ANTTIH` ×46
  - `ANTALUE` ×46
  - `ANTKPAI` ×46
  - `ANTLMP` ×46
  - `ANTYLAM` ×46
  - `ANTLISA` ×46
  - `TEKSTI1` ×18 — `FROM WHITE WATER TANK`
  - `TEKSTI2` ×18 — `35-25P502`
  - `KAAVIO` ×18 — `PI-DIAGRAM STOD206338`
  - `MRK` ×10 — `00`
  - `KPL` ×10
  - `PVM` ×10 — `04.03.2022`
  - `MUU` ×10 — `JLep`
  - `TAR` ×10 — `SStr`
  - `MUUTOS` ×10 — `Preliminary`
  - `INFO` ×6 — `+12.000`
  - `TUNNUS` ×4 — `PI`

**Text entity samples (model space):**

  - `SIZE PRESS PULPER` _(layer: P-TEXT)_
  - `START/ STOP` _(layer: P-TEXT)_
  - `REEL PULPER` _(layer: P-TEXT)_
  - `TAIL` _(layer: P-TEXT)_
  - `WINDER PULPER` _(layer: P-TEXT)_
  - `START` _(layer: P-TEXT)_
  - `STOP` _(layer: P-TEXT)_
  - `PRESS PULPER` _(layer: P-TEXT)_
  - `S1` _(layer: P-TEXT)_
  - `S2` _(layer: P-TEXT)_
  - `SV` _(layer: P-TEXT)_
  - `ST` _(layer: P-TEXT)_
  - `SS` _(layer: P-TEXT)_
  - `S3` _(layer: P-TEXT)_
  - `O` _(layer: P-TEXT)_
  - `DW` _(layer: P-TEXT)_
  - `D` _(layer: P-TEXT)_
  - `A1` _(layer: P-TEXT)_
  - `A2` _(layer: P-TEXT)_
  - `R` _(layer: P-TEXT)_

**Text styles:** `STANDARD` (ARIALN.TTF), `ROMANS` (ARIALN.TTF), `ISOCP` (ARIALN.TTF), `Arial` (ARIALN.TTF), `ARIALN` (ARIALN.TTF), `f0890111901` (ARIALN.TTF), `AUDIT_D_220106164814-0` (ARIALN.TTF), `CTS_REV` (isocp.shx), `ISO` (ISO.shx)

---

## TM01_PID  ·  GOR Italian (GORA*/GORB*) / KSD Swedish (KSDM*)

### 36. `GORA68210.05_Code 03 - P&ID AirCap_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 7550 |
| Entities (model space) | 5216 |
| Layers | 36 |
| Block definitions | 18 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×25 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×3597, TEXT×1046, CIRCLE×202, ARC×177, LWPOLYLINE×102, INSERT×65, SOLID×23, HATCH×3

**Layers (36):**  
`0`, `CARTIGLIO`, `2-WATER CUSTOMER (DOT)`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-WATER GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-PNEUMATIC GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `1-BACKPRESSURE GOR`, `VIEWPORT`, `VIEWPORT HIDDEN`, `1-GAS GOR`, `2-GAS CUSTOMER`, `2-PNEUMATIC CUSTOMER`, `2-BACKPRESSURE CUSTOMER`, `2-HYDRAULIC CUSTOMER`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `2-WATER CUSTOMER`, `1- DELIVERY LIMITS`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `Q`, `AM_0`, `AM_5`, `AM_6`, `BL-BLNK`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `CADRA_CONTINUOUS` — Solid line
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `ELECTRICAL_CONNECTION_L` — Electrical Connection Long ....]....]....]....
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (13):**

  - `LOOPDCS` (6 entities)
  - `COIL` (5 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA1++` (30 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `StampPreliminary` (262 entities)
  - `MetsoLogoA` (506 entities)
  - `ValmetStampForApproval` (107 entities)
  - `IndiceRevisione_180°` (3 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×62
  - `COIL` ×1
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×1 — `05`

**Text entity samples (model space):**

  - `661` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162TI2` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162F1-540-M1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162HC1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `540` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `SC` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `162TT2` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162TT1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162TI1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `581` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162TE1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `500` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162BCS1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `520` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162TA` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `600` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `620` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `162FV1-641` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `ESTRAZIONE PA PULPER AD UMIDO` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `ACANSGDT` (amgdt.shx), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `USER3` (ITALIC.SHX), `ISOR` (ISOCP.SHX)

---

### 37. `GORA68211.03_Code 03 - P&Id Adv ReDry_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4757 |
| Entities (model space) | 2258 |
| Layers | 39 |
| Block definitions | 29 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×26 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1651, TEXT×400, CIRCLE×75, ARC×64, LWPOLYLINE×37, SOLID×18, INSERT×8, HATCH×4

**Layers (39):**  
`0`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-PNEUMATIC GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `2-WATER EQUIPMENT CUSTOMER (DOT)`, `1-BACKPRESSURE GOR`, `2-PNEUMATIC CUSTOMER`, `2-BACKPRESSURE CUSTOMER`, `1-FLOW TEXT GOR`, `2-EQUIPMENT KSD`, `1- DELIVERY LIMITS`, `AM_BOR`, `VIEWPORT`, `VIEWPORT HIDDEN`, `AM_0`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `3-TAG AND INSTRUMENTS`, `3-EQUIPMENTMETSO CHINA`, `1-WATER GOR`, `2-TAG AND TEXT CUSTOMER`, `1-VALVE TEXT GOR`, `Defpoints`, `FORMATO`, `3-WATER KSD`, `2-WATER CUSTOMER`, `2-EQUIPMENT CUSTOMER`, `AM_8`, `AM_6`, `AM_5`, `BL-BLNK`, `2-EXISTING INSTRUMENTS`, `2-BACKPRESSURE GOR`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `CADRA_CONTINUOUS` — Solid line
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `ELECTRICAL_CONNECTION_L` — Electrical Connection Long ....]....]....]....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (24):**

  - `LOOPDCS` (6 entities)
  - `COIL` (5 entities)
  - `SquadraturaA1` (25 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniRiga` (13 entities)
  - `RevisioniTesta` (18 entities)
  - `StampPreliminary` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `MetsoLogoA` (506 entities)
  - `ValmetStampCertified` (107 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `INSTRUM` (8 entities)
  - `DCS DISPLAY` (7 entities)
  - `InstFieldMt_3LinesText` (4 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×4
  - `IndiceRevisione_90°` ×2
  - `COIL` ×1
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×3 — `03`

**Text entity samples (model space):**

  - `ESTRAZIONE PA PULPER AD UMIDO` _(layer: LEGEND)_
  - `BATTERIE DI SCAMBIO ACQUA O VAPORE` _(layer: LEGEND)_
  - `IN LINE VENTURI` _(layer: LEGEND)_
  - `VENTURI IN LINEA` _(layer: LEGEND)_
  - `DRAIN MODULE` _(layer: LEGEND)_
  - `MODULO DI SCARICO` _(layer: LEGEND)_
  - `WET DUST PULPER EXHAUST` _(layer: LEGEND)_
  - `COLLETTORE AD UMIDO` _(layer: LEGEND)_
  - `WET DUST COLLECTOR` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ACQUA` _(layer: LEGEND)_
  - `AIR/WATER HEAT EXCHANGER` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ARIA` _(layer: LEGEND)_
  - `AIR/AIR HEAT EXCHANGER` _(layer: LEGEND)_
  - `+` _(layer: LEGEND)_
  - `SC` _(layer: LEGEND)_
  - `FILTRO ARIA` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `FLEXIBLE JOINT` _(layer: LEGEND)_
  - `GIUNTO FLESSIBILE` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `MONOTXT` (monotxt), `ROMANS` (romans), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACISOGDT` (AMGDT), `USER3` (ITALIC.SHX), `ISOR` (ISOCP.SHX)

---

### 38. `GORA68212.04_Code 03 - P&ID Heat Recoveries_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4316 |
| Entities (model space) | 2399 |
| Layers | 40 |
| Block definitions | 25 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×27 | other: CONTENTBLOCKICON, MCAD_NO_VIS, AD_DRAW |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1738, TEXT×469, CIRCLE×81, LWPOLYLINE×34, ARC×32, SOLID×23, INSERT×11, HATCH×9

**Layers (40):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `1-AIR GOR`, `1-WATER GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-PNEUMATIC GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `1-BACKPRESSURE GOR`, `VIEWPORT`, `VIEWPORT HIDDEN`, `REV- C -ARROWS`, `2-PNEUMATIC CUSTOMER`, `2-TAG AND TEXT CUSTOMER`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-WATER CUSTOMER`, `1- DELIVERY LIMITS`, `Defpoints`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `3-PNEUMATIC KSD`, `3-WATER KSD`, `2-AIR CUSTOMER`, `AM_0`, `AM_6`, `AM_5`, `BL-BLNK`, `AM_8`, `2-WATER KSD`, `2-WATER CUSTOMER (DOT)`, `Pipe ID`, `Revision 02`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `CADRA_CONTINUOUS` — Solid line
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _

**Block definitions (21):**

  - `LOOPDCS` (6 entities)
  - `COIL` (5 entities)
  - `INSULATION LEG` (8 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `StampPreliminary` (262 entities)
  - `SquadraturaA1` (25 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `ValmetStampForApproval` (107 entities)
  - `_ACMFILLED30` (1 entities)
  - `_ACMEMPTY60` (3 entities)
  - `PIPENO` (2 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×8
  - `COIL` ×1
  - `INSULATION LEG` ×1
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×1 — `04`

**Text entity samples (model space):**

  - `ESTRAZIONE PA PULPER AD UMIDO` _(layer: LEGEND)_
  - `BATTERIE DI SCAMBIO ACQUA O VAPORE` _(layer: LEGEND)_
  - `IN LINE VENTURI` _(layer: LEGEND)_
  - `VENTURI IN LINEA` _(layer: LEGEND)_
  - `DRAIN MODULE` _(layer: LEGEND)_
  - `MODULO DI SCARICO` _(layer: LEGEND)_
  - `WET DUST PULPER EXHAUST` _(layer: LEGEND)_
  - `COLLETTORE AD UMIDO` _(layer: LEGEND)_
  - `WET DUST COLLECTOR` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ACQUA` _(layer: LEGEND)_
  - `AIR/WATER HEAT EXCHANGER` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ARIA` _(layer: LEGEND)_
  - `AIR/AIR HEAT EXCHANGER` _(layer: LEGEND)_
  - `+` _(layer: LEGEND)_
  - `SC` _(layer: LEGEND)_
  - `FILTRO ARIA` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `FLEXIBLE JOINT` _(layer: LEGEND)_
  - `GIUNTO FLESSIBILE` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `ACANSGDT` (amgdt.shx), `USER1` (TXT.SHX), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `USER2` (SIMPLEX.SHX), `ISOR` (ISOCP.SHX), `USER3` (ITALIC.SHX), `MZ_text` (romans.shx)

---

### 39. `KSDM160104102_04_SH01_Bale handling_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 69 |
| Entities (CSV) | 40 |
| XDATA entities (CSV) | 4 |
| Connectivity (CSV) | — |

---

### 40. `KSDM160104102_07_SH03_Soft and hardwood line_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 31 |
| Entities (model space) | 1938 |
| Layers | 67 |
| Block definitions | 87 |
| Unique attribute tags | 82 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | 🔴 No semantic connectivity |

**Title block fields:**

- `SHEET`: 3

**Entities:** LINE×889, INSERT×416, LWPOLYLINE×376, TEXT×138, ARC×53, MTEXT×17, POLYLINE×16, CIRCLE×13

**Layers (67):**  
`0`, `PS`, `PS-FL-P`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `AME_FRZ`, `BLANKETT`, `BLTEXT`, `PR`, `BL-BLNK`, `DEFPOINTS`, `PR-KONT`, `TX-TX25`, `TX-TX35`, `TX-TX50`, `Metso-log2`, `Metso-log1`, `PS-EQUIP`, `INSTR-VALVE`, `HAND-VALVE`, `TXT-HAND-VALVE`, `PS-FLOOR`, `Fresh water`, `White water untreated`, `White water treated`, `TXT-INST-VALVE`, `LA`, `Pipe ID`, `Pipe split`, `GHD-A`, `OH-TX25`, `PI4INST`, `PI4ITXT`, `PI3VTIVENT`, `Revision 01`, `中文标注`, `INSTRUMENT`, `Revision 02` … +27 more

**Custom linetypes (1):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 

**Block definitions (87):**

  - `PS-INIT` (0 entities)
  - `PS-INTXT` (2 entities)
  - `AME_NIL` (0 entities)
  - `AME_SOL` (0 entities)
  - `LA-INIT` (0 entities)
  - `PS_3214` (6 entities)
  - `PS_3201` (8 entities)
  - `PS_3202` (8 entities)
  - `REVHUVUD` (22 entities)
  - `METSOHUVUD` (89 entities)
  - `DRWSTAMPMETSO` (13 entities)
  - `A$C4F874EFE` (544 entities)
  - `POSNR` (5 entities)
  - `PS_3215` (8 entities)
  - `PS_3403` (14 entities)
  - `T` (8 entities)
  - `spec` (12 entities)
  - `PS_3208` (8 entities)
  - `instr` (5 entities)
  - `PILH` (7 entities)
  - `PILV` (7 entities)
  - `PS-3203` (9 entities)
  - `RAM-A1F-1` (87 entities)
  - `Pipeid` (5 entities)
  - `balance` (5 entities)
  - `Max` (7 entities)
  - `Line no` (1 entities)
  - `SPLIT` (2 entities)
  - `PS-3204` (9 entities)
  - `S` (3 entities)
  - … +57 more

**Most-used block inserts:**

  - `T` ×72
  - `instr` ×61
  - `PIPENO` ×39
  - `PS_3214` ×31
  - `LIMIT` ×24
  - `SPLIT` ×22
  - `Line no` ×18
  - `kona` ×16
  - `POSNR` ×13
  - `PS_3208` ×12
  - `PILV` ×11
  - `PS_3215` ×10
  - `PROCESSDATA` ×10
  - `PS_3202` ×10
  - `PS_3201` ×10

**Attribute tags & sample values (82 unique tags):**

  - `POSNR` ×210 — `030`
  - `KRETS` ×89 — `122PI`
  - `PIPEID` ×39 — `124L-003`
  - `PIPEDATA` ×39 — `200-P96-VE10H2A`
  - `TYPE` ×38
  - `MATERIAL` ×38 — `11S`
  - `SEALING` ×38
  - `BENÄMNING` ×36 — `CWW PUMP 134P-008`
  - `LINENO` ×18 — `QC 004`
  - `MAX_PROCESS` ×10 — `( - / 4,2 / 3770 )`
  - `NOM_PROCESS` ×10 — `- / 4 / 2585`
  - `DESCRIPTION` ×6 — `SW Refiner 1`
  - `ITEM` ×6 — `122E-001`
  - `MODEL` ×6 — `HC Cleaner200B`
  - `FLOW` ×6 — `2800 l/min`
  - `CONCENTRATION` ×6 — `4,2 %`
  - `HEAD` ×6
  - `DUTY` ×6 — `Inst: ,`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1
  - `PROJNUM_01` ×1 — `160104`
  - `ITEM_DOC_NO` ×1 — `KSDM160104102`
  - `REV` ×1 — `07`
  - `SHEET` ×1 — `3`

**Text entity samples (model space):**

  - `ITEM NUMBER` _(layer: TX-TX35)_
  - `SW REFINING` _(layer: TX-TX25)_
  - `{\Fisocp3|c0;CONTROL BOX\P22CB-001}` _(layer: TXT-INST-VALVE)_
  - `{\Fisocp3|c0;CONTROL BOX\P22CB-002}` _(layer: TXT-INST-VALVE)_
  - `M1` _(layer: TX-TX35)_
  - `HW REFINING` _(layer: TX-TX25)_
  - `DUTY, kW` _(layer: TX-TX35)_
  - `TECHNICAL DATA` _(layer: TX-TX35)_
  - `t/d` _(layer: TX-TX35)_
  - `%%%-weight` _(layer: TX-TX35)_
  - `l/min, kPa` _(layer: TX-TX35)_
  - `{\Fisocp3|c0;CONTROL BOX\P24CB-001}` _(layer: TXT-INST-VALVE)_
  - `M3` _(layer: TX-TX35)_
  - `Oil pump` _(layer: TX-TX35)_
  - `M2` _(layer: TX-TX35)_
  - `SEALING WATER` _(layer: TX-TX35)_
  - `KSDM160104112sh1` _(layer: TX-TX35)_
  - `LOCAL\PREMOTE` _(layer: TXT-INST-VALVE)_
  - `LOAD DEVICE         QUICK OPEN/CLOSE` _(layer: TXT-INST-VALVE)_
  - `REFINER` _(layer: TX-TX35)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ROMANS` (ROMANS.SHX), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `KSD7480417-4 Blending and mixing system$0$ISO` (isocp3.shx), `ISOCP` (isocp.shx)

---

### 41. `KSDM160104102_07_SH05_Thick stock screening_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 17 |
| Entities (CSV) | 16 |
| XDATA entities (CSV) | 1 |
| Connectivity (CSV) | — |

---

### 42. `KSDM160104102_07_SH06_Approach system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 170 |
| Entities (CSV) | 124 |
| XDATA entities (CSV) | 6 |
| Connectivity (CSV) | — |

---

### 43. `KSDM160104102_07_SH07_Machine broke pulper system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 60 |
| Entities (model space) | 765 |
| Layers | 67 |
| Block definitions | 61 |
| Unique attribute tags | 81 |
| App ID fingerprint | IDOK ×9 | GENIUS ×3 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 7

**Entities:** LINE×266, TEXT×164, LWPOLYLINE×152, INSERT×140, CIRCLE×26, ATTDEF×6, ARC×6, HATCH×4

**Layers (67):**  
`0`, `PS`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `AME_FRZ`, `BLANKETT`, `BLTEXT`, `PR`, `BL-BLNK`, `DEFPOINTS`, `PR-KONT`, `TX-TX25`, `TX-TX35`, `TX-TX50`, `Metso-log2`, `Metso-log1`, `PS-EQUIP`, `INSTR-VALVE`, `HAND-VALVE`, `TXT-HAND-VALVE`, `PS-FLOOR`, `Fresh water`, `White water untreated`, `TXT-INST-VALVE`, `LA`, `Pipe ID`, `Pipe split`, `Broke`, `White water treated`, `OH-TX25`, `Revision 00`, `中文标注`, `INSTRUMENT`, `Revision 02`, `AM_BOR`, `_HEAD_PARTLIST`, `_HEAD_PLANT`, `_HEAD_REV_ROW1` … +27 more

**Custom linetypes (2):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 
  - `AM_ISO08W050` — ValmetIso ____ . ____ . ____ . ____ . ____ . __

**Block definitions (61):**

  - `PS-INIT` (0 entities)
  - `PS5-2005` (8 entities)
  - `PS-INTXT` (2 entities)
  - `AME_NIL` (0 entities)
  - `AME_SOL` (0 entities)
  - `LA-INIT` (0 entities)
  - `PS_3202` (8 entities)
  - `REVHUVUD` (22 entities)
  - `METSOHUVUD` (89 entities)
  - `DRWSTAMPMETSO` (13 entities)
  - `A$C4F874EFE` (544 entities)
  - `POSNR` (5 entities)
  - `PS_3215` (8 entities)
  - `T` (8 entities)
  - `spec` (12 entities)
  - `instr` (5 entities)
  - `A1` (92 entities)
  - `PILH` (7 entities)
  - `PILV` (7 entities)
  - `Pipeid` (5 entities)
  - `Line no` (1 entities)
  - `SPLIT` (2 entities)
  - `PS_3203` (9 entities)
  - `PS_3204` (9 entities)
  - `S` (3 entities)
  - `balance` (5 entities)
  - `Max` (7 entities)
  - `PS_3302` (8 entities)
  - `ps_3901` (4 entities)
  - `LIMIT` (3 entities)
  - … +31 more

**Most-used block inserts:**

  - `Pipeno` ×19
  - `instr` ×17
  - `T` ×16
  - `kona` ×11
  - `SPLIT` ×10
  - `PS5-2005` ×8
  - `PS_3202` ×7
  - `Processdata` ×6
  - `LIMIT` ×6
  - `PILV` ×4
  - `PS_3204` ×4
  - `LOCALINSTR` ×4
  - `PILH` ×3
  - `ps_3901` ×3
  - `PS_3214` ×3

**Attribute tags & sample values (81 unique tags):**

  - `POSNR` ×57 — `004`
  - `KRETS` ×23 — `126QC`
  - `PIPEID` ×19 — `126L-002`
  - `PIPEDATA` ×19 — `200-P91-VE10H2A`
  - `BENÄMNING` ×14 — `DILUTION WATER 134P-004`
  - `TYPE` ×14
  - `MATERIAL` ×14 — `1K0`
  - `SEALING` ×14
  - `NOM_PROCESS` ×6 — `- / 3,5 / 4500`
  - `MAX_PROCESS` ×6 — `( - / 4,0 / 5400 )`
  - `ITEM` ×2 — `126P-001`
  - `MODEL` ×2 — `A32-125`
  - `FLOW` ×2 — `5400 l/min`
  - `CONCENTRATION` ×2 — `4 %`
  - `DUTY` ×2 — `RDC: 55 kW, 1500 rpm`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1
  - `PROJNUM_01` ×1 — `160104`
  - `ITEM_DOC_NO` ×1 — `KSDM160104102`
  - `REV` ×1 — `07`
  - `SHEET` ×1 — `7`
  - `OF_SHEET` ×1 — `9`
  - `GEN-TITLE-NAME` ×1 — `WEN`
  - `GEN-TITLE-DAT` ×1 — `11/21/2022`

**Text entity samples (model space):**

  - `ITEM NUMBER` _(layer: TX-TX35)_
  - `DUTY, kW` _(layer: TX-TX35)_
  - `S4` _(layer: TX-TX35)_
  - `S2` _(layer: TX-TX35)_
  - `S1` _(layer: TX-TX35)_
  - `ST2` _(layer: TX-TX35)_
  - `ST1` _(layer: TX-TX35)_
  - `MACHINE PRODUCTION` _(layer: TX-TX35)_
  - `199 KG/MIN` _(layer: TX-TX35)_
  - `TRIM PRODUCTION` _(layer: TX-TX35)_
  - `1,5 KG/MIN` _(layer: TX-TX35)_
  - `CWW SHOWER FOR LOOSE PAPER FROM REEL` _(layer: PS)_
  - `FLOW 1000 l/min, 200 kPa` _(layer: PS)_
  - `CWW SHOWER SHEET BREAK` _(layer: PS)_
  - `FLOW 2200 l/min, 200 kPa` _(layer: PS)_
  - `CWW SHOWER TRIM` _(layer: PS)_
  - `FLOW 50 l/min, 200 kPa` _(layer: PS)_
  - `SS` _(layer: TX-TX35)_
  - `DW` _(layer: TX-TX35)_
  - `A` _(layer: TX-TX35)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx), `KSD7480417-4 Blending and mixing system$0$ISO` (isocp3.shx)

---

### 44. `KSDM160104102_07_SH09_Internal broke system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 91 |
| Entities (model space) | 1760 |
| Layers | 109 |
| Block definitions | 141 |
| Unique attribute tags | 84 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 9

**Entities:** LINE×613, INSERT×606, LWPOLYLINE×233, TEXT×232, ARC×50, HATCH×6, ATTDEF×6, MTEXT×4

**Layers (109):**  
`0`, `PS`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `AME_FRZ`, `BLANKETT`, `BLTEXT`, `PR`, `BL-BLNK`, `DEFPOINTS`, `PR-KONT`, `TX-TX25`, `TX-TX35`, `TX-TX50`, `Metso-log2`, `Metso-log1`, `PS-EQUIP`, `INSTR-VALVE`, `HAND-VALVE`, `TXT-HAND-VALVE`, `PS-FLOOR`, `Fresh water`, `White water untreated`, `White water treated`, `TXT-INST-VALVE`, `LA`, `Pipe ID`, `Pipe split`, `White water treated CWW`, `Broke`, `OH-TX25`, `PI3VTIVENT`, `CHEMICALS`, `Revision 00`, `中文标注`, `INSTRUMENT`, `Revision 02`, `GHD-A` … +69 more

**Custom linetypes (5):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 
  - `DASHDOT` — __ . __ . __ . __ . __ . __ . __ . __ . __ . __
  - `KVL` — - - - - - - - - - -
  - `PKV` — __ . __ . __ . __
  - `CNT3` — extr long dash-dotted center

**Block definitions (141):**

  - `PS-INIT` (0 entities)
  - `PS-INTXT` (2 entities)
  - `AME_NIL` (0 entities)
  - `AME_SOL` (0 entities)
  - `LA-INIT` (0 entities)
  - `PS_3214` (6 entities)
  - `PS_3525` (10 entities)
  - `PS_3301` (8 entities)
  - `PS_3201` (8 entities)
  - `PS_3202` (8 entities)
  - `METSOHUVUD` (89 entities)
  - `DRWSTAMPMETSO` (13 entities)
  - `A$C4F874EFE` (544 entities)
  - `POSNR` (5 entities)
  - `PS_3215` (8 entities)
  - `PS_3403` (14 entities)
  - `T` (8 entities)
  - `spec` (12 entities)
  - `PS_3208` (5 entities)
  - `instr` (5 entities)
  - `PILH` (7 entities)
  - `PILV` (7 entities)
  - `Pipeid` (5 entities)
  - `Line no` (1 entities)
  - `PS-3203` (9 entities)
  - `SPLIT` (2 entities)
  - `PS_3204` (9 entities)
  - `PS-3204` (9 entities)
  - `balance` (5 entities)
  - `Max` (7 entities)
  - … +111 more

**Most-used block inserts:**

  - `PS-INTXT` ×140
  - `LA-INIT` ×63
  - `AME_NIL` ×57
  - `AME_SOL` ×57
  - `T` ×36
  - `instr` ×36
  - `PS-INIT` ×32
  - `Pipeno` ×31
  - `PS_3214` ×17
  - `PS_3201` ×14
  - `Line no` ×14
  - `kona` ×13
  - `LIMIT` ×13
  - `PS_3215` ×11
  - `SPLIT` ×10

**Attribute tags & sample values (84 unique tags):**

  - `POSNR` ×251 — `011`
  - `TYP` ×140
  - `KRETS` ×46 — `126LI`
  - `PIPEID` ×31 — `126L-039`
  - `PIPEDATA` ×31 — `150-P91-VE10H2A`
  - `TYPE` ×23
  - `MATERIAL` ×23 — `1K0`
  - `SEALING` ×23
  - `BENÄMNING` ×22 — `FLUSH PUMP 134P-008`
  - `LINENO` ×14 — `200/125`
  - `MAX_PROCESS` ×8 — `( - / 4 / 1389 )`
  - `NOM_PROCESS` ×8 — `- / 3,5 / -`
  - `ITEM` ×6 — `126P-002`
  - `CONCENTRATION` ×6 — `4 %`
  - `MODEL` ×5 — `A32-80`
  - `FLOW` ×5 — `2000 l/min`
  - `HEAD` ×5 — `45 m wc`
  - `DUTY` ×5 — `RDC: 30 kW, 1500 rpm`
  - `DESCRIPTION` ×4 — `Broke tower`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `STATUS` ×1 — `Certified`
  - `SIGNATURE` ×1 — `WEN`
  - `DATE` ×1 — `09/23/2024`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1

**Text entity samples (model space):**

  - `DUTY, kW` _(layer: TX-TX35)_
  - `ITEM NUMBER` _(layer: TX-TX35)_
  - `BROKE DEFLAKING` _(layer: TX-TX25)_
  - `125/150` _(layer: TX-TX25)_
  - `150/125` _(layer: TX-TX25)_
  - `TECHNICAL DATA` _(layer: TX-TX35)_
  - `t/d` _(layer: TX-TX35)_
  - `%%%-weight` _(layer: TX-TX35)_
  - `l/min, bar` _(layer: TX-TX35)_
  - `SEALING WATER` _(layer: TX-TX35)_
  - `KSDM160104112` _(layer: TX-TX35)_
  - `DN150` _(layer: MECHANICAL)_
  - `BROKE SCREENING` _(layer: TX-TX25)_
  - `INTERNAL BROKE SYSTEM` _(layer: TX-TX25)_
  - `{\Fisocp3|c0;FIELD BOX\P126FB001}` _(layer: TXT-INST-VALVE)_
  - `BROKE HC-CLEANING` _(layer: TX-TX25)_
  - `DN40` _(layer: Pipe ID)_
  - `Floor channel` _(layer: TX-TX35)_
  - `250/200` _(layer: TX-TX35)_
  - `MAX FLOW (kg/min / cons. % / LPM)` _(layer: PS)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx), `ROMANS` (ROMANS.SHX), `KSD7480417-4 Blending and mixing system$0$ISO` (isocp3.shx), `ROMA` (ROMA.shx), `NIMIKE` (D:\r13\com\fonts\isocp.shx), `SFS` (legible)

---

### 45. `KSDM160104102_08_SH02_SW_HW Dissolving system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 104 |
| Entities (model space) | 1195 |
| Layers | 56 |
| Block definitions | 46 |
| Unique attribute tags | 83 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 2

**Entities:** LINE×343, INSERT×321, LWPOLYLINE×314, TEXT×151, CIRCLE×27, POLYLINE×12, MTEXT×7, SPLINE×6

**Layers (56):**  
`0`, `PS`, `PS-FL-P`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `BLANKETT`, `DEFPOINTS`, `TX-TX25`, `TX-TX35`, `PS-EQUIP`, `INSTR-VALVE`, `HAND-VALVE`, `TXT-HAND-VALVE`, `PS-FLOOR`, `Fresh water`, `White water untreated`, `TXT-INST-VALVE`, `Pipe ID`, `Pipe split`, `GHD-A`, `Revision 02`, `White water treated`, `White water treated CWW`, `AM_BOR`, `_HEAD_PARTLIST`, `_HEAD_PLANT`, `_HEAD_REV_ROW1`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `_HEAD_MACHINE`, `Revision 01`, `Broke`, `Revision 05`, `SW Fiber` … +16 more

**Custom linetypes (1):**

  - `CNT3` — extr long dash-dotted center

**Block definitions (46):**

  - `PS_3214` (6 entities)
  - `PS_3525` (10 entities)
  - `PS_3301` (8 entities)
  - `PS_3201` (8 entities)
  - `PS_3202` (8 entities)
  - `T` (8 entities)
  - `instr` (5 entities)
  - `PILH` (7 entities)
  - `PILV` (7 entities)
  - `Line no` (1 entities)
  - `PS-3203` (9 entities)
  - `PS-3204` (9 entities)
  - `SPLIT` (2 entities)
  - `S` (3 entities)
  - `ps_3901` (4 entities)
  - `LIMIT` (3 entities)
  - `kona` (4 entities)
  - `A$C0E9C4445` (4 entities)
  - `MillRithuvud` (173 entities)
  - `revheadA0` (13 entities)
  - `ValmetStatusStamp` (130 entities)
  - `ValmetA1+210` (141 entities)
  - `PUMPSPEC` (11 entities)
  - `TANKSPEC` (8 entities)
  - `PIPENO` (2 entities)
  - `LOCALINSTRUMENT` (3 entities)
  - `TANKLABEL` (6 entities)
  - `PROCESSDATA` (2 entities)
  - `revisioner` (60 entities)
  - `maskinpos` (6 entities)
  - … +16 more

**Most-used block inserts:**

  - `PIPENO` ×44
  - `T` ×34
  - `instr` ×27
  - `LIMIT` ×20
  - `LOCALINSTRUMENT` ×20
  - `PS_3214` ×18
  - `PS_3202` ×16
  - `Line no` ×16
  - `PROCESSDATA` ×16
  - `SPLIT` ×13
  - `kona` ×12
  - `PILV` ×11
  - `ps_3901` ×10
  - `PS-3203` ×8
  - `PS-3204` ×6

**Attribute tags & sample values (83 unique tags):**

  - `POSNR` ×135 — `001`
  - `KRETS` ×54 — `122LI`
  - `PIPEID` ×44 — `121L-001`
  - `PIPEDATA` ×44 — `350-P95-VE10H2A`
  - `TYPE` ×36
  - `MATERIAL` ×36 — `1K0`
  - `SEALING` ×36
  - `BENÄMNING` ×32 — `SW HC CLEANER 122E-001`
  - `LINENO` ×16 — `80/50`
  - `MAX_PROCESS` ×16 — `(  / 0,006 / 11930 )`
  - `NOM_PROCESS` ×16 — `/ 0,006 / 8090`
  - `ITEM` ×12 — `122T-001`
  - `CONCENTRATION` ×12 — `5,0 %`
  - `MODEL` ×10 — `A42-200`
  - `FLOW` ×10 — `11820 l/min`
  - `DUTY` ×10 — `RDC: 75 kW, 1500 rpm`
  - `DESCRIPTION` ×6 — `HW dump tower`
  - `HEAD` ×4 — `25 m wc`
  - `VOLUME` ×2 — `200 m³`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `STATUS` ×1 — `Certified`
  - `SIGNATURE` ×1 — `WEN`
  - `DATE` ×1 — `09/23/2024`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1

**Text entity samples (model space):**

  - `ITEM NUMBER` _(layer: TX-TX35)_
  - `DUTY, kW` _(layer: TX-TX35)_
  - `TECHNICAL DATA` _(layer: TX-TX35)_
  - `t/d` _(layer: TX-TX35)_
  - `%%%-weight` _(layer: TX-TX35)_
  - `l/min, kPa` _(layer: TX-TX35)_
  - `PULP DISSOLVING LINE SW` _(layer: TX-TX25)_
  - `HW STORAGE` _(layer: TX-TX25)_
  - `SW STORAGE` _(layer: TX-TX25)_
  - `%%C150` _(layer: MECHANICAL)_
  - `SEALING WATER` _(layer: REFERENCES)_
  - `KSDM160104112` _(layer: REFERENCES)_
  - `PULP DISSOLVING LINE HW` _(layer: TX-TX25)_
  - `IN MACHINE DELIVERY` _(layer: TX-TX35)_
  - `CW1` _(layer: TX-TX35)_
  - `CW2` _(layer: TX-TX35)_
  - `Gearbox` _(layer: TX-TX35)_
  - `MAIN` _(layer: TX-TX35)_
  - `OIL` _(layer: TX-TX35)_
  - `E` _(layer: TX-TX35)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx)

---

### 46. `KSDM160104102_09_SH04_Mixing system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 12 |
| Entities (CSV) | 11 |
| XDATA entities (CSV) | 0 |
| Connectivity (CSV) | — |

---

### 47. `KSDM160104102_09_SH08_Converting broke pulper_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 190 |
| Entities (CSV) | 78 |
| XDATA entities (CSV) | 0 |
| Connectivity (CSV) | — |

---

### 48. `KSDM160104103_05_SH01_White water system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 32 |
| Entities (CSV) | 25 |
| XDATA entities (CSV) | 3 |
| Connectivity (CSV) | — |

---

### 49. `KSDM160104103_08_SH04_White water system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 32 |
| Entities (CSV) | 22 |
| XDATA entities (CSV) | 1 |
| Connectivity (CSV) | — |

---

### 50. `KSDM160104103_09_SH02_White water system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 32 |
| Entities (CSV) | 23 |
| XDATA entities (CSV) | 1 |
| Connectivity (CSV) | — |

---

### 51. `KSDM160104103_09_SH03_White water system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 27 |
| Entities (CSV) | 22 |
| XDATA entities (CSV) | 2 |
| Connectivity (CSV) | — |

---

### 52. `KSDM160104104_06_SH01_Shower water system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 30845 |
| Entities (CSV) | 30010 |
| XDATA entities (CSV) | 6484 |
| Connectivity (CSV) | — |

---

### 53. `KSDM160104105_05_SH03_Fresh water system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 73 |
| Entities (model space) | 567 |
| Layers | 61 |
| Block definitions | 50 |
| Unique attribute tags | 72 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 3

**Entities:** LINE×205, INSERT×181, TEXT×126, LWPOLYLINE×27, MTEXT×19, ATTDEF×6, CIRCLE×3

**Layers (61):**  
`0`, `PS`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `AME_FRZ`, `BLANKETT`, `BLTEXT`, `PR`, `BL-BLNK`, `DEFPOINTS`, `LOGO`, `PR-KONT`, `TX-TX25`, `TX-TX35`, `TX-TX50`, `Metso-log2`, `Metso-log1`, `PS-EQUIP`, `INSTR-VALVE`, `PS-FLOOR`, `Fresh water`, `TXT-INST-VALVE`, `LA`, `HAND-VALVE`, `TXT-HAND-VALVE`, `Pipe ID`, `Pipe split`, `White water treated SCWW`, `GHD-A`, `OH-TX25`, `White water untreated`, `Revision`, `Revision 01`, `中文标注`, `INSTRUMENT`, `Revision 02`, `White water treated`, `AM_BOR` … +21 more

**Custom linetypes (1):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 

**Block definitions (50):**

  - `PS-INIT` (0 entities)
  - `PS-INTXT` (2 entities)
  - `AME_NIL` (0 entities)
  - `AME_SOL` (0 entities)
  - `LA-INIT` (0 entities)
  - `$DDT_AUDIT_GENERATED_(4BE83D502104DCB8)` (319 entities)
  - `PS_3301` (8 entities)
  - `REVHUVUD` (22 entities)
  - `METSOHUVUD` (89 entities)
  - `DRWSTAMPMETSO` (13 entities)
  - `A$C4F874EFE` (544 entities)
  - `POSNR` (5 entities)
  - `T` (8 entities)
  - `spec` (12 entities)
  - `instr` (5 entities)
  - `PILHHL` (7 entities)
  - `PS_3201` (8 entities)
  - `PS_3203` (9 entities)
  - `S` (3 entities)
  - `ps_3901` (4 entities)
  - `SPLIT` (2 entities)
  - `RAM-A1F-2` (95 entities)
  - `PS_3204` (9 entities)
  - `PS5-2005` (8 entities)
  - `REVRUTA` (15 entities)
  - `PILV` (7 entities)
  - `PILVVL` (7 entities)
  - `Pipeid` (5 entities)
  - `Line no` (1 entities)
  - `balance` (5 entities)
  - … +20 more

**Most-used block inserts:**

  - `PS-INTXT` ×35
  - `Pipeno` ×25
  - `SPLIT` ×24
  - `PS_3203` ×23
  - `LA-INIT` ×21
  - `AME_NIL` ×17
  - `AME_SOL` ×17
  - `PS-INIT` ×12
  - `ValmetA1+210` ×1
  - `ValmetStatusStamp` ×1
  - `MillRithuvud` ×1
  - `revisioner` ×1
  - `produktion1` ×1
  - `produktion2` ×1
  - `PILH` ×1

**Attribute tags & sample values (72 unique tags):**

  - `POSNR` ×58 — `180V-152`
  - `TYP` ×35
  - `PIPEID` ×25 — `180L-150`
  - `PIPEDATA` ×25 — `80-W03-VE10H2A`
  - `TYPE` ×23
  - `MATERIAL` ×23 — `4S4`
  - `SEALING` ×23
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `BENÄMNING` ×2 — `FLUSH WATER HEADER`
  - `STATUS` ×1 — `Certified`
  - `SIGNATURE` ×1 — `WEN`
  - `DATE` ×1 — `09/23/2024`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1
  - `PROJNUM_01` ×1 — `160104`
  - `ITEM_DOC_NO` ×1 — `KSDM160104105`
  - `REV` ×1 — `05`
  - `SHEET` ×1 — `3`
  - `OF_SHEET` ×1 — `3`
  - `GEN-TITLE-NAME` ×1 — `WEN`
  - `GEN-TITLE-DAT` ×1 — `11/21/2022`
  - `CHECKED` ×1 — `JNS`
  - `CDATE` ×1 — `09/23/2024`
  - `APPROVED` ×1 — `MSA`
  - `ADATE` ×1 — `09/23/2024`

**Text entity samples (model space):**

  - `LEVEL +22,80` _(layer: PS)_
  - `MAX FLOW (kg/min / cons. % / LPM)` _(layer: PS)_
  - `DESIGN FLOW kg/min / cons. % / LPM` _(layer: PS)_
  - `DCS SYSTEM` _(layer: PS)_
  - `CONNECTED TO` _(layer: PS)_
  - `LOCAL` _(layer: PS)_
  - `20 / 4 / 505` _(layer: GHD-A)_
  - `( 24 / 4 / 600 )` _(layer: GHD-A)_
  - `PLC SYSTEM` _(layer: PS)_
  - `SWING CHECK VALVE` _(layer: Pipe ID)_
  - `SAMPLE VALVE` _(layer: Pipe ID)_
  - `KNIFE GATE VALVE` _(layer: Pipe ID)_
  - `VALVE TYPE CODE (acc. to SSG)` _(layer: TX-TX35)_
  - `BALL VALVE` _(layer: Pipe ID)_
  - `BUTTERFLY VALVE` _(layer: Pipe ID)_
  - `NAME` _(layer: TX-TX35)_
  - `DISC CHECK VALVE` _(layer: Pipe ID)_
  - `SAFETY VALVE` _(layer: Pipe ID)_
  - `CODE` _(layer: TX-TX35)_
  - `4S4` _(layer: Pipe ID)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx)

---

### 54. `KSDM160104105_06_SH01_Fresh water system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 11 |
| Entities (model space) | 934 |
| Layers | 78 |
| Block definitions | 80 |
| Unique attribute tags | 84 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 1

**Entities:** LINE×313, INSERT×284, LWPOLYLINE×153, TEXT×151, POLYLINE×9, CIRCLE×8, ARC×7, ATTDEF×7

**Layers (78):**  
`0`, `PS`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `AME_FRZ`, `BLANKETT`, `BLTEXT`, `PR`, `BL-BLNK`, `DEFPOINTS`, `LOGO`, `PR-KONT`, `TX-TX25`, `TX-TX35`, `TX-TX50`, `Metso-log2`, `Metso-log1`, `PS-EQUIP`, `INSTR-VALVE`, `PS-FLOOR`, `Fresh water`, `TXT-INST-VALVE`, `LA`, `HAND-VALVE`, `TXT-HAND-VALVE`, `Pipe ID`, `Pipe split`, `White water treated SCWW`, `GHD-A`, `OH-TX25`, `White water untreated`, `Revision`, `Revision 01`, `中文标注`, `INSTRUMENT`, `Revision 02`, `White water treated`, `PS-FL-P` … +38 more

**Custom linetypes (4):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 
  - `STR` — 2,-1
  - `FAN` — 5,-1.5,0,-1.5,0,-1.5
  - `CNT3` — extr long dash-dotted center

**Block definitions (80):**

  - `PS-INIT` (0 entities)
  - `PS-INTXT` (2 entities)
  - `AME_NIL` (0 entities)
  - `AME_SOL` (0 entities)
  - `LA-INIT` (0 entities)
  - `$DDT_AUDIT_GENERATED_(4BE83D502104DCB8)` (319 entities)
  - `PS_3301` (8 entities)
  - `REVHUVUD` (22 entities)
  - `METSOHUVUD` (89 entities)
  - `DRWSTAMPMETSO` (13 entities)
  - `A$C4F874EFE` (544 entities)
  - `POSNR` (5 entities)
  - `T` (8 entities)
  - `spec` (12 entities)
  - `instr` (5 entities)
  - `PILHHL` (7 entities)
  - `PS_3201` (8 entities)
  - `PS_3203` (9 entities)
  - `S` (3 entities)
  - `ps_3901` (4 entities)
  - `SPLIT` (2 entities)
  - `RAM-A1F-2` (103 entities)
  - `PS_3204` (9 entities)
  - `PS5-2005` (8 entities)
  - `REVRUTA` (15 entities)
  - `PILV` (7 entities)
  - `PILVVL` (7 entities)
  - `Pipeid` (5 entities)
  - `Line no` (1 entities)
  - `balance` (5 entities)
  - … +50 more

**Most-used block inserts:**

  - `PS-INTXT` ×35
  - `Pipeno` ×30
  - `LA-INIT` ×21
  - `AME_NIL` ×17
  - `AME_SOL` ×17
  - `instr` ×16
  - `PS_3201` ×16
  - `T` ×13
  - `PS-INIT` ×12
  - `kona` ×11
  - `PS_3203` ×10
  - `SPLIT` ×10
  - `PILH` ×9
  - `pumpspec` ×8
  - `ps_3901` ×8

**Attribute tags & sample values (84 unique tags):**

  - `POSNR` ×106 — `041`
  - `TYP` ×35
  - `TYPE` ×32
  - `MATERIAL` ×32 — `1K0`
  - `SEALING` ×32
  - `PIPEID` ×30 — `180L-001`
  - `PIPEDATA` ×30 — `200-W03-VE10H2A`
  - `BENÄMNING` ×20 — `COOLING WATER RETURN`
  - `KRETS` ×13 — `180LC`
  - `CONCENTRATION` ×10 — `0 %`
  - `ITEM` ×10 — `180T-002`
  - `DUTY` ×8 — `RDC: 30 kW, 3000 rpm`
  - `FLOW` ×8 — `300 l/min`
  - `HEAD` ×8 — `125 m wc`
  - `MODEL` ×8 — `A22-32`
  - `NOM_PROCESS` ×5 — `/ - / 966`
  - `MAX_PROCESS` ×5 — `(  / 0 / 966 )`
  - `VOLUME` ×2 — `20 m³`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `DESCRIPTION` ×2 — `Fresh water tank`
  - `STATUS` ×1 — `Certified`
  - `SIGNATURE` ×1 — `WEN`
  - `DATE` ×1 — `09/23/2024`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1

**Text entity samples (model space):**

  - `DUTY, kW` _(layer: TX-TX35)_
  - `ITEM NUMBER` _(layer: TX-TX35)_
  - `TECHNICAL DATA` _(layer: TX-TX35)_
  - `t/d` _(layer: TX-TX35)_
  - `%%%-weight` _(layer: TX-TX35)_
  - `l/min, bar` _(layer: TX-TX35)_
  - `ATM.` _(layer: PS)_
  - `Cooling tower` _(layer: TX-TX35)_
  - `MAX FLOW (kg/min / cons. % / LPM)` _(layer: PS)_
  - `DESIGN FLOW kg/min / cons. % / LPM` _(layer: PS)_
  - `DCS SYSTEM` _(layer: PS)_
  - `CONNECTED TO` _(layer: PS)_
  - `LOCAL` _(layer: PS)_
  - `20 / 4 / 505` _(layer: GHD-A)_
  - `( 24 / 4 / 600 )` _(layer: GHD-A)_
  - `PLC SYSTEM` _(layer: PS)_
  - `SWING CHECK VALVE` _(layer: Pipe ID)_
  - `SAMPLE VALVE` _(layer: Pipe ID)_
  - `KNIFE GATE VALVE` _(layer: Pipe ID)_
  - `VALVE TYPE CODE (acc. to SSG)` _(layer: TX-TX35)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx)

---

### 55. `KSDM160104105_06_SH02_Fresh water system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 61 |
| Entities (CSV) | 48 |
| XDATA entities (CSV) | 3 |
| Connectivity (CSV) | — |

---

### 56. `KSDM160104106_08_SH01_Vacuum system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 142 |
| Entities (model space) | 1036 |
| Layers | 58 |
| Block definitions | 47 |
| Unique attribute tags | 82 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 1

**Entities:** LINE×428, LWPOLYLINE×256, TEXT×156, INSERT×139, CIRCLE×36, POLYLINE×6, ARC×6, ATTDEF×6

**Layers (58):**  
`0`, `PS`, `PS-IN`, `PS-PO`, `PS-FL-S`, `BLANKETT`, `PS-VACUUM`, `DEFPOINTS`, `TX-TX35`, `PS-EQUIP`, `INSTR-VALVE`, `HAND-VALVE`, `TXT-HAND-VALVE`, `PS-FLOOR`, `Fresh water`, `White water untreated`, `TXT-INST-VALVE`, `Pipe ID`, `PS-FL-V`, `PR-CENT`, `Pipe split`, `White water treated SCWW`, `PR-STRK`, `4`, `X`, `PR-SEKT`, `AA`, `PI3VTIVENT`, `Revision 01`, `Revision 02`, `White water treated`, `Revision 03`, `HW Fiber`, `Broke`, `SW Fiber`, `AM_BOR`, `_HEAD_PARTLIST`, `_HEAD_PLANT`, `_HEAD_REV_ROW1`, `Valmet_logo_color_gray_solid` … +18 more

**Custom linetypes (5):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 
  - `ST2` — long dashed hidden
  - `CNT3` — extr long dash-dotted center
  - `Comos_1` — Linetype Comos_1
  - `DASHDOT` — Dash dot __ . __ . __ . __ . __ . __ . __ . __

**Block definitions (47):**

  - `PS_3201` (8 entities)
  - `PS_3202` (8 entities)
  - `POSNR` (5 entities)
  - `T` (8 entities)
  - `PS_3148` (4 entities)
  - `instr` (5 entities)
  - `PILV` (7 entities)
  - `PS_3204` (9 entities)
  - `PILH` (7 entities)
  - `SPLIT` (2 entities)
  - `ps_3901` (4 entities)
  - `kona` (4 entities)
  - `PS_3208` (5 entities)
  - `A$C52943BFF` (119 entities)
  - `vp` (8 entities)
  - `VP1` (8 entities)
  - `PS_3214` (6 entities)
  - `PS-3204` (9 entities)
  - `011103001010_2` (15 entities)
  - `MillRithuvud` (173 entities)
  - `ValmetStatusStamp` (130 entities)
  - `revisioner` (60 entities)
  - `produktion1` (8 entities)
  - `Design production` (6 entities)
  - `produktion2` (5 entities)
  - `pumpspec` (10 entities)
  - `maskinspec` (10 entities)
  - `Pipeno` (2 entities)
  - `LOCALINSTRUMENT` (3 entities)
  - `ValmetA1+420` (155 entities)
  - … +17 more

**Most-used block inserts:**

  - `T` ×27
  - `Pipeno` ×21
  - `instr` ×16
  - `limit` ×9
  - `kona` ×7
  - `PS_3202` ×7
  - `ps_3901` ×5
  - `PS_3214` ×5
  - `SPLIT` ×5
  - `LOCALINSTRUMENT` ×5
  - `pumpspec` ×3
  - `PILH` ×3
  - `PS_3201` ×3
  - `PS_3148` ×2
  - `PS_3208` ×2

**Attribute tags & sample values (82 unique tags):**

  - `POSNR` ×66 — `136V-024`
  - `KRETS` ×32 — `136HS`
  - `PIPEID` ×21 — `136L-022`
  - `PIPEDATA` ×21 — `125-B85-VE10H2A`
  - `TYPE` ×14
  - `MATERIAL` ×14 — `4S4`
  - `SEALING` ×14
  - `BENÄMNING` ×8 — `COOLING WATER`
  - `CONCENTRATION` ×5 — `%`
  - `ITEM` ×5 — `136E-021`
  - `DUTY` ×4 — `RDC: 980 kW, 1500 rpm`
  - `FLOW` ×4 — `l/min`
  - `MODEL` ×4 — `RT 71-1`
  - `HEAD` ×3 — `m wc`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `DESCRIPTION` ×2 — `Vacuum blower`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1
  - `PROJNUM_01` ×1 — `160104`
  - `ITEM_DOC_NO` ×1 — `KSDM160104106`
  - `REV` ×1 — `08`
  - `SHEET` ×1 — `1`
  - `OF_SHEET` ×1 — `1`
  - `GEN-TITLE-NAME` ×1 — `WEN`
  - `GEN-TITLE-DAT` ×1 — `11/21/2022`

**Text entity samples (model space):**

  - `VACUUM SYSTEM` _(layer: TX-TX35)_
  - `CONCRETE` _(layer: TX-TX35)_
  - `BLOWER OIL LUBE SYSTEM` _(layer: TX-TX35)_
  - `M2` _(layer: PS)_
  - `M3` _(layer: PS)_
  - `M1` _(layer: PS)_
  - `H1` _(layer: PS)_
  - `Position` _(layer: TX-TX35)_
  - `2:nd dewatering box` _(layer: TX-TX35)_
  - `1:st dewatering box` _(layer: TX-TX35)_
  - `Dewatering roll` _(layer: TX-TX35)_
  - `Flow (m3/min)` _(layer: TX-TX35)_
  - `115` _(layer: TX-TX35)_
  - `638` _(layer: TX-TX35)_
  - `Vacuum (-kPa)` _(layer: TX-TX35)_
  - `-25-47` _(layer: TX-TX35)_
  - `-25-40` _(layer: TX-TX35)_
  - `1` _(layer: TX-TX35)_
  - `4` _(layer: TX-TX35)_
  - `2` _(layer: TX-TX35)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx)

---

### 57. `KSDM160104107_09_SH01_Steam and condensate system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 26293 |
| Entities (CSV) | 25579 |
| XDATA entities (CSV) | 3868 |
| Connectivity (CSV) | — |

---

### 58. `KSDM160104108_06_SH01_Mill air system_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 82 |
| Entities (CSV) | 48 |
| XDATA entities (CSV) | 2 |
| Connectivity (CSV) | — |

---

### 59. `KSDM160104110_08_SH01_Internal effluent treatment_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 201 |
| Entities (CSV) | 84 |
| XDATA entities (CSV) | 1 |
| Connectivity (CSV) | — |

---

### 60. `KSDM160104111_06_SH01_Process ventilation_C.dwg`

> ❌ **Parse failed:** `DXFStructureError: missing ENDSEC tag.`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects (CSV) | 51 |
| Entities (CSV) | 41 |
| XDATA entities (CSV) | 3 |
| Connectivity (CSV) | — |

---

### 61. `KSDM160104112_05_SH01_Sealing water system_C.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇸🇪 KSD Swedish |
| DWG version | 33 |
| Last saved by | `ksdwenzhec` |
| Objects | 71 |
| Entities (model space) | 692 |
| Layers | 58 |
| Block definitions | 60 |
| Unique attribute tags | 76 |
| App ID fingerprint | IDOK ×9 | GENIUS ×1 | other: PS-PROM, IPT_DEF, AME_SOL |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 1

**Entities:** INSERT×350, LINE×166, TEXT×93, LWPOLYLINE×79, CIRCLE×3, MTEXT×1

**Layers (58):**  
`0`, `PS`, `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `AME_FRZ`, `BLANKETT`, `BLTEXT`, `PR`, `BL-BLNK`, `DEFPOINTS`, `LOGO`, `PR-KONT`, `TX-TX25`, `TX-TX35`, `TX-TX50`, `Metso-log2`, `Metso-log1`, `PS-EQUIP`, `INSTR-VALVE`, `PS-FLOOR`, `Fresh water`, `TXT-INST-VALVE`, `LA`, `HAND-VALVE`, `TXT-HAND-VALVE`, `Pipe ID`, `Pipe split`, `White water treated SCWW`, `GHD-A`, `OH-TX25`, `White water untreated`, `Revision`, `Revision 01`, `中文标注`, `INSTRUMENT`, `Revision 02`, `White water treated`, `AM_BOR` … +18 more

**Custom linetypes (1):**

  - `PHANTOM` — ______  __  __  ______  __  __  ______  __  __ 

**Block definitions (60):**

  - `PS-INIT` (0 entities)
  - `PS-INTXT` (2 entities)
  - `AME_NIL` (0 entities)
  - `AME_SOL` (0 entities)
  - `LA-INIT` (0 entities)
  - `$DDT_AUDIT_GENERATED_(4BE83D502104DCB8)` (319 entities)
  - `PS_3301` (8 entities)
  - `REVHUVUD` (22 entities)
  - `METSOHUVUD` (89 entities)
  - `DRWSTAMPMETSO` (13 entities)
  - `A$C4F874EFE` (544 entities)
  - `POSNR` (5 entities)
  - `T` (8 entities)
  - `spec` (12 entities)
  - `instr` (5 entities)
  - `PILHHL` (7 entities)
  - `PS_3201` (8 entities)
  - `PS_3203` (9 entities)
  - `S` (3 entities)
  - `ps_3901` (4 entities)
  - `SPLIT` (2 entities)
  - `RAM-A1F-2` (95 entities)
  - `PS_3204` (9 entities)
  - `PS5-2005` (8 entities)
  - `REVRUTA` (15 entities)
  - `PILV` (7 entities)
  - `PILVVL` (7 entities)
  - `Pipeid` (5 entities)
  - `Line no` (1 entities)
  - `balance` (5 entities)
  - … +30 more

**Most-used block inserts:**

  - `Pipeno` ×50
  - `SPLIT` ×50
  - `RUTA` ×43
  - `PS_3201` ×42
  - `maskinpos` ×41
  - `PS-INTXT` ×35
  - `LA-INIT` ×21
  - `AME_NIL` ×17
  - `AME_SOL` ×17
  - `PS-INIT` ×12
  - `PS_3214` ×6
  - `T` ×6
  - `PUMP POS TÄTNV` ×2
  - `PILHHL` ×1
  - `ValmetA1+210` ×1

**Attribute tags & sample values (76 unique tags):**

  - `POSNR` ×169 — `726A-001`
  - `BENÄMNING` ×88 — `SEALING WATER HEADER`
  - `PIPEID` ×50 — `180L-104`
  - `PIPEDATA` ×50 — `25-W03-VE16H2A`
  - `DESCRIPTION` ×43 — `Agitator Broke tower`
  - `TYPE` ×42
  - `MATERIAL` ×42 — `4S4`
  - `SEALING` ×42
  - `TYP` ×35
  - `KRETS` ×6 — `180HS`
  - `ROW3` ×2 — `SOFTWOOD  24-144 BDT/D`
  - `ROW4` ×2 — `HARDWOOD 96-217 BDT/D`
  - `ROW1` ×2 — `TM PRODUCTION 263 BDT/D`
  - `ROW2` ×2 — `PRODUCTION SPLIT (MAX/LINE):`
  - `STATUS` ×1 — `Certified`
  - `SIGNATURE` ×1 — `WEN`
  - `DATE` ×1 — `08/01/2023`
  - `CUSTOMER_NAME_01` ×1 — `SHOTTON`
  - `LOCATION_OF_MILL_01` ×1 — `DEESIDE, UK`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1
  - `PROJNUM_01` ×1 — `160104`
  - `ITEM_DOC_NO` ×1 — `KSDM160104112`
  - `REV` ×1 — `05`
  - `SHEET` ×1 — `1`
  - `OF_SHEET` ×1 — `1`
  - `GEN-TITLE-NAME` ×1 — `WEN`
  - `GEN-TITLE-DAT` ×1 — `11/21/2022`
  - `CHECKED` ×1 — `JNS`
  - `CDATE` ×1 — `08/01/2023`

**Text entity samples (model space):**

  - `MAX FLOW (kg/min / cons. % / LPM)` _(layer: TX-TX35)_
  - `DESIGN FLOW kg/min / cons. % / LPM` _(layer: TX-TX35)_
  - `DCS SYSTEM` _(layer: TX-TX35)_
  - `CONNECTED TO` _(layer: TX-TX35)_
  - `LOCAL` _(layer: TX-TX35)_
  - `20 / 4 / 505` _(layer: Pipe ID)_
  - `( 24 / 4 / 600 )` _(layer: Pipe ID)_
  - `PLC SYSTEM` _(layer: TX-TX35)_
  - `NAME` _(layer: TX-TX35)_
  - `MEDIA` _(layer: TX-TX35)_
  - `P95` _(layer: Pipe ID)_
  - `P96` _(layer: Pipe ID)_
  - `B88` _(layer: Pipe ID)_
  - `FLOW SUBSTANCES` _(layer: TX-TX35)_
  - `P85` _(layer: Pipe ID)_
  - `PULP, MACHINE FURNISH, BLEACHED` _(layer: Pipe ID)_
  - `PULP BLEACHED DRIED DISSOLVED SULPHATE SOFTWOOD` _(layer: Pipe ID)_
  - `WHITE WATER, SUPERFILTRATE` _(layer: Pipe ID)_
  - `B85` _(layer: Pipe ID)_
  - `WHITE WATER, PAPER MACHINE` _(layer: Pipe ID)_

**Text styles:** `STANDARD` (isocp.shx), `ISO` (isocp3.shx), `SIMPLEX` (SIMPLEX), `ISOR` (isocp3.shx), `ISOL` (ISOCP.SHX), `hz2` (romans99.shx), `ISOCP` (isocp.shx)

---

### 62. `GORA68208.04_Code 13 - P&Id Mist Removal_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 3705 |
| Entities (model space) | 1568 |
| Layers | 34 |
| Block definitions | 22 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×26 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1107, TEXT×299, CIRCLE×55, ARC×55, SOLID×24, LWPOLYLINE×17, INSERT×6, HATCH×3

**Layers (34):**  
`0`, `CARTIGLIO`, `1-AIR GOR`, `1-TAG AND INSTRUMENTS GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT`, `VIEWPORT HIDDEN`, `2-PNEUMATIC CUSTOMER`, `2-EQUIPMENT CUSTOMER`, `1-FLOW TEXT GOR`, `2-WATER CUSTOMER`, `1- DELIVERY LIMITS`, `1-VALVE TEXT GOR`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `AM_0`, `1-WATER GOR`, `1-PNEUMATIC GOR`, `1-EQUIPMENT KSD`, `1-EQUIPMENT KAWANOE`, `2-AIR CUSTOMER`, `2-WATER CUSTOMER (DOT)`, `3-FLOW TEXT`, `AM_6`, `AM_8`, `3-EQUIPMENT KSD`, `3-WATER KSD`, `2-WATER KSD`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `CADRA_CONTINUOUS` — Solid line
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _

**Block definitions (19):**

  - `LOOPDCS` (6 entities)
  - `COIL` (5 entities)
  - `SquadraturaA1` (25 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `StampPreliminary` (262 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C6B987A8E` (353 entities)
  - `ValmetStampForApproval` (107 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `_ACMFILLED30` (1 entities)
  - `_ACMEMPTY60` (3 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×4
  - `COIL` ×1
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×1 — `04`

**Text entity samples (model space):**

  - `ESTRAZIONE PA PULPER AD UMIDO` _(layer: LEGEND)_
  - `BATTERIE DI SCAMBIO ACQUA O VAPORE` _(layer: LEGEND)_
  - `IN LINE VENTURI` _(layer: LEGEND)_
  - `VENTURI IN LINEA` _(layer: LEGEND)_
  - `DRAIN MODULE` _(layer: LEGEND)_
  - `MODULO DI SCARICO` _(layer: LEGEND)_
  - `WET DUST PULPER EXHAUST` _(layer: LEGEND)_
  - `COLLETTORE AD UMIDO` _(layer: LEGEND)_
  - `WET DUST COLLECTOR` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ACQUA` _(layer: LEGEND)_
  - `AIR/WATER HEAT EXCHANGER` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ARIA` _(layer: LEGEND)_
  - `AIR/AIR HEAT EXCHANGER` _(layer: LEGEND)_
  - `+` _(layer: LEGEND)_
  - `SC` _(layer: LEGEND)_
  - `FILTRO ARIA` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `FLEXIBLE JOINT` _(layer: LEGEND)_
  - `GIUNTO FLESSIBILE` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ISOR` (ISOCP.SHX), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `MZ_text` (romans.shx)

---

### 63. `GORA68209.03_Code 13 - P&ID AdvWetDust_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 3833 |
| Entities (model space) | 2183 |
| Layers | 36 |
| Block definitions | 18 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×20 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1614, TEXT×392, CIRCLE×54, ARC×53, LWPOLYLINE×32, SOLID×25, INSERT×7, HATCH×4

**Layers (36):**  
`0`, `CARTIGLIO`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-WATER GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-PNEUMATIC GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `1-BACKPRESSURE GOR`, `VIEWPORT`, `VIEWPORT HIDDEN`, `2-PNEUMATIC CUSTOMER`, `2-EQUIPMENT CUSTOMER`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-WATER CUSTOMER`, `1- DELIVERY LIMITS`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `AM_0`, `2-PNEUMATIC KSD`, `1-EQUIPMENT KSD`, `3-EQUIPMENT KSD`, `AM_5`, `AM_6`, `BL-BLNK`, `AM_8`, `3-WATER KSD`, `2-WATER KSD`, `2-WATER CUSTOMER (DOT)`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `CADRA_CONTINUOUS` — Solid line
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _

**Block definitions (14):**

  - `LOOPDCS` (6 entities)
  - `COIL` (5 entities)
  - `SquadraturaA1` (25 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `StampPreliminary` (262 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$Ce455b4ce` (8 entities)
  - `ValmetStampForApproval` (107 entities)
  - `_ACMFILLED30` (1 entities)
  - `_ACMEMPTY60` (3 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×5
  - `COIL` ×1
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×1 — `03`

**Text entity samples (model space):**

  - `ESTRAZIONE PA PULPER AD UMIDO` _(layer: LEGEND)_
  - `BATTERIE DI SCAMBIO ACQUA O VAPORE` _(layer: LEGEND)_
  - `IN LINE VENTURI` _(layer: LEGEND)_
  - `VENTURI IN LINEA` _(layer: LEGEND)_
  - `DRAIN MODULE` _(layer: LEGEND)_
  - `MODULO DI SCARICO` _(layer: LEGEND)_
  - `WET DUST PULPER EXHAUST` _(layer: LEGEND)_
  - `COLLETTORE AD UMIDO` _(layer: LEGEND)_
  - `WET DUST COLLECTOR` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ARIA` _(layer: LEGEND)_
  - `AIR/AIR HEAT EXCHANGER` _(layer: LEGEND)_
  - `+` _(layer: LEGEND)_
  - `SC` _(layer: LEGEND)_
  - `FILTRO ARIA` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `FLEXIBLE JOINT` _(layer: LEGEND)_
  - `GIUNTO FLESSIBILE` _(layer: LEGEND)_
  - `SILENZIATORE` _(layer: LEGEND)_
  - `SILENCER` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `ACANSGDT` (amgdt.shx), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ISOR` (ISOCP.SHX), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `USER3` (ITALIC.SHX), `MZ_text` (romans.shx)

---

### 64. `GORB18781.02_Code 13 - P&ID Active AirFoil_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 3080 |
| Entities (model space) | 1523 |
| Layers | 28 |
| Block definitions | 12 |
| Unique attribute tags | 0 |
| App ID fingerprint | IDOK ×9 | GENIUS ×20 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1232, TEXT×177, CIRCLE×44, ARC×41, LWPOLYLINE×14, MTEXT×8, SOLID×4, HATCH×2

**Layers (28):**  
`0`, `CARTIGLIO`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-WATER GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-PNEUMATIC GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `2-PNEUMATIC CUSTOMER`, `2-EQUIPMENT CUSTOMER`, `1-FLOW TEXT GOR`, `2-WATER CUSTOMER (DOT)`, `1- DELIVERY LIMITS`, `1-VALVE TEXT GOR`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_0`, `1-EQUIPMENT KSD`, `2-BACKPRESSURE CUSTOMER`, `Defpoints`, `AM_6`, `AM_8`

**Custom linetypes (11):**

  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----

**Block definitions (9):**

  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `Arrow Down` (4 entities)
  - `SquadraturaA3+` (21 entities)
  - `StampPreliminary` (262 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Arrow Down` ×1

**Text entity samples (model space):**

  - `164F-740-M1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `164PS2` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `743` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164PA2` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164PS1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164PA1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `PI2` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `PI1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164F-740` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164E-060` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164E-061` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `164E-062` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `CUSTOMER` _(layer: 1- DELIVERY LIMITS)_
  - `VALMET GOR` _(layer: 1- DELIVERY LIMITS)_
  - `SC` _(layer: LEGEND)_
  - `INVERTER/CONVERTER` _(layer: LEGEND)_
  - `OTHERS` _(layer: LEGEND)_
  - `LIMITI DI FORNITURA` _(layer: LEGEND)_
  - `DELIVERY LIMITS` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ISOR` (ISOCP.SHX), `ACISOTS` (isocp.shx)

---

### 65. `GORB18782.02_Code 13 - P&ID QCS - WIS_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 2067 |
| Entities (model space) | 483 |
| Layers | 24 |
| Block definitions | 14 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×20 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×325, TEXT×89, ARC×32, CIRCLE×23, LWPOLYLINE×8, INSERT×4, HATCH×2

**Layers (24):**  
`0`, `CARTIGLIO`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-TAG AND INSTRUMENTS GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `2-EQUIPMENT CUSTOMER`, `1- DELIVERY LIMITS`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `AM_0`, `AM_6`, `VIEWPORT HIDDEN`, `3-EQUIPMENT KSD`, `AM_8`, `1-EQUIPMENT KAWANOE`, `AM_5`, `BL-BLNK`

**Custom linetypes (16):**

  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `ACISOTGL` — _ _ _ _ _

**Block definitions (10):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `SquadraturaA3+` (21 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `StampPreliminary` (262 entities)
  - `StampCertified` (262 entities)
  - `ValmetStampForApproval` (107 entities)
  - `IndiceRevisione_180°` (3 entities)

**Most-used block inserts:**

  - `IndiceRevisione_0°` ×2
  - `LOOPDCS` ×1
  - `IndiceRevisione_180°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×3 — `01`

**Text entity samples (model space):**

  - `SC` _(layer: LEGEND)_
  - `INVERTER/CONVERTER` _(layer: LEGEND)_
  - `REVISION ARROW` _(layer: LEGEND)_
  - `INDICE DI REVISIONE` _(layer: LEGEND)_
  - `VALMET GOR` _(layer: LEGEND)_
  - `CUSTOMER` _(layer: LEGEND)_
  - `LIMITI DI FORNITURA` _(layer: LEGEND)_
  - `DELIVERY LIMITS` _(layer: LEGEND)_
  - `NORMALLY CLOSE SOLENOID VALVE` _(layer: LEGEND)_
  - `NORMALLY OPEN SOLENOID VALVE` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE APERTA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE APERTA` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE CHIUSA` _(layer: LEGEND)_
  - `NORMALLY CLOSED MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE CHIUSA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL GLOBE VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE DI REG. NORM. APERTA` _(layer: LEGEND)_
  - `LINEA ARIA COMPRESSA` _(layer: LEGEND)_
  - `PNEUMATIC LINE` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ISOR` (ISOCP.SHX), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `USER3` (ITALIC.SHX)

---

### 66. `GORA68213.05_Code 14 - P&ID MHV Heat recovery_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 9893 |
| Entities (model space) | 2952 |
| Layers | 41 |
| Block definitions | 35 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×43 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1834, TEXT×459, HATCH×341, INSERT×125, LWPOLYLINE×102, CIRCLE×59, ARC×26, SOLID×5

**Layers (41):**  
`0`, `VIEWPORT HIDDEN`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `1-AIR GOR`, `1-WATER GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-PNEUMATIC GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `2-PNEUMATIC CUSTOMER`, `3-EQUIPMENT KSD`, `1-FLOW TEXT GOR`, `3-WATER KSD`, `1- DELIVERY LIMITS`, `1-VALVE TEXT GOR`, `1-BACKPRESSURE GOR`, `2-STEAM CUSTOMER`, `VIEWPORT`, `2- DELIVERY LIMITS HIDDEN`, `Defpoints`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `1-EQUIPMENT KSD`, `AM_8`, `2-EQUIPMENT CUSTOMER`, `2-WATER CUSTOMER (DOT)`, `EQUIPMENT_GRAF`, `3-PNEUMATIC KSD`, `2-TAG AND TEXT CUSTOMER`, `2-WATER CUSTOMER`, `2-AIR CUSTOMER`, `3-STEAM CUSTOMER`, `AM_5` … +1 more

**Custom linetypes (25):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGL` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `CADRA_CONTINUOUS` — Solid line
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....

**Block definitions (31):**

  - `SquadraturaA1+` (28 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `LOOPDCS` (6 entities)
  - `COIL` (5 entities)
  - `INSULATION LEG` (8 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION` (8 entities)
  - `StampPreliminary` (262 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `Pipeno` (2 entities)
  - `point` (1 entities)
  - `MetsoLogoA` (506 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `A$C632270BC` (4 entities)
  - `GORA68048.02_Code 14 - P&ID MHV Heat recovery_SWE NEPTUNE_P` (3307 entities)
  - `A$C0F9E32A6` (5 entities)
  - `A$C187B2666` (14 entities)
  - `A$C5C8A467D` (284 entities)
  - `A$C0CC74273` (320 entities)
  - `ValmetStampForApproval` (107 entities)
  - `IndiceRevisione_270°` (3 entities)
  - … +1 more

**Most-used block inserts:**

  - `Pipeno` ×45
  - `TAG VALVOLA` ×43
  - `INSULATION` ×17
  - `LOOPDCS` ×12
  - `IndiceRevisione_90°` ×3
  - `IndiceRevisione_270°` ×2
  - `COIL` ×1
  - `INSULATION LEG` ×1
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×45 — `168L-041`
  - `PIPEDATA` ×45 — `200-W38-VE10H2A`
  - `TAG_VALVOLA` ×43 — `168V-094`
  - `TIPO_VALVOLA` ×43 — `4S4-LWE-50`
  - `02` ×6 — `05`

**Text entity samples (model space):**

  - `ESTRAZIONE PA PULPER AD UMIDO` _(layer: LEGEND)_
  - `BATTERIE DI SCAMBIO ACQUA O VAPORE` _(layer: LEGEND)_
  - `IN LINE VENTURI` _(layer: LEGEND)_
  - `VENTURI IN LINEA` _(layer: LEGEND)_
  - `DRAIN MODULE` _(layer: LEGEND)_
  - `MODULO DI SCARICO` _(layer: LEGEND)_
  - `WET DUST PULPER EXHAUST` _(layer: LEGEND)_
  - `COLLETTORE AD UMIDO` _(layer: LEGEND)_
  - `WET DUST COLLECTOR` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ACQUA` _(layer: LEGEND)_
  - `AIR/WATER HEAT EXCHANGER` _(layer: LEGEND)_
  - `SCAMBIATORE ARIA/ARIA` _(layer: LEGEND)_
  - `AIR/AIR HEAT EXCHANGER` _(layer: LEGEND)_
  - `+` _(layer: LEGEND)_
  - `SC` _(layer: LEGEND)_
  - `FILTRO ARIA` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `FLEXIBLE JOINT` _(layer: LEGEND)_
  - `GIUNTO FLESSIBILE` _(layer: LEGEND)_

**Text styles:** `Standard` (txt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ROMANS` (romans), `MONOTXT` (monotxt), `ACISOGDT` (amgdt.shx), `ACANSGDT` (amgdt.shx), `ISOR` (ISOCP.SHX), `ACISOTS` (isocp.shx), `USER3` (ITALIC.SHX)

---

### 67. `GORA68267.03_Code 14 - MHV Water ring piping overview_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 6328 |
| Entities (model space) | 710 |
| Layers | 49 |
| Block definitions | 31 |
| Unique attribute tags | 40 |
| App ID fingerprint | IDOK ×9 | GENIUS ×62 | other: MCAD_NO_VIS, ACATTRIBSERVICES, EMT-PARTLIST-690612 |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Title block fields:**

- `SHEET`: 1

**Entities:** INSERT×236, LINE×236, TEXT×112, LWPOLYLINE×100, MTEXT×20, CIRCLE×6

**Layers (49):**  
`0`, `Defpoints`, `AM_BOR`, `_HEAD_PARTLIST`, `_HEAD_PLANT`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_lightgray_solid`, `Valmet_logo_color_green_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_color_lightgray_borders`, `Valmet_logo_color_green_borders`, `_HEAD_MACHINE`, `AM_0N`, `AM_3N`, `AM_9N`, `_HEAD_REV_ROW1`, `EQUIPMENT`, `VIEWPORT HIDDEN`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_black_solid`, `AM_9`, `LA-BYGG-CL`, `LA-TXT025`, `QUOTE E NOTE-AM_6`, `1-FLOW TEXT GOR`, `Pipe ID`, `Revison 03`, `05_CONCRETE VIEW`, `05_CONCRETE`, `05_STEEL VIEW`, `A-ANNO-NOTE`, `05_AXIS NAME`, `MECHEQPT`, `T-GANTRY`, `T-OLD-BUILDING`, `FLOOR DRAINS`, `05_GLASS`, `05_DOOR`, `05_WINDOW` … +9 more

**Custom linetypes (20):**

  - `ByBlock` — 
  - `ByLayer` — 
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `ACISOTGL` — _ _ _ _ _
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `CENTRUML0` — -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
  - `DASH` — dashline
  - `DASH3` — DASH3
  - `DASH4` — DASH4
  - `DDASH1` — DDASH1

**Block definitions (27):**

  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `MillRithuvud` (173 entities)
  - `ValmetStatusStamp` (130 entities)
  - `revheadA0` (13 entities)
  - `revisionA0` (15 entities)
  - `ValmetA0+1260` (271 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `SquadraturaA1+4` (38 entities)
  - `Pipeno` (2 entities)
  - `A$C4C2047AA` (2 entities)
  - `A$C40BC6A40` (1 entities)
  - `S-PRK-SCL - S-PRK-SCL_650x1100mm-1543692-GROUND FLOOR PLAN` (4 entities)
  - `Grid - M_Grid Head - Circle-45800-SECOND FLOOR PLAN` (1 entities)
  - `KUZEY-ENG - Type 1-922606-MP-GF-200` (26 entities)
  - `Spiral_Door_HS7030_EN - 4000mm W x4000mm H-1555134-GROUND FLOOR PLAN` (50 entities)
  - `A-PRK-DOR - A-PRK-DOR_1000_2200-V7-GROUND FLOOR PLAN` (46 entities)
  - `wndw` (5 entities)
  - `A$C305b5995` (2788 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_0°` (3 entities)

**Most-used block inserts:**

  - `A$C40BC6A40` ×109
  - `Pipeno` ×73
  - `A$C4C2047AA` ×41
  - `revisionA0` ×2
  - `ValmetStatusStamp` ×1
  - `MillRithuvud` ×1
  - `ValmetA0+1260` ×1
  - `revheadA0` ×1
  - `A$C305b5995` ×1
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (40 unique tags):**

  - `PIPEID` ×73 — `168L-021`
  - `PIPEDATA` ×73 — `150-W38-VE10H2A`
  - `REVISION1` ×2 — `01`
  - `REV1_ROW1` ×2 — `CIVIL AND ARCHITECTURAL UPDATED`
  - `REV1_ROW2` ×2 — `-`
  - `REV1_DATE` ×2 — `2021-03-25`
  - `REV1_DRAWN` ×2 — `KNM`
  - `REV1_CHECKED` ×2 — `KNM`
  - `REV1_APPROVE` ×2 — `MKN`
  - `STATUS` ×1 — `CERTIFIED`
  - `SIGNATURE` ×1 — `KNM`
  - `DATE` ×1 — `2020-12-18`
  - `CUSTOMER_NAME_01` ×1 — `MODERN KARTON`
  - `LOCATION_OF_MILL_01` ×1 — `-`
  - `CUSTOMERS_DRAWING_NUM_01` ×1
  - `CUSTOMERS_POSITION_NUM_01` ×1
  - `PROJNUM_01` ×1 — `643-160104`
  - `ITEM_DOC_NO` ×1 — `KSDM160104201`
  - `REV` ×1 — `02`
  - `SHEET` ×1 — `1`
  - `OF_SHEET` ×1 — `1`
  - `GEN-TITLE-NAME` ×1 — `KNM`
  - `GEN-TITLE-DAT` ×1 — `2020-09-15`
  - `CHECKED` ×1 — `-`
  - `CDATE` ×1 — `-`
  - `APPROVED` ×1 — `-`
  - `ADATE` ×1 — `-`
  - `LANG1` ×1 — `EN`
  - `LANG2` ×1 — `-`
  - `GEN-TITLE-SCA` ×1 — `1:100`

**Text entity samples (model space):**

  - `\A1;\pxt2;{\LGENERAL LOADS, design criteria} \P\pi-3,l4;-^IDISTRUBUTED LOAD 3...` _(layer: EQUIPMENT)_
  - `IMPORTANT: DEPARTMENT LAYOUT IS NOT TO BE USED FOR DETAILED DESIGN. ONLY TO B...` _(layer: EQUIPMENT)_
  - `200x150` _(layer: 1-FLOW TEXT GOR)_
  - `100x150` _(layer: 1-FLOW TEXT GOR)_
  - `100x200` _(layer: 1-FLOW TEXT GOR)_
  - `100x65` _(layer: 1-FLOW TEXT GOR)_
  - `150x100` _(layer: 1-FLOW TEXT GOR)_
  - `65x100` _(layer: 1-FLOW TEXT GOR)_
  - `65X100` _(layer: 1-FLOW TEXT GOR)_
  - `150x200` _(layer: 1-FLOW TEXT GOR)_
  - `200x100` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=1250l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=3600l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=250l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=1000l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=1350l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=850l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=500l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=2250l/min)` _(layer: 1-FLOW TEXT GOR)_
  - `(Q=2350l/min)` _(layer: 1-FLOW TEXT GOR)_

**Text styles:** `STANDARD` (ISOCP.SHX), `ACISOTS` (isocp.shx), `ACISOGDT` (AMGDT), `SIMPLEX` (SIMPLEX), `ISOCP` (isocp.shx), `ISO` (isocp2.shx), `ACANSGDT` (amgdt.shx), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `MONOTXT` (monotxt), `ISOR` (ISOCP.SHX), `Arial_B` (arialbd.ttf), `Arial_B_1` (arialbd.ttf), `Arial_5` (arial.ttf), `USER3` (ITALIC.SHX)

---

### 68. `GORB18777.05_Code 14 - P&ID Turboblower & WE Roof heating_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 5780 |
| Entities (model space) | 1823 |
| Layers | 43 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×28 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1203, TEXT×330, HATCH×86, CIRCLE×61, INSERT×56, LWPOLYLINE×40, ARC×34, SOLID×9

**Layers (43):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-FLOW TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `AM_9`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `2-AIR CUSTOMER`, `2-PNEUMATIC CUSTOMER`, `1-PNEUMATIC GOR`, `1-WATER METSO`, `3-PNEUMATIC KSD`, `3-WATER CUSTOMER`, `1-VALVE TEXT GOR`, `3-EQUIPMENT KSD`, `Pipe ID`, `Revison 03`, `1-WATER GOR`, `BUILDING`, `AM_0`, `AM_6`, `2-WATER KSD (DOT)`, `AM_8`, `AM_5` … +3 more

**Custom linetypes (23):**

  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `CADRA_CONTINUOUS` — Solid line
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `Cartiglio` (324 entities)
  - `StampPreliminary` (262 entities)
  - `TAG VALVOLA` (3 entities)
  - `Pipeno` (2 entities)
  - `INSULATION` (8 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `SquadraturaA3+4` (32 entities)
  - `StampCertified` (262 entities)
  - `ValmetStampForApproval` (107 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `GORB18777.04_Code 14 - P&ID Turboblower & WE Roof heating_SWE Shotton_CE` (1768 entities)
  - `_ACMFILLED30` (1 entities)
  - `_ACMEMPTY60` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `A$Ccbda91f5` (7 entities)

**Most-used block inserts:**

  - `TAG VALVOLA` ×24
  - `LOOPDCS` ×15
  - `Pipeno` ×7
  - `INSULATION` ×6
  - `COIL` ×1
  - `INSULATION LEG` ×1
  - `IndiceRevisione_0°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `TAG_VALVOLA` ×24 — `168V-708`
  - `TIPO_VALVOLA` ×24 — `4S4-LWE-25`
  - `PIPEID` ×7 — `168L-701`
  - `PIPEDATA` ×7 — `25-W03-VE10H2A`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `\P\PTHIS SYMBOL INDICATES A "MANUAL REGULATION VALVE" OR A MANUAL VALVE WITH ...` _(layer: 0)_
  - `GENERAL NOTES:` _(layer: 0)_
  - `FLOWREDUCER` _(layer: LEGEND)_
  - `DAMPER WITH ELECTRIC ACTUATOR` _(layer: LEGEND)_
  - `SERRANDA CON ATT. ELETTRICO` _(layer: LEGEND)_
  - `MANUAL DAMPER` _(layer: LEGEND)_
  - `SERRANDA MANUALE` _(layer: LEGEND)_
  - `REGOLATORE DI FLUSSO` _(layer: LEGEND)_
  - `THREE WAY VALVE` _(layer: LEGEND)_
  - `E. VALVOLA A TRE VIE` _(layer: LEGEND)_
  - `PRESSURE STABILIZER` _(layer: LEGEND)_
  - `STABILIZZATORE DI PRESSIONE` _(layer: LEGEND)_
  - `GAS FILTER` _(layer: LEGEND)_
  - `FILTRO GAS` _(layer: LEGEND)_
  - `NORMALLY CLOSE SOLENOID VALVE` _(layer: LEGEND)_
  - `NORMALLY OPEN SOLENOID VALVE` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE APERTA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE APERTA` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE CHIUSA` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `ISOR` (ISOCP.SHX), `USER3` (ITALIC.SHX), `MZ_text` (romans.shx)

---

### 69. `GORB18778.04_SH1(2)_Code 14 - P&ID Ventil Unit SU01_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 3422 |
| Entities (model space) | 1474 |
| Layers | 36 |
| Block definitions | 25 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×28 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×961, TEXT×269, HATCH×63, ARC×60, LWPOLYLINE×43, CIRCLE×37, INSERT×36, MTEXT×4

**Layers (36):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `AM_9`, `VIEWPORT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `2-AIR CUSTOMER`, `2- DELIVERY LIMITS HIDDEN`, `2-PNEUMATIC CUSTOMER`, `2-WATER CUSTOMER`, `Pipe ID`, `Revison 03`, `AM_8`, `AM_0`, `AM_5`, `AM_6`, `BL-BLNK`

**Custom linetypes (22):**

  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .

**Block definitions (21):**

  - `LOOPDCS` (6 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `Cartiglio` (324 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `StampCertified` (262 entities)
  - `ValmetStampForApproval` (107 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `A$Cc077d5d9` (1 entities)
  - `IndiceRevisione_180°` (3 entities)

**Most-used block inserts:**

  - `TAG VALVOLA` ×13
  - `Pipeno` ×12
  - `LOOPDCS` ×6
  - `IndiceRevisione_180°` ×2
  - `COIL` ×1
  - `INSULATION LEG` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `TAG_VALVOLA` ×13 — `168V-101`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `PIPEID` ×12 — `168L-107`
  - `PIPEDATA` ×12 — `65-W38-VE10H2A`
  - `02` ×3 — `04`

**Text entity samples (model space):**

  - `+` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `168E-101` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `UNIT SU01` _(layer: 1-AIR GOR)_
  - `168F-205` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168F-205-M1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `205` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168HC1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168HS1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168TT` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `201` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN80` _(layer: 1-FLOW TEXT GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `ISOR` (ISOCP.SHX), `USER3` (ITALIC.SHX)

---

### 70. `GORB18778.04_SH2(2)_Code 14 - P&ID Ventil Unit SU02_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 3355 |
| Entities (model space) | 1482 |
| Layers | 34 |
| Block definitions | 23 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×28 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×969, TEXT×269, HATCH×63, ARC×60, LWPOLYLINE×43, CIRCLE×37, INSERT×36, MTEXT×4

**Layers (34):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `AM_9`, `VIEWPORT`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `2-AIR CUSTOMER`, `2- DELIVERY LIMITS HIDDEN`, `2-PNEUMATIC CUSTOMER`, `2-WATER CUSTOMER`, `Pipe ID`, `Revison 03`, `AM_0`, `AM_6`, `AM_8`

**Custom linetypes (22):**

  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .

**Block definitions (20):**

  - `LOOPDCS` (6 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `Cartiglio` (324 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `StampCertified` (262 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)
  - `IndiceRevisione_180°` (3 entities)

**Most-used block inserts:**

  - `TAG VALVOLA` ×13
  - `Pipeno` ×12
  - `LOOPDCS` ×6
  - `IndiceRevisione_180°` ×2
  - `COIL` ×1
  - `INSULATION LEG` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `TAG_VALVOLA` ×13 — `168V-121`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `PIPEID` ×12 — `168L-125`
  - `PIPEDATA` ×12 — `65-W38-VE10H2A`
  - `02` ×3 — `04`

**Text entity samples (model space):**

  - `+` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `168E-121` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `UNIT SU02` _(layer: 1-AIR GOR)_
  - `168F-215` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168F-215-M1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `215` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168HC1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168HS1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168TT` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `211` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN65 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `ISOR` (ISOCP.SHX)

---

### 71. `GORB18779.05_SH1(12)_Code 14 - P&ID Ventil Unit WU01_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4583 |
| Entities (model space) | 1915 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1284, TEXT×338, ARC×84, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-306`
  - `PIPEDATA` ×16 — `65-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-301`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `301` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168TC1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `168P-300` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `300` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168HC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168TT1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `307` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168TA1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168P-300-M1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `168TT2` _(layer: 1-TAG AND INSTRUMENTS GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 72. `GORB18779.05_SH10(12)_Code 14 - P&ID Ventil Unit WU10_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4576 |
| Entities (model space) | 1901 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1281, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×49, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-490`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-481`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU10` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 73. `GORB18779.05_SH11(12)_Code 14 - P&ID Ventil Unit WU11_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-510`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-501`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU11` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 74. `GORB18779.05_SH12(12)_Code 14 - P&ID Ventil Unit WU12_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4623 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-530`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-521`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU12` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 75. `GORB18779.05_SH2(12)_Code 14 - P&ID Ventil Unit WU02_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4573 |
| Entities (model space) | 1898 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1279, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-330`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-321`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU02` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 76. `GORB18779.05_SH3(12)_Code 14 - P&ID Ventil Unit WU03_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-350`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-341`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `168TC1` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU03` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 77. `GORB18779.05_SH4(12)_Code 14 - P&ID Ventil Unit WU04_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-370`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-361`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU04` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 78. `GORB18779.05_SH5(12)_Code 14 - P&ID Ventil Unit WU05_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-390`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-381`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU05` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 79. `GORB18779.05_SH6(12)_Code 14 - P&ID Ventil Unit WU06_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4585 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 32 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (28):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `A$Ccdb34b82` (6 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-410`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-401`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU06` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 80. `GORB18779.05_SH7(12)_Code 14 - P&ID Ventil Unit WU07_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-430`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-421`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU07` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 81. `GORB18779.05_SH8(12)_Code 14 - P&ID Ventil Unit WU08_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-450`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-441`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU08` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 82. `GORB18779.05_SH9(12)_Code 14 - P&ID Ventil Unit WU09_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 4574 |
| Entities (model space) | 1899 |
| Layers | 37 |
| Block definitions | 31 |
| Unique attribute tags | 5 |
| App ID fingerprint | IDOK ×9 | GENIUS ×23 | other: ACDBBLOCKREPETAG, GradientColor1ACI, GradientColor2ACI |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×1280, TEXT×338, ARC×72, HATCH×65, CIRCLE×50, LWPOLYLINE×48, INSERT×41, MTEXT×4

**Layers (37):**  
`0`, `CARTIGLIO`, `REV-A`, `REV-B`, `CLIENTE`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `1-TAG AND INSTRUMENTS GOR`, `1-AIR GOR`, `1- DELIVERY LIMITS`, `AM_BOR`, `1-BACKPRESSURE GOR`, `2-WATER CUSTOMER (DOT)`, `1-WATER GOR`, `1-FLOW TEXT GOR`, `1-VALVE TEXT GOR`, `2-EQUIPMENT CUSTOMER`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_9`, `VIEWPORT`, `Defpoints`, `2- DELIVERY LIMITS HIDDEN`, `2-WATER KSD`, `2-PNEUMATIC CUSTOMER`, `AM_0`, `AM_6`, `Pipe ID`, `Revison 03`, `AM_5`, `BL-BLNK`, `2-AIR CUSTOMER`, `AM_8`

**Custom linetypes (23):**

  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `NASCOSTA` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `BACK_PRESSURE_GOR` — Back pressure GOR ----X----X----X----
  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `GAS_LINE` — Gas line ----GAS----GAS----GAS----GAS----GAS---
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `BACK_PRESSURE_OTHERS` — Back pressure othes ....X....X....X....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `PHANTOM` — Phantom ______  __  __  ______  __  __  ______
  - `CADRA_CONTINUOUS` — Solid line
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/

**Block definitions (27):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `COIL` (5 entities)
  - `TAG VALVOLA` (3 entities)
  - `INSULATION LEG` (8 entities)
  - `SquadraturaA3+3` (30 entities)
  - `StampCertified` (262 entities)
  - `A$C3C542838` (458 entities)
  - `IndiceRevisione_0°` (3 entities)
  - `A$C5E18478E` (1 entities)
  - `StampPreliminary` (262 entities)
  - `Pipeno` (2 entities)
  - `StampForApproval` (262 entities)
  - `Metso_Pos0` (1 entities)
  - `Metso_Pos1` (8 entities)
  - `Metso_Pos2` (8 entities)
  - `Metso_Pos3` (8 entities)
  - `Metso_Pos4` (14 entities)
  - `Metso_Pos` (5 entities)
  - `IndiceRevisione_180°` (3 entities)
  - `A$C187B2666` (14 entities)
  - `A$C2C071CCC` (1 entities)
  - `IndiceRevisione_270°` (3 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `Pipeno` ×16
  - `TAG VALVOLA` ×13
  - `LOOPDCS` ×6
  - `COIL` ×3
  - `INSULATION LEG` ×1
  - `IndiceRevisione_180°` ×1
  - `IndiceRevisione_90°` ×1

**Attribute tags & sample values (5 unique tags):**

  - `PIPEID` ×16 — `168L-470`
  - `PIPEDATA` ×16 — `40-W38-VE10H2A`
  - `TAG_VALVOLA` ×13 — `168V-461`
  - `TIPO_VALVOLA` ×13 — `2K0-BF-65`
  - `02` ×2 — `05`

**Text entity samples (model space):**

  - `M` _(layer: 2-EQUIPMENT CUSTOMER)_
  - `TO MACHINE HALL` _(layer: 1-AIR GOR)_
  - `B` _(layer: 1-FLOW TEXT GOR)_
  - `AB` _(layer: 1-FLOW TEXT GOR)_
  - `A` _(layer: 1-FLOW TEXT GOR)_
  - `CUSTOMER` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OTHERS` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `DN40 PN16` _(layer: 2- DELIVERY LIMITS HIDDEN)_
  - `OUTSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `INSIDE BUILDING` _(layer: 1-AIR GOR)_
  - `+` _(layer: 1-EQUIPMENT GOR)_
  - `MCC` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `VALMET` _(layer: 1- DELIVERY LIMITS)_
  - `GOR` _(layer: 1- DELIVERY LIMITS)_
  - `WU09` _(layer: 1-AIR GOR)_
  - `WITH AUX SWITCH` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `LOCAL DISCONNECTOR` _(layer: 1-TAG AND INSTRUMENTS GOR)_
  - `2xFLANGE` _(layer: 1-FLOW TEXT GOR)_
  - `1st UNIT` _(layer: 1-AIR GOR)_
  - `2nd UNIT` _(layer: 1-AIR GOR)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ISOR` (ISOCP.SHX), `ACANSTS` (romans.shx), `USER3` (ITALIC.SHX)

---

### 83. `GORB18780.03_Code 14 - P&ID Bale pulper Extractor_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 1886 |
| Entities (model space) | 326 |
| Layers | 22 |
| Block definitions | 13 |
| Unique attribute tags | 1 |
| App ID fingerprint | IDOK ×9 | GENIUS ×20 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×214, TEXT×77, CIRCLE×15, LWPOLYLINE×10, ARC×6, INSERT×3, HATCH×1

**Layers (22):**  
`0`, `CARTIGLIO`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-TAG AND INSTRUMENTS GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `2-EQUIPMENT CUSTOMER`, `1- DELIVERY LIMITS`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `AM_8`, `Defpoints`, `AM_0`, `AM_5`, `AM_6`, `BL-BLNK`

**Custom linetypes (17):**

  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `LINEA-LINEETTA` — ____ _ ____ _ ____ _ ____ _ ____ _ ____ _ ____ 
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `ACISOTGL` — _ _ _ _ _

**Block definitions (9):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `StampPreliminary` (262 entities)
  - `SquadraturaA3` (20 entities)
  - `StampCertified` (262 entities)
  - `ValmetStampForApproval` (107 entities)
  - `IndiceRevisione_0°` (3 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×2
  - `IndiceRevisione_0°` ×1

**Attribute tags & sample values (1 unique tags):**

  - `02` ×1 — `03`

**Text entity samples (model space):**

  - `SC` _(layer: LEGEND)_
  - `INVERTER/CONVERTER` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `VALMET GOR` _(layer: LEGEND)_
  - `CUSTOMER` _(layer: LEGEND)_
  - `LIMITI DI FORNITURA` _(layer: LEGEND)_
  - `DELIVERY LIMITS` _(layer: LEGEND)_
  - `NORMALLY CLOSE SOLENOID VALVE` _(layer: LEGEND)_
  - `NORMALLY OPEN SOLENOID VALVE` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE APERTA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE APERTA` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE CHIUSA` _(layer: LEGEND)_
  - `NORMALLY CLOSED MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE CHIUSA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL GLOBE VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE DI REG. NORM. APERTA` _(layer: LEGEND)_
  - `LINEA ARIA COMPRESSA` _(layer: LEGEND)_
  - `PNEUMATIC LINE` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `USER3` (ITALIC.SHX), `ISOR` (ISOCP.SHX)

---

### 84. `GORB18784.04_Code 14 - P&ID Machine Hall Extractors_SWE Shotton_CE.dwg`

| Field | Value |
|-------|-------|
| Ecosystem | 🇮🇹 GOR Italian |
| DWG version | 33 |
| Last saved by | `gorceschma` |
| Objects | 2311 |
| Entities (model space) | 460 |
| Layers | 22 |
| Block definitions | 15 |
| Unique attribute tags | 0 |
| App ID fingerprint | IDOK ×9 | GENIUS ×20 | other: GradientColor1ACI, GradientColor2ACI, ACCMTRANSPARENCY |
| Connectivity | ⚠️ XDATA present, no named endpoints |

**Entities:** LINE×283, TEXT×96, ARC×42, CIRCLE×27, INSERT×8, LWPOLYLINE×3, HATCH×1

**Layers (22):**  
`0`, `CARTIGLIO`, `2-AIR CUSTOMER`, `1-AIR GOR`, `1-TAG AND INSTRUMENTS GOR`, `LEGEND`, `1-EQUIPMENT GOR`, `VIEWPORT HIDDEN`, `2-EQUIPMENT CUSTOMER`, `1- DELIVERY LIMITS`, `AM_BOR`, `Valmet_logo_black_borders`, `Valmet_logo_black_hatch`, `Valmet_logo_color_gray_solid`, `Valmet_logo_color_gray_borders`, `Valmet_logo_black_solid`, `Defpoints`, `AM_0`, `AM_5`, `AM_6`, `BL-BLNK`, `AM_8`

**Custom linetypes (16):**

  - `COMPRESS_AIR_GOR` — Compress air GOR ----/\----/\----/\----
  - `COMPRESS_AIR_OTHERS` — Compress air others ..../\..../\..../\....
  - `PID_ELECTBINARY` — P&ID Elecrical Binary Line--  -- \ --  --  --  
  - `AM_ISO08W050` — ____ . ____ . ____ . ____ . ____ . ____ . ____
  - `AM_ISO08W050x2` — __ . __ . __ . __ . __ . __
  - `Amconstr` — _______________________
  - `Amzigzag2` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACANSTGB` — __ . . __ . .
  - `ACANSTGL` — _ _ _ _ _
  - `AM_ISO02W050` — __ __ __ __ __ __ __ __ __ __ __ __ __ __ __
  - `AM_ISO09W050` — _____ . . _____ . . _____ . . ____ .. ____
  - `AM_ISO02W050x2` —  _ _ _ _ _ _ _ _ _ _ _ _
  - `Amzigzag` — /\/-/\/-/\/-/\/-/\/-/\/
  - `ACISOWELD` — _ _ _ _ _
  - `ACISOTGB` — __ . . __ . .
  - `ACISOTGL` — _ _ _ _ _

**Block definitions (11):**

  - `LOOPDCS` (6 entities)
  - `Cartiglio` (324 entities)
  - `RevisioniTesta` (18 entities)
  - `RevisioniRiga` (13 entities)
  - `SquadraturaA3+` (21 entities)
  - `StampPreliminary` (262 entities)
  - `StampCertified` (262 entities)
  - `A$C32F93955` (21 entities)
  - `StampForApproval` (262 entities)
  - `IndiceRevisione_90°` (3 entities)
  - `ValmetStampForApproval` (107 entities)

**Most-used block inserts:**

  - `LOOPDCS` ×8

**Text entity samples (model space):**

  - `SC` _(layer: LEGEND)_
  - `INVERTER/CONVERTER` _(layer: LEGEND)_
  - `WASHING UNIT` _(layer: LEGEND)_
  - `UNITA' LAVAGGIO` _(layer: LEGEND)_
  - `VALMET GOR` _(layer: LEGEND)_
  - `CUSTOMER` _(layer: LEGEND)_
  - `LIMITI DI FORNITURA` _(layer: LEGEND)_
  - `DELIVERY LIMITS` _(layer: LEGEND)_
  - `NORMALLY CLOSE SOLENOID VALVE` _(layer: LEGEND)_
  - `NORMALLY OPEN SOLENOID VALVE` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE APERTA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE APERTA` _(layer: LEGEND)_
  - `E. VALVOLA NORMALMENTE CHIUSA` _(layer: LEGEND)_
  - `NORMALLY CLOSED MANUAL BALL VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE NORMALMENTE CHIUSA` _(layer: LEGEND)_
  - `NORMALLY OPEN MANUAL GLOBE VALVE` _(layer: LEGEND)_
  - `VALVOLA MANUALE DI REG. NORM. APERTA` _(layer: LEGEND)_
  - `LINEA ARIA COMPRESSA` _(layer: LEGEND)_
  - `PNEUMATIC LINE` _(layer: LEGEND)_

**Text styles:** `STANDARD` (txt), `ROMANS` (romans), `MONOTXT` (monotxt), `USER1` (TXT.SHX), `USER2` (SIMPLEX.SHX), `ACANSGDT` (amgdt.shx), `ACISOTS` (isocp.shx), `ACISOGDT` (amgdt.shx), `USER3` (ITALIC.SHX), `ISOR` (ISOCP.SHX)

---
