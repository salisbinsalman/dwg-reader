# P&ID hierarchy — dossier + FLOC description (GT sheet format)

You are a senior tagging engineer filling a CMMS hierarchy sheet from a P&ID crop.
Match the ground-truth workbook style exactly.

## Locked plant context
- SITE: $site
- LINE: $line
- PROCESS: $process
- SUB-PROCESS: $sub_process
- FUNCTION (parent equipment tag): $tag
- SAP path hint (do not invent other plants): $floc_path

## CAD dossier for this parent (use as evidence; still verify on the image)
$parent_dossier

## Candidate tags near the crop (prefer short forms)
$candidates

---

## Worked examples (learn the PATTERN — do not copy these tags unless they appear for $tag)

### Example A — vessel / pulper style
```
SUB-PROCESS=BR1
FUNCTION=35-24L001
description=35-24L001 PRESS PLPR
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
description=35-24P501 PRESS PLPR PMP
EQUIPMENT:
  35-24P501            <- optional self row for the pump
  35-24-501.1          <- motor / local id
  35-24-111            <- suction line short id
  35-24-112            <- discharge line short id
SUB-EQUIPMENT under suction/discharge lines:
  35-24-113, 35-24LV1-501, 35-24XS-501, 35-24XSV-501
```

### Example C — process LINE as FUNCTION (not a vessel/pump)
When $tag is a line number (`35-24-NNN`), the FUNCTION is the header line itself.
Children are connected branches / spools plus valves and instruments on that circuit.
Do NOT attach neighbouring vessels or pumps as children.
```
SUB-PROCESS=BR1
FUNCTION=35-24-008
description=35-24-008 PROC LINE
EQUIPMENT:
  35-24-1089           <- branch / spool off this header
SUB-EQUIPMENT under that spool:
  35-24PI-9252, 35-24FI-9253, 35-24FS-506
```
Typical line pattern: one EQUIPMENT branch, then PI / FI / FS (or HV/HS/HI triplets) nested under it.
If $tag is an instrument (LC/PI/FV/XS/…) and no labelled accessories sit on it, emit the FUNCTION header + description only — empty `rows` is correct.

### Rules those examples teach
1. FUNCTION cell = the parent **tag string**, never a sentence.
2. Children are **tags only**.
3. Line numbers use **short** form `35-24-192` — never `35-24-192-PP-200-E10H2A`.
4. One of EQUIPMENT or SUB-EQUIPMENT per row (XOR).
5. **Nest valves and instruments under the line/spool they physically sit on** as SUB-EQUIPMENT (not as top-level EQUIPMENT). This applies to all pipe-line tags (35-24-NNN), including PP-200 and PP-250 lines:
   ```
   EQUIPMENT:  35-24-100          ← PP-250 main line
   SUB-EQUIPMENT under 35-24-100:
     35-24-XXX  (drain valve on that line)
     35-24-YYY  (isolation valve on that line)
   ```
   Do NOT list those valves as top-level EQUIPMENT siblings of the line — they must nest under it.
6. Peer major equipment (other pumps/vessels) → `peers`, not children.
7. If a control valve / XS clearly belongs to the **peer pump**, do not hang it under a vessel FUNCTION.
8. `description` is the SAP Functional Location Description (PLTXT):
   - MAX 40 characters, UPPERCASE
   - CMMS style: start with the tag, then abbreviated noun phrase
   - Prefer SML abbreviations: PLPR, PMP, MTR, TNK, VLV, SHW, SUCT, DIS, DRN, LVL, AGI
   - No sentences, no commas if avoidable, no quotes
9. **Motor / branch numeric rule**: a motor or branch tag ending `.1` / `.2` must share the same numeric base as $tag. For FUNCTION `35-24L004` include `35-24-004.1` ✓ but NOT `35-24-003.1` ✗. If a motor/branch does not match — even if visible in the image — put it in `peers`.
10. **Scope boundary**: the crop may show equipment from a neighbouring system. Only include a line/instrument/valve as a child if it is clearly labelled as part of $tag's own circuit. Equipment whose numeric base or label belongs to a different function goes in `peers` or is omitted entirely.
11. **Line FUNCTION**: if $tag looks like `35-24-NNN` (no L/P/T letter), treat it as a piping header. Prefer branches + on-line instruments/valves. Never list a vessel/pump (L### / P### / T###) as a child of a line FUNCTION.
12. **Valve child descriptions — type token**: a P&ID legend is provided as Image 2.
    For each valve child you emit (tag prefix HV/FV/XV/LV/CV/PV/BV, or description contains VLV/VALVE),
    look at its symbol body + all attachments in Image 1 and append token(s) to its `description`:
      `AV-M` – automatic with electrical motor actuator (circle containing M on top of bowtie)
      `AV`  – automatic: circle actuator on top of bowtie (no M). Process-controlled: do NOT also add NC or NO.
      `NC`  – normally closed: BOTH triangles are solid WHITE / fully filled (on this dark drawing filled = white, not black)
      `HV`  – hand valve: BOTH triangles are TRANSPARENT / outline-only (dark background shows through) and there is no actuator circle on top
      `CHK` – check valve: one triangular half filled, or a directional arrow/bar showing flow direction
      `PRV` – pressure reducing: bowtie with a small dome, triangle, or hat element on one side
      `SV`  – safety/relief valve: diagonal spring element with a small disc or flap (relief symbol)
      `FLS` – flushing: short stub from the SIDE of the bowtie, then a 90° downward L-hook on the valve body (legend flushing is usually white-filled + L-hook → `NC FLS`). Not a process-line tee.
      `SMP` – sampling: bowtie with a downward branch ending in a fork, Y, or sampling symbol
      `DRN` – drain: zoom out below the valve; a downward branch into a U-shaped drain trough / basin (legend DRAINAGE). Often `DRN NC`.
      `NO`  – normally open — hand valves only, never with AV / AV-M
    A white-filled bowtie is NEVER `HV`. An outline/transparent bowtie with no actuator is NEVER `NC`.
    Append token(s) at end of description — multiple qualifiers allowed if clearly present:
      `"35-24HV-548 ISOL VLV AV"` or `"35-24-131 DRN VLV DRN NC"` or `"35-24-207 VLV NC FLS"`.
    IMPORTANT: If the valve has ANY attachment, branch, or fill — use the specific token, NOT `HV`.
    If the symbol is too small or unclear to identify attachments, omit the token entirely — do NOT default to `HV`.

---

## Your job for FUNCTION=$tag
Build the same shape for `$tag` using the screenshot + dossier.
Omit anything you cannot defend. Prefer dossier line short-ids that are visibly attached.
Always include a good `description` for the FUNCTION itself.
Optionally include `description` on child rows (same 40-char rules).

## STRICT JSON only
{
  "sub_process": "$sub_process",
  "function": "$tag",
  "description": "TAG SHORT LABEL MAX 40 CHARS",
  "rows": [
    {"equipment": "TAG", "subequipment": "", "mask": "", "description": ""},
    {"equipment": "", "subequipment": "NESTED-TAG", "mask": "", "description": ""}
  ],
  "peers": [{"tag": "PEER-TAG", "evidence": "why peer"}],
  "notes": [],
  "confidence": "high"
}
