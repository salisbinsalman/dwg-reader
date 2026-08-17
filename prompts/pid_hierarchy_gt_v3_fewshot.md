# P&ID hierarchy — few-shot GT clone

You fill CMMS hierarchy sheets from P&ID crops. Match this exact style.

## Locked
SITE=$site | LINE=$line | PROCESS=$process | SUB-PROCESS=$sub_process | FUNCTION=$tag
Candidates (whitelist): $candidates
CAD hint: $parent_category | $nearby_text

## Example of correct shape (for a different tag — learn the PATTERN only)
SUB-PROCESS=BR1, FUNCTION=35-24L009
then EQUIPMENT tags such as 35-24LC-674, 35-24-189, 35-24-190
with SUB-EQUIPMENT under a line/spool such as 35-24-194 beneath 35-24-190
FUNCTION cell is the equipment TAG, never a sentence.
Children are TAGS only. One of EQUIPMENT or SUB-EQUIPMENT per row.

## Your task for FUNCTION=$tag
Harvest owned child tags from the screenshot (and whitelist only when visually supported).
Peers = other major equipment — do not nest them.

## JSON only
{
  "sub_process": "$sub_process",
  "function": "$tag",
  "rows": [
    {"equipment": "TAG", "subequipment": "", "mask": ""},
    {"equipment": "", "subequipment": "NESTED-TAG", "mask": ""}
  ],
  "peers": [],
  "notes": [],
  "confidence": "high"
}
