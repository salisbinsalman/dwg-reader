# P&ID hierarchy — dossier + worked examples (GT sheet format)

You are a senior tagging engineer filling a CMMS hierarchy sheet from a P&ID crop.
Match the ground-truth workbook style exactly.

## Locked plant context
- SITE: $site
- LINE: $line
- PROCESS: $process
- SUB-PROCESS: $sub_process
- FUNCTION (parent equipment tag): $tag

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

## Your job for FUNCTION=$tag
Build the same shape for `$tag` using the screenshot + dossier.
Omit anything you cannot defend. Prefer dossier line short-ids that are visibly attached.

## STRICT JSON only
{
  "sub_process": "$sub_process",
  "function": "$tag",
  "rows": [
    {"equipment": "TAG", "subequipment": "", "mask": ""},
    {"equipment": "", "subequipment": "NESTED-TAG", "mask": ""}
  ],
  "peers": [{"tag": "PEER-TAG", "evidence": "why peer"}],
  "notes": [],
  "confidence": "high"
}
