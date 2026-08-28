# Standard addendum — SML / Valmet PS-21

Tag grammar: `PP-EE{letter}{seq}` e.g. `35-24P518`, `35-24L009`, `35-24T601`.
Motor: strip the type letter, append `.1` → `35-24-518.1`.
Line short form: `35-24-192` — never emit the long spec `35-24-192-PP-200-E10H2A`.
Gearbox housings (`.1` / `.2` on the vessel tag, plus oil-pump `.3` / `.4`) apply
**only when $tag is an L### vessel**. Never emit `P###.1`/`.2` gearbox housings
or `P###.2`/`.3`/`.4` on a pump — a pump's only motor child is `35-24-NNN.1`.

Abbreviations: PLPR, PMP, MTR, TNK, VLV, SHW, SUCT, DIS, DRN, LVL, AGI.

## Worked examples (PATTERN only — do not copy these tags unless they appear for $tag)

### Example A — vessel / pulper
```
FUNCTION=35-24L010  description=35-24L010 WIRE PIT PLPR
EQUIPMENT: 35-24LC-576, 35-24-013, 35-24-011, 35-24L010.1, 35-24-010.1, 35-24L010.2, 35-24-010.2, 35-24-009
SUB-EQUIPMENT under 35-24-011: 35-24-1100
SUB-EQUIPMENT under 35-24L010.1: 35-24-010.3, 35-24PI-NNN
SUB-EQUIPMENT under 35-24-009: 35-24-1088, 35-24-181, 35-24-226
```

### Example B — pump (no gearbox)
```
FUNCTION=35-24P510  description=35-24P510 COUCH PIT PMP
EQUIPMENT: 35-24P510 (self), 35-24-510.1 (motor only — not .2/.3/.4), 35-24-126 (discharge LINE), 35-24-127 (suction LINE)
SUB-EQUIPMENT under 35-24-126: valves and instruments sitting on that line
Do NOT emit 35-24P510.1 / .2 / .3 / .4 — those gearbox forms are for L### vessels only.
```

### Example C — process LINE as FUNCTION
When $tag is `35-24-NNN` (no L/P/T letter), FUNCTION is the header line.
Children are branches / spools plus on-line valves and instruments.
Do NOT attach neighbouring vessels or pumps as children.

## SML-only rules

- Plain numeric `35-24-NNN` tags can be **valves**, not lines. Identify by symbol:
  line-number label on a pipe run → EQUIPMENT; bowtie → SUB-EQUIPMENT under its parent line.
  GT descriptions for those valves start with `HV 35-24-NNN`.
- Motor / branch `.1` / `.2` must share the numeric base of $tag
  (`35-24L004` → `35-24-004.1` yes, `35-24-003.1` no → peers).
- Line FUNCTION: never list a vessel/pump (`L###` / `P###` / `T###`) as a child.
- Valve description examples: `"35-24HV-548 ISOL VLV AV"` or `"35-24-131 DRN VLV DRN NC"`.
