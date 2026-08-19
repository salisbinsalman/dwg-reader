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

### Example A — vessel / pulper style (full depth)
```
FUNCTION=35-24L010  description=35-24L010 WIRE PIT PLPR

EQUIPMENT rows (direct children of the function):
  35-24LC-576          ← level/consistency instrument mounted on vessel body
  35-24-013            ← overflow/drain LINE connected to vessel (standalone line)
  35-24-011            ← drain LINE connected to vessel
  35-24L010.1          ← gearbox unit 1 (rotor/gearbox sub-assembly, NOT a motor)
  35-24-010.1          ← main drive motor of gearbox 1
  35-24L010.2          ← gearbox unit 2
  35-24-010.2          ← main drive motor of gearbox 2
  35-24-009            ← pump suction LINE leaving vessel

SUB-EQUIPMENT rows (nested one level under an EQUIPMENT above):
  under 35-24-011:   35-24-1100  ← drain valve on the drain line (HV bowtie symbol)
  under 35-24L010.1: 35-24-010.3 ← oil pump motor for gearbox 1 (.3 = oil pump sub-motor)
                     35-24PI-NNN ← pressure indicator on gearbox 1
  under 35-24L010.2: 35-24-010.4 ← oil pump motor for gearbox 2 (.4 = oil pump sub-motor)
                     35-24PI-NNN ← pressure indicator on gearbox 2
  under 35-24-009:   35-24-1088  ← flush valve on suction line (bowtie symbol)
                     35-24-181   ← drain valve on suction line (bowtie symbol)
                     35-24-226   ← isolation valve on suction line (bowtie symbol)
```

### Example B — pump style (full depth)
```
FUNCTION=35-24P510  description=35-24P510 COUCH PIT PMP

EQUIPMENT rows:
  35-24P510            ← self-row: the pump unit itself
  35-24-510.1          ← pump motor (numeric matches function: 510 → 510)
  35-24-126            ← discharge LINE (main pipe leaving pump)
  35-24-127            ← suction LINE (main pipe entering pump)

SUB-EQUIPMENT rows (nested under the line they physically sit on):
  under 35-24-126:  35-24-072   ← bleed valve NC on discharge line (bowtie)
                    35-24-062   ← flush valve NC on discharge line (bowtie)
                    35-24-065   ← drain valve NC on discharge line (bowtie)
                    35-24LV-NNN ← auto level valve on discharge line
                    35-24NI-NNN ← consistency instrument on discharge
                    35-24XS-NNN ← sample control on discharge
                    35-24XSV-NNN ← sample manual valve
  under 35-24-127:  35-24-NNN   ← isolation valve on suction line (bowtie)
```

### Example C — process LINE as FUNCTION (not a vessel/pump)
When $tag is a line number (`35-24-NNN`), the FUNCTION is the header line itself.
Children are connected branches / spools plus valves and instruments on that circuit.
Do NOT attach neighbouring vessels or pumps as children.
```
FUNCTION=35-24-008  description=35-24-008 PROC LINE
EQUIPMENT:
  35-24-1089           ← branch / spool off this header
SUB-EQUIPMENT under that spool:
  35-24PI-9252, 35-24FI-9253, 35-24FS-506
```
Typical line pattern: one EQUIPMENT branch, then PI / FI / FS (or HV/HS/HI triplets) nested under it.
If $tag is an instrument (LC/PI/FV/XS/…) and no labelled accessories sit on it, emit the FUNCTION header + description only — empty `rows` is correct.

---

## Rules those examples teach

1. FUNCTION cell = the parent **tag string**, never a sentence.
2. Children are **tags only**.
3. Line numbers use **short** form `35-24-192` — never `35-24-192-PP-200-E10H2A`.
4. One of EQUIPMENT or SUB-EQUIPMENT per row (XOR).
5. **Nest valves and instruments under the line/spool they physically sit on** as SUB-EQUIPMENT:
   ```
   EQUIPMENT:  35-24-100          ← main connected line
   SUB-EQUIPMENT under 35-24-100:
     35-24-NNN  (drain valve on that line — bowtie symbol)
     35-24-NNN  (flush valve on that line — bowtie symbol)
   ```
   A valve symbol (bowtie / triangle pair) always means SUB-EQUIPMENT, regardless of tag format.
   Do NOT list those valves as top-level EQUIPMENT siblings of the line.

6. **Plain numeric `35-24-NNN` tags can be valves, not lines.**
   In this plant, hand isolation valves often carry plain `35-24-NNN` tags (no HV/FV letter prefix).
   Identify them by their symbol on the drawing — a bowtie or triangle pair means it is a VALVE:
   - If it looks like a **line** (horizontal/vertical run with a line-number label) → EQUIPMENT
   - If it looks like a **bowtie / valve symbol** (even with a plain numeric tag) → SUB-EQUIPMENT under its parent line
   The GT description always starts with `HV 35-24-NNN` for these valve tags.

7. **Gearbox sub-components** for vessel functions (L###):
   - `35-24L###.1` / `35-24L###.2` = gearbox housing units → EQUIPMENT
   - `35-24-###.1` / `35-24-###.2` = **main drive motors** for those gearboxes → EQUIPMENT
   - `35-24-###.3` / `35-24-###.4` = **oil pump sub-motors** → SUB-EQUIPMENT under the gearbox (`.1` / `.2`)
   - `35-24PI-NNN` on a gearbox = pressure indicator → SUB-EQUIPMENT under the gearbox
   Example: for function 35-24L003, `.3` goes under L003.1, `.4` goes under L003.2.

8. Peer major equipment (other pumps/vessels) → `peers`, not children.
9. If a control valve / XS clearly belongs to the **peer pump**, do not hang it under a vessel FUNCTION.
10. `description` is the SAP Functional Location Description (PLTXT):
    - MAX 40 characters, UPPERCASE
    - CMMS style: start with the tag, then abbreviated noun phrase
    - Prefer SML abbreviations: PLPR, PMP, MTR, TNK, VLV, SHW, SUCT, DIS, DRN, LVL, AGI
    - No sentences, no commas if avoidable, no quotes
11. **Motor / branch numeric rule**: a motor or branch tag ending `.1` / `.2` must share the same numeric base as $tag. For FUNCTION `35-24L004` include `35-24-004.1` ✓ but NOT `35-24-003.1` ✗. If a motor/branch does not match — even if visible in the image — put it in `peers`.
12. **Scope boundary**: the crop shows neighbouring systems too. Only include a line/instrument/valve as a child if it is clearly labelled as part of $tag's own circuit. If a tag's numeric base or label belongs to a different function, put it in `peers` or omit it entirely.
13. **Line FUNCTION**: if $tag looks like `35-24-NNN` (no L/P/T letter), treat it as a piping header. Prefer branches + on-line instruments/valves. Never list a vessel/pump (L### / P### / T###) as a child of a line FUNCTION.
14. **Valve child descriptions — type token**: a P&ID legend is provided as Image 2.
    For each valve child you emit (tag prefix HV/FV/XV/LV/CV/PV/BV, **or a plain `35-24-NNN` bowtie symbol**),
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
