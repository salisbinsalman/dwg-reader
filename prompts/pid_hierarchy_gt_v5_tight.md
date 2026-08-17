# P&ID hierarchy — dossier + GT clone (tight)

Role: CMMS tagging engineer. Output must match GT column nesting.

## Context
SITE=$site | LINE=$line | PROCESS=$process | SUB-PROCESS=$sub_process | FUNCTION=$tag

## CAD dossier
$parent_dossier

## Whitelist candidates
$candidates

## Teach-by-example (pattern only)
For a pump FUNCTION=35-24P501 the GT-like sheet is:
- EQUIPMENT: 35-24P501, 35-24-501.1, 35-24-111, 35-24-112
- SUB-EQUIPMENT under those lines: 35-24LV1-501, 35-24-113, 35-24XS-501
For a vessel FUNCTION=35-24L001:
- EQUIPMENT: 35-24LC-101, 35-24-101, 35-24-102, 35-24L001.1, 35-24-001.1
- SUB-EQUIPMENT: 35-24-104 under the related line

## Hard rules
1. FUNCTION=$tag (tag string).
2. Short line ids only (35-24-192).
3. XOR EQUIPMENT/SUB-EQUIPMENT per row.
4. Peers (other major equipment) not nested.
5. Do not invent tags absent from image+dossier+whitelist.
6. Prefer dossier nearby lines that attach to $tag.

## JSON only
{"sub_process":"$sub_process","function":"$tag","rows":[{"equipment":"TAG","subequipment":"","mask":""}],"peers":[],"notes":[],"confidence":"high"}
