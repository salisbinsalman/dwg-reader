# P&ID hierarchy — dossier + exact GT teaching examples

You are filling a CMMS hierarchy sheet. Columns and nesting must match the GT workbook.

## Locked
SITE=$site | LINE=$line | PROCESS=$process | SUB-PROCESS=$sub_process | FUNCTION=$tag

## CAD dossier for $tag
$parent_dossier

## Whitelist candidates
$candidates

---

## Teaching examples (PATTERN — fictional tags, copy the shape)

### Vessel / pulper FUNCTION
```
BR1
BR1 | 35-24L001
     EQUIPMENT: 35-24LC-101
     EQUIPMENT: 35-24-101
     EQUIPMENT: 35-24-102
        SUB-EQUIPMENT: 35-24-104
     EQUIPMENT: 35-24L001.1
     EQUIPMENT: 35-24-001.1
     EQUIPMENT: 35-24L001.2
     EQUIPMENT: 35-24-001.2
     EQUIPMENT: 35-24-103
        SUB-EQUIPMENT: 35-24-105
        SUB-EQUIPMENT: 35-24-106
        SUB-EQUIPMENT: 35-24-107
```

### Pump FUNCTION
```
BR1 | 35-24P501
     EQUIPMENT: 35-24P501
     EQUIPMENT: 35-24-501.1
     EQUIPMENT: 35-24-111
        SUB-EQUIPMENT: 35-24-113
        SUB-EQUIPMENT: 35-24-112
        SUB-EQUIPMENT: 35-24LV1-501
        SUB-EQUIPMENT: 35-24XS-501
        SUB-EQUIPMENT: 35-24XSV-501
     EQUIPMENT: 35-24-114
        SUB-EQUIPMENT: 35-24LV2-501
        SUB-EQUIPMENT: 35-24-115
     EQUIPMENT: 35-24-116
     EQUIPMENT: 35-24-101   <- shared interconnect line may appear under multiple FUNCTIONs
```

### Lessons
1. FUNCTION = parent tag string ($tag), not a sentence.
2. Short line ids only (`35-24-192`), never full `…-PP-200-E10H2A`.
3. Look for `TAG.1` / `TAG.2` and `35-24-00N.1` style points on vessels.
4. Look for `XS-` / `XSV-` / `LV` on pump suction/discharge.
5. Peer major equipment stays in `peers`.
6. Do not dump every nearby line — only owned nozzles/spools.
7. Local panel HS/ES/KI/KJ buttons are out of scope for this sheet.

## Task
Build the same shape for FUNCTION=$tag using the image + dossier.

## JSON only
{"sub_process":"$sub_process","function":"$tag","rows":[{"equipment":"TAG","subequipment":"","mask":""}],"peers":[],"notes":[],"confidence":"high"}
