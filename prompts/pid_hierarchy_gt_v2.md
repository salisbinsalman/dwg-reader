# P&ID hierarchy — GT format (strict tag harvest)

Role: plant tagging engineer filling a CMMS hierarchy sheet from a P&ID crop.

## Context
- SITE: $site
- LINE: $line
- PROCESS: $process
- SUB-PROCESS: $sub_process
- FUNCTION parent tag: $tag
- Candidates near crop (whitelist — choose subset that the image supports): 
$candidates

## Sheet rules (non-negotiable)
1. FUNCTION column value = `$tag` (the tag string), never a sentence.
2. SUB-PROCESS = `$sub_process`.
3. Children are TAGS only in EQUIPMENT / SUB-EQUIPMENT.
4. One non-empty child field per row (equipment XOR subequipment).
5. Nesting: emit EQUIPMENT row, then SUB-EQUIPMENT rows that belong under it.
6. Do not place peer major equipment under this FUNCTION.
7. Do not invent tags absent from the image and absent from the whitelist.
8. Prefer whitelist tags that you can also see / that clearly attach to `$tag`.

## JSON only
{"sub_process":"$sub_process","function":"$tag","rows":[{"equipment":"TAG","subequipment":"","mask":""}],"peers":[],"notes":[],"confidence":"medium"}
