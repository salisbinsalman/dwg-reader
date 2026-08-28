# Standard addendum — GOR Fiorentini (KSDM160104 numbering, Italian CAD)

Do **not** emit Valmet tags (`35-24P518`, `.1` motors, `PP-EE` line specs).

Tag grammar: `{unit}{letters}[-]{seq}` e.g. `168P-410`, `168F-415`, `168V-521`, `168TC1`.
Unit prefix is mill+area (162=AirCap, 168=ventilation, 160=mist, 164=wet dust).
FUNCTION is the ventil unit id: `WU12` / `WU05`, or the 3-digit prefix `168` on Code 03/13.

Equipment letters: E A P T X F. Valve letters: V ST VX KV HV FV. L = line.
Two or more ISO letters (TC, TT, PT, LC, …) = instrument.
A hyphen does **not** mean equipment — `168V-521` is a valve.

Motors: append `-M1` to driven equipment (`168P-410-M1`, `168F-415-M1`).
Not for tanks, valves, lines, or instruments.
Safety valves are irregular: `168-ST521`, `168ST-061`, `168-ST-096` — all ST valves.

Code 14: TAG VALVOLA blocks carry the real tag + TIPO_VALVOLA. Prefer those tags.
Nest `168V-522` as SUB-EQUIPMENT under line `168L-522` when the numeric suffix matches.
Code 03/13: tags are split TEXT (`162F1` + `540` + `M1` → fan `162F-540` + motor `162F-540-M1`).
Reassemble split tags from the crop; do not leave fragments as separate children.

Foreign layers (KSD, Kawanoe, Metso, China) are not this unit — omit or `peers`.

## Worked example — Code 14 ventil unit
```
FUNCTION=WU12  description=WU12 VENTIL UNIT
EQUIPMENT:
  168F-415            ← fan
  168F-415-M1         ← fan motor (SUB-EQUIPMENT under the fan if nested, else EQUIPMENT)
  168P-410            ← pump
  168L-522            ← pipe line
SUB-EQUIPMENT under 168L-522:
  168V-522            ← valve whose suffix matches the line
  168V-521            ← other valve on that spool if drawn there
EQUIPMENT (instruments on the unit, not on a line):
  168TC1, 168TT1
```

## GOR-only rules

- Prefer candidate PIPEID line tags (`168L-###`) as EQUIPMENT; valves go under the matching line.
- If the unit description says `N VLV`, emit all N inventory valves (`168V-###`) that sit in the crop — do not keep only the left-hand manifold.
- Every `168L-###` in the candidate/dossier list that is drawn inside the unit box is EQUIPMENT.
- TIPO codes (BF, LWE, ST, VX, FL) describe the valve — do not invent a second tag from TIPO.
- Blind flange (FL) is not a valve child.
- Description style: `168P-410 PMP`, `168F-415 FAN`, `168V-521 VLV NC`, `168L-522 PIPE`.
