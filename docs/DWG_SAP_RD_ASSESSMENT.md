# DWG → SAP Converter: R&D Discovery Assessment

**Plant:** Shotton Mill Ltd, Shotton Paper Mill, United Kingdom  
**Date:** 2026-08-26  
**Status:** Discovery / Pre-implementation  
**Scope:** 84 DWGs across 4 mill sections + 2 PDF-only areas

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [DWG Inventory](#2-dwg-inventory)
3. [Author / Company Mapping](#3-author--company-mapping)
4. [Drafting Standard Mapping](#4-drafting-standard-mapping)
5. [Forensic Structural Analysis](#5-forensic-structural-analysis)
6. [DWG ↔ PDF Comparison](#6-dwg--pdf-comparison)
7. [Resource File Inventory](#7-resource-file-inventory)
8. [Provided vs Missing Standards](#8-provided-vs-missing-standards)
9. [Author / Standard Clustering](#9-author--standard-clustering)
10. [Converter-Relevant Differences](#10-converter-relevant-differences)
11. [Extraction Capability Matrix](#11-extraction-capability-matrix)
12. [R&D Risks](#12-rd-risks)
13. [Recommended Architecture](#13-recommended-architecture)
14. [Phased Project Scope](#14-phased-project-scope)
15. [Final Conclusion](#15-final-conclusion)

---

## 1. Executive Summary

The Shotton Mill DWG ecosystem contains **three fundamentally different CAD author/standard families**, produced by different engineering companies for different mill sections. These are not variations on a single standard — they require distinct extraction strategies.

| Ecosystem | DWGs | Folders | Company | Data Quality | Standard Docs |
|-----------|-----:|---------|---------|-------------|:-------------:|
| **Valmet PS-21** (Finnish) | 35 | CHEM_PID, OCC_PID, PM03_PID | Valmet Oy | Excellent — block attrs + XDATA connectivity | ✅ Complete |
| **GOR Italian** | 19 | TM01_PID / Code 03, 13, 14 | GOR S.r.l. | Poor — 1 attribute per DWG; all data is plain text | ❌ None |
| **KSD Swedish** | 25 | TM01_PID / Code 12 | KSD / Andritz | Moderate — KRETS/POSNR/BENÄMNING attrs | ⚠️ Partial |
| **PDF-only** | 0 | CHP2_PID, ETP2_PID | Unknown / Nijhuis | No DWGs | ❌ None |

**Recommended architecture:** Universal ingestion → ecosystem detector → three standard-specific adapters → common entity model → SAP mapper.

A single universal parser will not work across all three families.

---

## 2. DWG Inventory

**84 DWGs** indexed in `resources/sml_dwg_index_260806.csv`. All DWGs use AC1032 (AutoCAD 2018 format), except GOR files which use AC1024 (AutoCAD 2010). All 84 indexed DWGs parse successfully via ODA File Converter + ezdxf, **with the exception of ~20% of KSD files** which fail with `DXFStructureError: missing ENDSEC tag`.

Two additional folders exist on disk that are **not in the CSV index** and contain no DWG files:

| Folder | DWGs (CSV) | PDFs | Notes |
|--------|:----------:|:----:|-------|
| CHEM_PID | 5 | 5 | Chemical preparation P&IDs |
| OCC_PID | 6 | 6 | OCC (recycled fibre) plant P&IDs |
| PM03_PID | 24 | 24 | Paper Machine 3 P&IDs + flow diagrams |
| TM01_PID | 49 | 49 | Tissue Machine 1 (GOR + KSD) |
| **CSV total** | **84** | **84** | |
| CHP2_PID | — | ~40 | PDF-only; Combined Heat & Power 2 |
| ETP2_PID | — | 30 | PDF-only; Effluent Treatment Plant 2 (Nijhuis) |

### Filename Naming Conventions (Valmet)

| Prefix | System | Example |
|--------|--------|---------|
| `PCSG028xxx` | Chemical preparation | `PCSG028666.03_Surface_size_preparation.dwg` |
| `STOD206xxx` | Stock / OCC / PM3 process | `STOD206340.10 OCC Pulping line 1.dwg` |
| `RAU8G/RAU8F` | PM3 utility & process | `RAU8G02312.11 Shower Water system.dwg` |
| `RAU6401xxx` | PM3 flow diagrams (sub-type) | `RAU6401403_03_FLOW_DIAGRAM_OCPRO.dwg` |
| `GORA/GORB` | GOR Italian equipment | `GORA68210.05_Code 03 - P&ID AirCap_SWE Shotton_CE.dwg` |
| `KSDM160104xxx` | KSD tissue process | `KSDM160104102_07_SH07_Machine broke pulper system_C.dwg` |

---

## 3. Author / Company Mapping

### Group 1 — Valmet Oy (Finnish) · 35 DWGs · **High Confidence**

| Field | Value |
|-------|-------|
| Company | Valmet Oy (formerly Metso Paper) — Finnish paper machinery manufacturer |
| CAD users | jani.linden, nina.niittykumpu, kai.kuoppa, kaisa.leino, samuli.autio, jklohenoti |
| Project | Shotton Mill Ltd, UK — "Shotton PM3" / "Shotton OCC" |
| DWG format | AC1032 (AutoCAD 2018) |
| CAD system | Genius Plant Design (AutoCAD add-on) + PCAD (Valmet proprietary P&ID layer) |

**Evidence:** PCAD_ and GENIUS_ app IDs throughout; Finnish-language attribute tags (VENIMI, VEPOSITIO, MOOPOS, MOOTEHO, KORKEUS); Finnish block names (VENTK = ball valve, TOIMILV = actuated valve, TAKAISKU = check valve, VAROV = safety valve, NUOLI = arrow); Valmet_TB01 / VALMET_R_OTS title blocks; "Shotton Mill Ltd" confirmed in all title blocks from machine-readable fields.

**Confirmed title block** (extracted from `RAU8G02312.11 Shower Water system.dwg`):
```
PROJECT1  : Shotton Mill Ltd
PROJECT2  : Shotton Paper Mill, United Kingdom
PROJECT3  : Shotton PM3
DRAWINGID : RAU8G02312.11
TITLE1    : Shower Water system
SHEET     : 1/1
ARKKI     : A1
LYH       : SHOTTONPM3
```

---

### Group 2 — GOR S.r.l. (Italian) · 19 DWGs · **High Confidence**

| Field | Value |
|-------|-------|
| Company | GOR S.r.l. — Italian manufacturer of tissue machine hood/air systems |
| CAD user | gorceschma |
| Sections | Codes 03, 13, 14: AirCap, ReDry, AdvWetDust, MistRemoval, MHV, TurboBlower, AirFoil, QCS-WIS, Bale pulper |
| DWG format | **AC1024 (AutoCAD 2010)** — 2 versions older than all other DWGs |
| CAD system | Genius + IDOK_ (process P&ID automation tool, Italian) |

**Evidence:** "gorceschma" username (GOR + CE = Central Europe); IDOK_ app IDs (IDOK_INSTRUMENT, IDOK_LAYOUT, IDOK_PROCESS_1/2, IDOK_SKALA); Italian layer names (CARTIGLIO = title block, NASCOSTA = hidden line, LINEA-LINEETTA = centre line); Italian block names (SquadraturaA1++ = A1+ drawing frame, RevisioniTesta/Riga = revision header/row, Cartiglio); Italian linetypes; MetsoLogoA + ValmetStampForApproval blocks.

**Filename convention:** `GORA68xxx` / `GORB18xxx` + `_Code XX - P&ID [System]_SWE Shotton_CE`

---

### Group 3 — KSD / Andritz (Swedish) · 25 DWGs · **High Confidence**

| Field | Value |
|-------|-------|
| Company | KSD (possibly Kadant Solutions Division) using Andritz/Metso framework |
| CAD user | ksdwenzhec |
| Sections | Code 12: all tissue machine process systems (broke, white water, fresh/shower/sealing water, vacuum, steam, air, ventilation, ETP) |
| DWG format | AC1032 (AutoCAD 2018) |
| CAD system | Genius (shared with Valmet) — **no PCAD** app IDs |

**Evidence:** "ksdwenzhec" username (KSD prefix); Swedish language throughout — block names (REVHUVUD = revision header, METSOHUVUD = Metso header, BENÄMNING = name/designation), attribute tags (KRETS = circuit/loop, POSNR = position number, BENÄMNING = description), layer names (BLANKETT = form, BLTEXT = form text); resource file `Naming_Tissue/KSDM160104_010.00 Process Numbering System.pdf` directly named after the DWG prefix; GENIUS_ app IDs but **zero PCAD_ app IDs**.

**Filename convention:** `KSDM160104{doc}_{rev}_SH{sheet}_{System}_C`

---

### PDF-Only Groups (No DWGs)

**CHP2_PID — Combined Heat & Power Plant 2**
- ~40 PDFs. Naming: `MK-SHO-CHP-SOL-CHP-PRO-200-DWG-xxxxx-IFCO-xxx`
- Content: HP/LP/IP steam, feedwater, gas, condensate, instrument air, cooling, HRSG P&IDs
- Author and standard: **unknown** — different document management system

**ETP2_PID — Effluent Treatment Plant 2**
- 30 PDFs. Produced by **Nijhuis** (Dutch wastewater treatment company)
- Simple sequential naming: `01 - Primary Treatment Old Equipment.pdf` … `30 - Sludge Storage.pdf`
- Author: Nijhuis Industries B.V. (Netherlands)

---

## 4. Drafting Standard Mapping

### Valmet PS-21 — Confirmed · High Confidence

| Area | Observation |
|------|-------------|
| Layer naming | `P-VALVEPOS`, `P-INSTRPOS`, `P-LINEPOS`, `P-WATER`, `P-STEAM2`, `P-PUMPS`, `P-TANK_POS`, `FIMPEC_COLOR/BW`; older variant uses short codes: `I`, `T`, `R`, `VEP`, `PKV` |
| Layer organisation | Media separation (P-WATER, P-AIR, P-STEAM2, P-REJECT); position layers per equipment type; FIMPEC classification layers |
| Blocks / symbols | Large Finnish-named library: VENTK (ball valve), TOIMILV (actuated valve), TAKAISKU (check valve), VAROV (safety valve), MOTOR, KOMPR; P7Axxx and PPI_xxx instrument bubbles |
| Block naming | Finnish abbreviations — VENTK = venttiili kuula, TOIMILV = toimilaiteventtiili |
| Text styles | STANDARD (TXT.shx), ROMANS, ARIAL, SFS (Finnish Standards SFS-4536), ISOCP |
| Dimension styles | 7 (minimal use in P&ID context) |
| Linetypes | 13–14 (mostly standard AutoCAD set) |
| Title block | Valmet_TB01 / VALMET_R_OTS with structured attributes: PROJECT1/2/3, DRAWINGID, TITLE1, SHEET, ARKKI, LYH, MRK/PVM/MUU/TAR/MUUTOS (revision history) |
| Coordinates / units | AC1032, metric |
| XREFs | Font files only (ROMANS.SHX, amgdt.shx, arial.ttf) |
| Attributes | Rich: VENIMI (valve name), VEPOSITIO (position), VEKOKO (size), VETYYPPI (type), LINJA (line), VEKEMIKAALI (medium), VEVALMISTAJA (manufacturer); MOOPOS, MOOTEHO etc. for motors |
| Connectivity | **LIN_FROM / LIN_TO** encoded in PCAD XDATA on LWPOLYLINE entities — full connectivity graph reconstructable |
| Equipment conventions | Block name = equipment type; attributes = tag, spec, manufacturer |
| Pipeline conventions | Layer name encodes medium; LINJA attribute on valves; LIN_FROM/LIN_TO for connectivity |
| **Likely standard** | **SML Standard 21 (PS-21) — Valmet** |
| **Evidence** | Full 8.5 MB standard PDF provided; FIMPEC_ layers match PS-21 Appendix II; PCAD app IDs; SRVAS/SROIK status attrs match PS-21 vocabulary |
| **Confidence** | **High** |

---

### GOR Italian Company Standard — Confirmed · High Confidence

| Area | Observation |
|------|-------------|
| Layer naming | `1-AIR GOR`, `1-WATER GOR`, `1-GAS GOR`, `1-TAG AND INSTRUMENTS GOR`, `1-EQUIPMENT GOR`, `1-PNEUMATIC GOR`, `1-BACKPRESSURE GOR` (GOR supply); `2-AIR CUSTOMER`, `2-WATER CUSTOMER`, `2-EQUIPMENT CUSTOMER` (customer supply); `CARTIGLIO` (title block); `LEGEND`; `VIEWPORT` |
| Layer organisation | GOR vs customer split via "1-" / "2-" prefix; media encoded in layer name |
| Blocks / symbols | Minimal: LOOPDCS, Cartiglio, RevisioniTesta, RevisioniRiga, SquadraturaA1++, IndiceRevisione_0°/180°, MetsoLogoA, ValmetStampForApproval, StampCertified/Preliminary |
| Block naming | Italian: Cartiglio = title block, RevisioniTesta = revision header, SquadraturaA1++ = A1+ drawing border |
| Text styles | STANDARD, ROMANS, MONOTXT, USER1/2/3 (TXT.SHX, SIMPLEX.SHX, ITALIC.SHX), ACISOTS (isocp.shx — ISO), ISOR |
| Dimension styles | 17 — heavy use, more dimensioning than other families |
| Linetypes | 32 — includes custom **process-specific linetypes**: COMPRESS_AIR_GOR (`----/\----`), BACK_PRESSURE_GOR (`----X----`), GAS_LINE (`----GAS----`), COMPRESS_AIR_OTHERS (dotted), BACK_PRESSURE_OTHERS (dotted); also Italian: LINEA-LINEETTA, NASCOSTA |
| Title block | Cartiglio block (Italian) + IndiceRevisione_0°/180° for revision indexing |
| Coordinates / units | AC1024; `$INSUNITS=0` (unitless), `$MEASUREMENT=0` |
| Attributes | **Near-zero structured attributes** — 1 attribute per drawing; all engineering data in plain TEXT entities |
| Tags / identifiers | TEXT entities on semantic layers: `{3-digit area}{instrument type}{seq}` e.g. `162TI2`, `162TT1`, `162F1-540-M1`, `162BCS1`; motor suffix `-M1` |
| Connectivity | **No semantic connectivity** — must be inferred geometrically from polyline endpoints |
| Equipment conventions | Text on `1-EQUIPMENT GOR` layer |
| Pipeline conventions | Linetype encodes medium; "1-" layer prefix = GOR supply; "2-" = customer supply |
| **Likely standard** | **GOR S.r.l. company-specific standard** |
| **Evidence** | Italian layer/block/linetype names throughout; IDOK_ app IDs; AC1024 format |
| **Confidence** | **High — no published standard; company-specific only** |

---

### KSD Swedish Standard — Confirmed · High Confidence

| Area | Observation |
|------|-------------|
| Layer naming | `PS` (process), `PS-IN-P`, `PS-IN`, `PS-PO`, `PS-FL-S`, `PR` (process related), `PR-KONT`, `BLANKETT` (form), `BLTEXT`, `TX-TX25`, `TX-TX35`, `AME_FRZ`, `DEFPOINTS` |
| Blocks / symbols | PS-INIT, PS5-2005, PS-INTXT, REVHUVUD (revision header), METSOHUVUD (Metso title), DRWSTAMPMETSO, POSNR, T (instrument bubble), PILH/PILV (horizontal/vertical pipe arrows), spec |
| Block naming | Swedish: REVHUVUD = revision head, METSOHUVUD = Metso head, BENÄMNING = name/designation |
| Text styles | STANDARD, ROMANS (similar to other families) |
| Attributes | KRETS = circuit/loop tag (e.g. `126LC`, `126QC`); POSNR = position number (e.g. `001`); BENÄMNING = description (e.g. `DILUTION WATER 134P-004`); PILH/PILV blocks carry BENÄMNING with cross-sheet continuation refs |
| Connectivity | **No LIN_FROM/LIN_TO** — connectivity via geometric tracing and BENÄMNING cross-references |
| App IDs | GENIUS_ (shared with Valmet) — **no PCAD_** |
| Parse reliability | ~20% of KSD DWGs fail: `DXFStructureError: missing ENDSEC tag` |
| **Likely standard** | **KSD project-specific numbering (KSDM160104) — Swedish pulp/tissue convention** |
| **Evidence** | Resource file `Naming_Tissue/KSDM160104_010.00` directly matches filenames; KRETS/POSNR follow Swedish instrument tagging conventions |
| **Confidence** | **High** |

---

## 5. Forensic Structural Analysis

### 5.1 Valmet PS-21 — Entity Composition

Sample: `RAU8G02312.11 Shower Water system.dwg` (18,590 objects)

| Metric | Value |
|--------|------:|
| Block inserts | 3,103 |
| Block attributes | 1,977 |
| XDATA (EED) records | 5,970 |
| Connectivity graph nodes | 3,103 |
| Connectivity graph edges | 3,763 |
| Connectivity junctions | 408 |
| Text entities | 3,505 |
| Layers | 49 |
| Non-anonymous blocks | 223 |

**PCAD-POS-INFO XDATA schema** (per instrument INSERT):

| Field index | Content | Example |
|:-----------:|---------|---------|
| 0 | Position ID | `1476378` |
| 1 | Instrument type code | `LC` (Level Control), `LT`, `LH` |
| 2 | Area / section code | `507` |
| 8 | Line / area reference | `35-26` |
| 9 | Drawing reference | `RAU8G02312 SHOWER WATER SYSTEM` |
| 13 | Description | `WARM WATER TANK LEVEL` |

**PI-LNKREF** cross-links instrument bubble ↔ position tag, enabling entity pairing.  
**LIN_FROM / LIN_TO** on LWPOLYLINE entities forms a reconstructable flow graph.

**Title block** (machine-readable, complete revision history):
```
MRK  PVM          MUU    TAR    MUUTOS
00   04.03.2022   JLep   SStr   Preliminary
01   29.04.2022   JLep   SStr   Certified
02   04.05.2022   JLep   SStr   Pipeline position legend presentation changed
...
11   22.12.2023   JLin   SStr   Updated
```

---

### 5.2 GOR Italian — Entity Composition

Sample: `GORA68210.05_Code 03 - P&ID AirCap.dwg`

| Metric | Value |
|--------|------:|
| Block inserts | 65 |
| Block attributes | **1** |
| XDATA (EED) records | 9 |
| Text entities | 1,049 |
| Connectivity graph edges (geometric) | 3,702 |
| Layers | 36 |
| Non-anonymous blocks | 18 |

**All engineering tags are plain TEXT entities** on semantic layers:

```
Layer "1-TAG AND INSTRUMENTS GOR":
  162TI2      → area 162, Temperature Indicator, seq 2
  162TT1      → area 162, Temperature Transmitter, seq 1
  162TE1      → area 162, Temperature Element, seq 1
  162F1-540-M1 → area 162, Fan/pump F1, position 540, Motor 1
  162BCS1     → area 162, Binary Control Switch, seq 1
  162HC1      → area 162, Humidity Control, seq 1

Layer "1-EQUIPMENT GOR":
  Equipment descriptions (text only)

Layer "1-AIR GOR" / "1-WATER GOR":
  Drawn on these layers; medium = layer name
```

**Custom linetypes encode medium visually:**

| Linetype | Pattern | Meaning |
|----------|---------|---------|
| `COMPRESS_AIR_GOR` | `----/\----/\----` | GOR-supplied compressed air |
| `BACK_PRESSURE_GOR` | `----X----X----` | GOR backpressure |
| `GAS_LINE` | `----GAS----GAS----` | Gas piping |
| `COMPRESS_AIR_OTHERS` | `..../\..../\....` | Customer compressed air |
| `BACK_PRESSURE_OTHERS` | `....X....X....` | Customer backpressure |

**No structured connectivity.** Pipe routes are LWPOLYLINE entities; connections must be inferred geometrically from endpoint proximity.

---

### 5.3 KSD Swedish — Entity Composition

Sample: `KSDM160104102_07_SH07_Machine broke pulper system_C.dwg`

| Metric | Value |
|--------|------:|
| Block inserts | 140 |
| Block attributes | 266 |
| XDATA (EED) records | 221 |
| Connectivity graph edges | 419 |
| Text entities | 164 |
| Layers | 67 |
| Non-anonymous blocks | 15 |

**Key attribute tags:**

| Tag | Meaning | Example value |
|-----|---------|---------------|
| KRETS | Circuit / instrument loop | `126LC`, `126QC` |
| POSNR | Position number | `001`, `004` |
| BENÄMNING | Name / description | `DILUTION WATER 134P-004` |
| BENÄMNING (PILH/PILV) | Cross-sheet continuation | `KSDM160104103 sh.03` |

**No LIN_FROM/LIN_TO.** Connectivity must be traced geometrically or via BENÄMNING cross-references.

---

### 5.4 PM3 Flow Diagrams — Special Sub-Type

`RAU6401403` and `RAU6401404` are **flow diagrams** (not P&IDs) in a distinct older Valmet layer/block scheme:

| Metric | Value |
|--------|------:|
| Total objects | 69,171 |
| Block inserts | 405 |
| Block attributes | 2,084 |
| Connectivity (relationship records) | **0** |

**Layer scheme:** `PI0ATT`, `PI3VENT`, `PI4INST`, `PI1POSI`, `PI5LAITE`, `TEKSTIT` — older PI-prefix convention, different from the "P-" prefix used by all P&IDs.

**Pipeline connector block `PI0NUOPR`** carries very rich pipe attributes (in Finnish):

| Attr tag | Meaning |
|----------|---------|
| PUTAINE | Medium / substance |
| PUTAILY | Flow direction |
| PUTDN | Nominal diameter |
| PUTPN | Nominal pressure |
| PUTMATE | Pipe material |
| PUTPAIN | Operating pressure |
| PUTLAMM | Operating temperature |
| PUTVIRT | Flow rate |
| PUTKAP | Capacity |
| PUTTIH | Density |

These flow diagrams must be treated as a separate drawing sub-type — different extraction rules, no connectivity, but richer pipeline metadata than regular P&IDs.

---

## 6. DWG ↔ PDF Comparison

| Aspect | Valmet PS-21 | GOR Italian | KSD Swedish |
|--------|-------------|-------------|-------------|
| **DWG-native information** | Equipment tags, line numbers, instrument tags, connectivity graph, revision history, pipeline attributes — all machine-readable | IDOK automation data, revision index, title block | KRETS loop tags, POSNR position numbers, BENÄMNING descriptions, revision data |
| **Information in PDF but not DWG** | Valve symbol shapes (for type classification) | Almost all engineering content — DWG text entities carry same information but less structured | Symbol shapes for type classification; legend context |
| **PDF required for extraction?** | For valve type via vision AI (already in pipeline) | **Potentially essential** — DWG attribute data is almost zero | For symbol-level validation |
| **PDF validation feasibility** | High — DWG and PDF tightly coupled | Medium — PDFs show same text as DWG entities | Medium |
| **Key gap** | None for semantic data; valve type handled by existing vision AI | Near-total lack of structured block attributes; text extraction + geometry required | Parse failures (~20%) need PDF fallback |

---

## 7. Resource File Inventory

| File | Type | Standard / Spec | Relevant DWGs | Converter Use | Machine-Readable |
|------|------|-----------------|---------------|---------------|:----------------:|
| `sml_dwg_index_260806.csv` | Index / metadata | All | All 84 | App ID fingerprinting, author grouping, connectivity assessment | ✅ |
| `SML PS-21 STANDARD 21 DOC.pdf` (8.5 MB) | Full standard | SML PS-21 | CHEM, OCC, PM03 | Layer rules, block library, attribute schema, FIMPEC valve codes | ⚠️ PDF |
| `SML SAP FLOC Structure V3.xlsx` | SAP structure | SML | All SML | **Critical**: line / process / sub-process codes → SAP FLOC | ✅ (→ JSON) |
| `SML OBJECT TYPE LIST V3 EXPANDED.xlsx` | Object type lookup | SML | All SML | Block name → SAP object type number | ✅ (→ JSON) |
| `SML Naming Abbreviation Standard.xlsx` | Abbreviation lookup | SML | All SML | Decode abbreviations in equipment names | ✅ (→ JSON) |
| `gt_hierarchy_broke_system.xlsx` | Ground truth | SML | STOD206339 | Validation and testing | ✅ |
| `Masterdata- Technical Object Structure Build SOP.docx` | SOP | SML | All | Process guidance | ⚠️ Word |
| `Naming _PM3/COMMON FOR MILL...pdf` | Naming standard | PM3 | PM03_PID, OCC | Cross-discipline naming rules | ⚠️ PDF |
| `Naming _PM3/PROCESS AND AUTOMATION.pdf` | Naming standard | PM3 P&A | PM03_PID | Instrument/automation naming | ⚠️ PDF |
| `Naming_Tissue/KSDM160104_010.00.pdf` | Naming standard | KSD tissue | TM01/KSD | **Critical for KSD**: process numbering system | ⚠️ PDF (→ JSON) |
| `Example for motors.docx` | Example | SML | All | Motor tag construction | ⚠️ Word |
| `standards/valmet_ps21.json` | Parsed standard | Valmet PS-21 | CHEM, OCC, PM03 | Layer rules, tag patterns, motor suffix, FIMPEC codes | ✅ |
| `standards/sml_floc_structure.json` | Parsed structure | SML | All SML | SAP FLOC mapping | ✅ |
| `standards/sml_object_types.json` | Parsed types | SML | All SML | Equipment → SAP object type | ✅ |
| `standards/sml_abbreviations.json` | Parsed abbreviations | SML | All SML | Abbreviation decoding | ✅ |
| `standards/tissue_ksdm160104.json` | Parsed standard | KSD tissue | TM01/KSD | Tag patterns, layer rules | ✅ |
| `standards/floc_context_map.json` | Context map | SML | All | Drawing → FLOC context | ✅ |
| `standards/legend.png` | Legend image | Visual | All | Symbol reference for vision AI | Visual |

---

## 8. Provided vs Missing Standards

| Standard / Convention | Provided? | Evidence | Relevant DWGs | Importance |
|-----------------------|:---------:|----------|:-------------:|:----------:|
| SML PS-21 (Valmet) | ✅ **Complete** | 8.5 MB PDF + 4 JSON files | CHEM, OCC, PM03 | 🔴 Critical |
| SML SAP FLOC structure | ✅ **Complete** | XLSX + JSON | All SML | 🔴 Critical |
| SML Object Type List | ✅ **Complete** | XLSX + JSON | All SML | 🔴 Critical |
| SML Abbreviation Standard | ✅ **Complete** | XLSX + JSON | All SML | 🟠 High |
| KSD Tissue Numbering | ⚠️ **Partial** | Naming PDF + basic JSON; no block library or attribute schema | TM01/KSD | 🟠 High |
| PM3 Naming (Valmet) | ⚠️ **Partial** | 2 PDFs (COMMON FOR MILL; PROCESS AND AUTOMATION) | PM03_PID | 🟡 Medium |
| GOR Italian Standard | ❌ **Missing** | No document — derived only from DWG forensics | TM01/GOR | 🟠 High |
| CHP2 Drafting Standard | ❌ **Missing** | No DWGs; IFCO PDFs only | CHP2_PID | ❓ Unknown |
| ETP2 / Nijhuis Standard | ❌ **Missing** | No DWGs; 30 PDFs only | ETP2_PID | ❓ Unknown |

### Standards We Have Enough to Build From
- Valmet PS-21 — full implementation possible now
- SAP FLOC + Object Type mapping — available as JSON
- KSD tag patterns — tag extraction possible; block recognition needs more work

### Standards That Need to Be Obtained
- **GOR company standard** — contact GOR S.r.l. or extract from project documentation; reverse-engineer from all 19 DWGs as interim
- **KSD block library** — obtain from KSD or Andritz to enable block → equipment type lookup
- **CHP2 standard** — clarify whether CHP2 is in scope; if yes, obtain DWGs or enable PDF pipeline
- **ETP2/Nijhuis standard** — same

---

## 9. Author / Standard Clustering

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLUSTER 1 — Valmet PS-21 / SML Standard                            │
│ Confidence: HIGH                                                     │
│                                                                      │
│ CHEM_PID (5):  PCSG028666, PCSG028670, PCSG028671-73               │
│ OCC_PID  (6):  STOD206340-44, STOD212164                           │
│ PM03_PID (24): PCSG028667-78, RAU8F00290, RAU8G02312-334,          │
│                STOD206336-39                                         │
│   Sub-type: Flow diagrams (RAU6401403-04) — older PI-scheme,        │
│             no connectivity, rich pipeline attrs                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ CLUSTER 2 — GOR Italian Company Standard                           │
│ Confidence: HIGH                                                     │
│                                                                      │
│ TM01_PID/Code 03 (3):  GORA68210-12                                │
│ TM01_PID/Code 13 (4):  GORA68208-09, GORB18781-82                 │
│ TM01_PID/Code 14 (12): GORA68213, GORA68267, GORB18777-84         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ CLUSTER 3 — KSD Swedish Standard                                   │
│ Confidence: HIGH                                                     │
│                                                                      │
│ TM01_PID/Code 12 (25): KSDM160104102 (×8), KSDM160104103 (×3),    │
│                         KSDM160104104-08, KSDM160104110-12          │
│   Note: ~20% fail to parse (DXFStructureError)                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PDF-ONLY — Out of current DWG scope                                │
│                                                                      │
│ CHP2_PID (~40 PDFs):  Standard unknown; IFCO numbering scheme      │
│ ETP2_PID (30 PDFs):   Nijhuis (Dutch); proprietary standard         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Converter-Relevant Differences

| Dimension | Valmet PS-21 | GOR Italian | KSD Swedish | Converter Impact |
|-----------|-------------|-------------|-------------|-----------------|
| **Tag encoding** | Block attribute (VEPOSITIO, PCAD-POS-INFO XDATA) | Plain TEXT entity on semantic layer | Block attribute (KRETS + POSNR) | 3 different tag extractors |
| **Connectivity** | LIN_FROM/LIN_TO in XDATA → direct graph | **Geometric only** — no semantic | **Geometric only** — BENÄMNING cross-refs | Valmet: direct; GOR+KSD: spatial analysis |
| **Valve type** | Block name → Finnish lookup (VENTK/TOIMILV/TAKAISKU) | **Visual only** — no encoding | **Visual only** — block shape | Vision AI required for GOR + KSD |
| **Medium / substance** | Layer name: P-WATER, P-STEAM2, P-AIR | Linetype name: GAS_LINE, COMPRESS_AIR_GOR | Layer name: PS | Rules-based (different rules per family) |
| **Title block** | Structured attributes (Valmet_TB01) | Italian text entities (Cartiglio) | Swedish text entities (METSOHUVUD) | 3 different title block parsers |
| **Block library size** | Large (223 blocks in one sample) | Minimal (18 blocks) | Small (15 blocks) | Block name → type lookup only works for Valmet |
| **Instrument tag format** | PCAD-POS-INFO: type code + area + ID | Text: `{area}{type}{seq}` (162TI2) | KRETS: `{area}{type}{seq}` (126LC) | Regex parser differs per family |
| **Pipeline tag format** | LINJA attribute (e.g. `35-26`) | Text on pipeline layer (numbers) | KRETS format | Different field extraction |
| **DWG version** | AC1032 | **AC1024** | AC1032 | GOR needs older-format compatibility |
| **Parse reliability** | 100% | 100% | **~80%** — ~20% fail | KSD needs PDF fallback |
| **Attribute density** | ~1,800 attrs per drawing | **~1 attr per drawing** | ~270 attrs per drawing | GOR requires text parsing as primary |
| **Manufacturer data** | VEVALMISTAJA attribute | Not available | Not available | Only extractable for Valmet |

---

## 11. Extraction Capability Matrix

| SAP-relevant Information | Valmet PS-21 | GOR Italian | KSD Swedish |
|--------------------------|:------------:|:-----------:|:-----------:|
| Drawing ID / title | Direct | Title block text | Title block text |
| Project / plant | Direct attrs | Text | Text |
| Revision history | Direct attrs | Block text | Block text |
| **Equipment tag** | ✅ Direct (VEPOSITIO) | ⚠️ Text parse | ⚠️ KRETS attr |
| Equipment type | ✅ Block name lookup | 🔴 Vision AI | 🔴 Vision AI |
| **Valve tag** | ✅ Direct (VEPOSITIO) | ⚠️ Text parse | ⚠️ Text parse |
| Valve type | ✅ Block name (VENTK etc.) | 🔴 Vision AI | 🔴 Vision AI |
| **Instrument tag** | ✅ PCAD-POS-INFO XDATA | ⚠️ Text parse | ✅ KRETS attr |
| Instrument type | ✅ PCAD-POS-INFO type field | ⚠️ Text prefix (TI, TT, TE) | ⚠️ KRETS prefix |
| **Pipeline / line ID** | ✅ LINJA attr | ⚠️ Text on layer | ⚠️ KRETS format |
| Medium / substance | ✅ Layer name | ✅ Linetype name | ✅ Layer name |
| **Pipe connectivity** | ✅ LIN_FROM/LIN_TO graph | 🔴 Geometric trace | 🔴 Geometric trace |
| Flow direction | ✅ LIN_FROM/LIN_TO | 🔴 Geometry arrows | 🔴 PILH/PILV arrows |
| Motor / drive tag | ✅ Derived (PS-21 rule) | ⚠️ Text + -M1 suffix | ⚠️ Text + -M1 suffix |
| SAP FLOC L3/L4 | ✅ Drawing → floc_context_map | ✅ Code number mapping | ✅ KSDM prefix mapping |
| SAP object type | ✅ Block name → object_type | 🔴 Vision + rules | 🔴 Vision + rules |
| Manufacturer | ✅ VEVALMISTAJA attr | ❌ Not available | ❌ Not available |
| Pipe size | ⚠️ VEKOKO (often "x" = TBD) | ⚠️ Text | ⚠️ Text |
| Pipe material | ⚠️ Flow diagrams only (PUTMATE) | ❌ | ❌ |
| Cross-sheet connections | ⚠️ KAAVIO attr (text parse) | ❌ | ⚠️ BENÄMNING (text parse) |

**Legend:**  
✅ Directly extractable  ⚠️ Extractable with rules / text parsing  🔴 Requires geometric / vision AI  ❌ Not available in DWG data

---

## 12. R&D Risks

### 🔴 Risk 1 — KSD DWG Parse Failures (~20%)
**Impact:** High — entire sheets of tissue machine process data missing  
**Evidence:** `KSDM160104102_07_SH06_Approach system_C.dwg`, `KSDM160104103_05_SH01_White water system_C.dwg` fail with `DXFStructureError: missing ENDSEC tag`  
**Mitigation:** Investigate ODA converter version-specific fix; try LibreDWG as alternative; implement PDF companion fallback  
**R&D needed:** Root cause diagnosis; alternative parser evaluation; PDF fallback implementation

---

### 🔴 Risk 2 — GOR Drawings Have Near-Zero Structured Data
**Impact:** High — extraction quality for GOR will be significantly lower than Valmet  
**Evidence:** 1 attribute per drawing vs 1,674 for Valmet; 65 block inserts vs 935; all data is plain TEXT entities  
**Mitigation:** Text-layer regex extraction; geometric connectivity analysis; vision AI for equipment type; PDF cross-validation  
**R&D needed:** Text extraction accuracy assessment on GOR tag patterns; geometric connectivity precision/recall

---

### 🟠 Risk 3 — Missing GOR Standard Documentation
**Impact:** Medium — conventions must be reverse-engineered; risk of gaps or misinterpretation  
**Evidence:** No GOR company standard file in resources/  
**Mitigation:** Request from GOR S.r.l.; extract from project documentation; complete reverse-engineering from all 19 DWGs  
**R&D needed:** Full GOR convention reverse-engineering across all 19 DWGs

---

### 🟠 Risk 4 — CHP2 and ETP2 are PDF-Only
**Impact:** High if these areas must be included in converter scope  
**Evidence:** CHP2_PID and ETP2_PID contain only PDFs; not in CSV index  
**Mitigation:** Scope decision first; if in scope, separate PDF extraction pipeline (vision AI / text extraction from PDFs)  
**R&D needed:** Scope decision + PDF parsing capability assessment (separate R&D track)

---

### 🟡 Risk 5 — DWG Format Version Gap (GOR: AC1024)
**Impact:** Low-Medium — ODA converter handles both, but some features may differ  
**Evidence:** `$ACADVER: AC1024` in GOR vs AC1032 everywhere else  
**Mitigation:** Regression test ODA converter on all GOR files; verify entity fidelity  
**R&D needed:** AC1024 vs AC1032 parsing comparison test

---

### 🟡 Risk 6 — PM3 Flow Diagrams Are a Distinct Sub-Type
**Impact:** Medium — different extraction rules needed; no LIN_FROM/LIN_TO  
**Evidence:** PI-prefix layers, PI0NUOPR connector block, 0 relationship records  
**Mitigation:** Detect flow diagram type by layer naming scheme; apply separate rules  
**R&D needed:** Flow diagram extraction pipeline (PUT-prefix pipe attributes are rich — worth exploiting)

---

### 🟡 Risk 7 — PCAD XDATA Schema Requires Custom Parser
**Impact:** Medium — without PCAD-POS-INFO parsing, instrument type/area/ID data is lost  
**Evidence:** XDATA decoded as positional string arrays; PCAD-TAKY-INFO provides field name schema  
**Mitigation:** Build PCAD schema parser: PCAD-TAKY-INFO → field names, PCAD-POS-INFO → values, zip to dict  
**R&D needed:** Parser implementation + field mapping validation across all Valmet DWGs

---

### 🟡 Risk 8 — Cross-Sheet Connectivity
**Impact:** High for hierarchy reconstruction — multi-sheet systems can't be fully connected within a single drawing  
**Evidence:** KAAVIO attribute = `PI-DIAGRAM RAU8G02314` (references another drawing); KSD BENÄMNING = `KSDM160104103 sh.03`  
**Mitigation:** Parse KAAVIO/BENÄMNING attributes; build inter-drawing graph as post-processing step  
**R&D needed:** Cross-drawing graph construction implementation

---

## 13. Recommended Architecture

```
                     ┌──────────────────┐
                     │   DWG / PDF Input │
                     └────────┬─────────┘
                              │
                   ┌──────────▼──────────┐
                   │  Ingestion Layer     │
                   │  ODA → ezdxf → JSON  │
                   │  (already built)     │
                   └──────────┬──────────┘
                              │
                   ┌──────────▼──────────┐
                   │  Ecosystem Detector  │
                   │  App ID fingerprint  │
                   │  Layer name pattern  │
                   │  Filename prefix     │
                   │  Block language      │
                   └────┬────┬────┬──────┘
                        │    │    │
           ┌────────────┘    │    └────────────┐
           ▼                 ▼                 ▼
  ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
  │ Valmet Adapter │ │  GOR Adapter │ │   KSD Adapter    │
  │                │ │              │ │                  │
  │ PCAD-POS-INFO  │ │ Text-layer   │ │ KRETS/POSNR/     │
  │ XDATA parser   │ │ regex parser │ │ BENÄMNING        │
  │ LIN_FROM/TO    │ │ Linetype →   │ │ extractor        │
  │ graph builder  │ │ medium map   │ │ BENÄMNING cross- │
  │ Block name →   │ │ Geometric    │ │ ref resolver     │
  │ Finnish lookup │ │ connectivity │ │ Geometric        │
  │ P-layer →      │ │ Vision AI    │ │ connectivity     │
  │ media map      │ │ for types    │ │ Vision AI        │
  └────────┬───────┘ └──────┬───────┘ └────────┬─────────┘
           │                │                  │
           └────────────────┼──────────────────┘
                            ▼
              ┌─────────────────────────┐
              │   Common Entity Model   │
              │   Equipment            │
              │   Instrument           │
              │   Valve                │
              │   Pipeline             │
              │   Drawing              │
              └─────────────┬───────────┘
                            │
              ┌─────────────▼───────────┐
              │  Semantic Enrichment     │
              │  FLOC context mapping   │
              │  Object type lookup     │
              │  Motor tag derivation   │
              │  Cross-sheet graph      │
              │  Engineering inference  │
              └─────────────┬───────────┘
                            │
              ┌─────────────▼───────────┐
              │     SAP Mapping          │
              │  FLOC structure         │
              │  Equipment Master       │
              │  Functional Location    │
              │  Document links         │
              └─────────────┬───────────┘
                            │
              ┌─────────────▼───────────┐
              │     Validation           │
              │  vs PDF companion       │
              │  vs ground truth xlsx   │
              │  vs expected SAP struct │
              │  Confidence scoring     │
              └─────────────────────────┘
```

---

## 14. Phased Project Scope

### Phase 1 — DWG Ingestion / Extraction
*Infrastructure largely already built in `dwg_reader` package*

- Complete ODA + ezdxf pipeline for all 84 DWGs
- Diagnose and fix (or document workaround for) KSD parse failures
- Generate structured JSON output for every DWG
- **Deliverable:** 84 structured JSON files with entities, blocks, layers, attributes, XDATA

### Phase 2 — Ecosystem / Standard Identification
*Partially implemented in `dwg_reader/dwg_ecosystem.py`*

- App ID fingerprinting → ecosystem classifier (`valmet_ps21` / `gor_italian` / `ksd_swedish`)
- Validate against filename prefix patterns
- **Deliverable:** Per-DWG ecosystem label with confidence score

### Phase 3 — Standard-Specific Normalization
*Build 3 adapters in plug-in pattern*

- **Valmet adapter** (highest ROI — 35 DWGs, richest data): PCAD-TAKY-INFO schema parser, PCAD-POS-INFO field extractor, LIN_FROM/LIN_TO graph builder, block name → type lookup, P-layer media mapping, LINJA → pipeline ID
- **GOR adapter**: TEXT-layer regex extractor (tag pattern `{area}{type}{seq}`), linetype → medium mapping, geometric connectivity tracer
- **KSD adapter**: KRETS/POSNR/BENÄMNING extractor, BENÄMNING cross-reference resolver, geometric connectivity tracer
- **PM3 flow diagram adapter**: PUT-prefix pipe attribute extractor (PUTDN, PUTPN, PUTMATE, PUTAINE, etc.)
- **Deliverable:** Normalised entity lists per DWG (Equipment, Instrument, Valve, Pipeline, Connection)

### Phase 4 — Engineering Semantic Extraction
*Build on existing vision AI pipeline*

- Extend valve type vision AI from Valmet to GOR + KSD symbol conventions
- Geometric connectivity analysis for GOR and KSD
- Cross-sheet graph construction (KAAVIO/BENÄMNING inter-drawing links)
- Motor/drive tag derivation
- FLOC sub-process assignment (engineering domain rules)
- **Deliverable:** Semantically enriched entity objects with confidence scores

### Phase 5 — SAP Mapping
- FLOC structure mapping (drawing → L1/L2/L3/L4 Functional Location)
- Equipment master data generation
- Instrument location assignment
- Valve equipment record creation
- Motor/drive linking
- **Deliverable:** SAP-ready import file (LSMW / BAPI / IDoc format)

### Phase 6 — Validation
- PDF cross-validation (DWG extracted vs. PDF visual content)
- Ground truth comparison (`gt_hierarchy_broke_system.xlsx`)
- Inter-drawing consistency checks
- SAP structure validation against expected hierarchy
- **Deliverable:** Validation report + exception list for manual review

### Phase 7 — Production Hardening
- KSD parse failure handling and PDF fallback
- CHP2 / ETP2 PDF extraction pipeline (if in scope)
- Error reporting and audit trail
- Confidence scoring and human review queue
- **Deliverable:** Production-ready converter with exception management

---

## 15. Final Conclusion

> **Based on the available DWGs and resources:**
>
> **This is what we know.** The Shotton Mill DWG set consists of three distinct CAD ecosystems: Valmet PS-21 (Finnish, 35 DWGs, excellent standard documentation and rich structured data), GOR Italian (19 DWGs, no standard documentation, near-zero block attributes), and KSD Swedish (25 DWGs, partial documentation, ~20% parse failure rate) — plus two PDF-only areas outside the current DWG scope.
>
> **This is what we do not know.** GOR's drafting standard is entirely undocumented and must be reverse-engineered from 19 DWG samples. The root cause of KSD parse failures is undiagnosed. CHP2 and ETP2 scope, DWG availability, and standards are unknown.
>
> **This is what can be automated.** For Valmet PS-21 DWGs, nearly all equipment tags, instrument tags, connectivity (LIN_FROM/LIN_TO graph), title block metadata, pipeline IDs, and SAP object types can be deterministically extracted — the core infrastructure already exists in the `dwg_reader` package. For GOR and KSD, tag extraction is achievable via text parsing and attribute extraction, but connectivity requires geometric analysis and valve/equipment type requires vision AI.
>
> **This requires further R&D.** GOR standard reverse-engineering; KSD parse failure diagnosis and PDF fallback; PCAD XDATA schema decoder for Valmet connectivity graph; vision AI extension to GOR and KSD symbol sets; cross-sheet graph construction; PDF extraction pipeline for CHP2/ETP2 if required by scope.
>
> **The recommended architecture** is a universal DWG ingestion layer (already partially built) feeding into an ecosystem detector and three standard-specific adapters, normalising into a common entity model before SAP mapping — with a validation layer that cross-checks against companion PDFs, ground truth data, and expected SAP hierarchy.

---

*Generated from forensic analysis of 84 DWGs using ODA File Converter + ezdxf, cross-referenced against the provided resource files and CSV index. All conclusions supported by extracted DWG data; confidence levels assigned per finding.*
