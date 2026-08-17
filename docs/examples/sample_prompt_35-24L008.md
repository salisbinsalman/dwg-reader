# P&ID hierarchy — dossier + worked examples (GT sheet format)

You are a senior tagging engineer filling a CMMS hierarchy sheet from a P&ID crop.
Match the ground-truth workbook style exactly.

## Locked plant context
- SITE: Shotton Paper Mill, United Kingdom
- LINE: Shotton PM3
- PROCESS: Broke System
- SUB-PROCESS: BR1
- FUNCTION (parent equipment tag): 35-24L008

## CAD dossier for this parent (use as evidence; still verify on the image)
Parent tag: 35-24L008
Parent category/block: process_equipment / PPI_1302A-25_0
Parent XY: (660.0, 297.5)
Nearby descriptions: WINDER PULPER; HP-33G2; 800 BDTPD

Same-tag CAD family:
- process_equipment @ (660.0,297.5) block=PPI_1302A-25_0 nearby=35-24L008; 35-24P509
- motors @ (680.0,232.5) block=PPI_1504A-25_0 nearby=35-24L008; 35-24P509
- valves @ (672.5,242.5) block=PPI_0900A nearby=35-24L008; 35-24P509
- valves @ (691.25,312.5) block=PPI_0900A nearby=35-24L008
- valves @ (661.75,310.0) block=PPI_0900A nearby=35-24L008
- valves @ (691.25,332.5) block=PPI_0900A nearby=35-24L008; 35-24
- valves @ (651.25,260.0) block=PPI_0900A nearby=35-24L008; 35-24P509
- instruments @ (707.8420054295607,267.5) block=PPI_0100X nearby=35-24L008

Nearby line numbers (short ids preferred in output):
- 35-24-015  full=35-24-015-WAF-125-E10H2A  d=147  layer=P-LINEPOS
- 35-24-016  full=35-24-016-WAF-250-E10H2A  d=197  layer=P-LINEPOS
- 35-24-011  full=35-24-011-PP-250-E10H2A  d=107  layer=P-LINEPOS
- 35-24-007  full=35-24-007-PP-200-E10H2A  d=80  layer=P-LINEPOS
- 35-24-002  full=35-24-002-PP-500-E10H2A  d=181  layer=P-LINEPOS
- 35-24-013  full=35-24-013-PP-600-E10H2A  d=120  layer=P-LINEPOS
- 35-24-009  full=35-24-009-PP-600-E10H2A  d=46  layer=P-LINEPOS

Nearby devices (valves/instruments/pumps/…):
- line_markers: PPI_1100A  d=48  block=PPI_1100A
- valves: PPI_0900A  d=113  block=PPI_0900A
- control_valves: PPI_1000A  d=195  block=PPI_1000A
- instruments: PPI_1205A  d=164  block=PPI_1205A
- pumps: P7A0200  d=56  block=P7A0200
- motors: PPI_1504A-25_0  d=68  block=PPI_1504A-25_0
- fittings: P7A1214  d=168  block=P7A1214

Nearby peer primary equipment (do NOT nest under parent):
- 35-24P509 (pumps, d=56)

Nearby drawing text tokens:
- A1  d=62  layer=P-TEXT
- A2  d=55  layer=P-TEXT
- 2 bar  d=120  layer=P-TEXT
- 1 bar  d=64  layer=P-TEXT
- S2  d=107  layer=P-TEXT
- S6  d=70  layer=P-TEXT
- S1  d=129  layer=P-TEXT
- S5  d=72  layer=P-TEXT
- S3  d=33  layer=P-TEXT
- GEARBOX 1  d=196  layer=P-OTHER
- 800 BDTPD  d=24  layer=P-TEXT
- 35-24  d=187  layer=P-INSTRPOS_TEXTS
- SHOWER S3  d=194  layer=P-TEXT
- 35-24L008  d=7  layer=P-EQUIPMENT_POS
- HP-33G2  d=16  layer=P-EQUIPMENT_POS
- 516  d=200  layer=P-INSTRPOS_TEXTS
- 504  d=185  layer=P-INSTRPOS_TEXTS
- 511  d=110  layer=P-INSTRPOS_TEXTS
- 510  d=125  layer=P-INSTRPOS_TEXTS
- 509  d=160  layer=P-INSTRPOS_TEXTS
- 508  d=140  layer=P-INSTRPOS_TEXTS
- WINDER PULPER ROTOR 1  d=153  layer=P-TEXT
- 513  d=112  layer=P-INSTRPOS_TEXTS
- 665  d=182  layer=P-INSTRPOS_TEXTS
- 691  d=155  layer=P-INSTRPOS_TEXTS
- 501  d=185  layer=P-INSTRPOS_TEXTS
- 35-24P509  d=87  layer=P-PUMP_POS
- 300  d=92  layer=P-PUMP_POS
- 28  d=85  layer=P-PUMP_POS
- 110  d=96  layer=P-PUMP_POS
- 1000  d=90  layer=P-PUMP_POS
- 35-24-008.4  d=179  layer=P-MOTOR_POS
- 1,5  d=182  layer=P-MOTOR_POS
- 1500  d=177  layer=P-MOTOR_POS
- 35-24-008.3  d=166  layer=P-MOTOR_POS
- 35-24-008.1  d=88  layer=P-MOTOR_POS
- 200  d=93  layer=P-MOTOR_POS
- 35-24-008.2  d=73  layer=P-MOTOR_POS
- 35-24-187  d=159  layer=P-VALVEPOS
- 003-50  d=160  layer=P-VALVEPOS

## Candidate tags near the crop (prefer short forms)
35-24L008, 35-24P509, 35-24-180, 35-24-1094, 35-24-226, 35-24-178, 35-24-009, 35-24-181, 35-24, 35-24-1088, 35-24-008.2, 35-24-184, 35-24-007, 35-24-008.1, 35-24LV2-513, 35-24-1100, 35-24-011, 35-24-013, 35-24LV1-513, 35-24-015, 35-24-172, 35-24-173, 35-24-187, 35-24-186, 35-24-008.3, 35-24-174, 35-24-008.4, 35-24-002, 35-24NV-504, 35-24-016, 35-24TV-9251, 35-24HV-516, 35-24-1089, 35-24-185, 35-24-1116, 35-24XV-665

---

## Worked examples (learn the PATTERN — do not copy these tags unless they appear for 35-24L008)

### Example A — vessel / pulper style
```
SUB-PROCESS=BR1
FUNCTION=35-24L001
EQUIPMENT rows (first level):
  35-24LC-101          <- level / consistency instrument on the vessel
  35-24-101            <- nozzle / connected line short id
  35-24-102
  35-24L001.1          <- local point / branch on the machine
  35-24-001.1
SUB-EQUIPMENT rows (nested under a line/spool above):
  under 35-24-102 -> 35-24-104   (valve / fitting on that spool)
```

### Example B — pump style
```
SUB-PROCESS=BR1
FUNCTION=35-24P501
EQUIPMENT:
  35-24P501            <- optional self row for the pump
  35-24-501.1          <- motor / local id
  35-24-111            <- suction line short id
  35-24-112            <- discharge line short id
SUB-EQUIPMENT under suction/discharge lines:
  35-24-113, 35-24LV1-501, 35-24XS-501, 35-24XSV-501
```

### Rules those examples teach
1. FUNCTION cell = the parent **tag string**, never a sentence.
2. Children are **tags only**.
3. Line numbers use **short** form `35-24-192` — never `35-24-192-PP-200-E10H2A`.
4. One of EQUIPMENT or SUB-EQUIPMENT per row (XOR).
5. Nest valves / interlocks under the line/spool they sit on.
6. Peer major equipment (other pumps/vessels) → `peers`, not children.
7. If a control valve / XS clearly belongs to the **peer pump**, do not hang it under a vessel FUNCTION.

---

## Your job for FUNCTION=35-24L008
Build the same shape for `35-24L008` using the screenshot + dossier.
Omit anything you cannot defend. Prefer dossier line short-ids that are visibly attached.

## STRICT JSON only
{
  "sub_process": "BR1",
  "function": "35-24L008",
  "rows": [
    {"equipment": "TAG", "subequipment": "", "mask": ""},
    {"equipment": "", "subequipment": "NESTED-TAG", "mask": ""}
  ],
  "peers": [{"tag": "PEER-TAG", "evidence": "why peer"}],
  "notes": [],
  "confidence": "high"
}