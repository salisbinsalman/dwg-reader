# Standard addendum — KSD / Andritz (KSDM160104)

Do **not** emit Valmet tags (`35-24P518`, `.1` motors) or GOR WU-unit ids.

Tag grammar: `xyyz-aaa` e.g. `122E-001`, `126P-001`, `180T-001`.
  x = machine (1=TM01), yy = area (22=softwood, 26=broke, 32=white water, 80=fresh water…),
  z = function letter, aaa = running number.

FUNCTION is a primary equipment ITEM tag (`122E-001`, `126P-001`, `126A-001`), not a valve or line.

Letters: E=machine, A=agitator, P=pump, T=tank, V=valve, L=line, X=other.
Instruments: `KRETS` + `POSNR` → `126LC-001`. If POSNR is already a full tag (`180V-152`),
use POSNR as-is — do not compose `180LC-180V-152`.
Lines: `126L-002` (PIPEID). Spec string `200-P96-VE10H2A` is PIPEDATA, not a tag.

Motors: append `-M1` only on driven E/A/P/X (`122E-001-M1`). Never invent motors for
tanks, valves, or lines.

CAD: HAND-VALVE = manual (HV), INSTR-VALVE = control (AV).
BENÄMNING is a description / cross-sheet name — not a tag.

## Worked example — pulper / pump package
```
FUNCTION=122E-001  description=122E-001 SW PULPER
EQUIPMENT:
  122E-001            ← self (the machine)
  122E-001-M1         ← drive motor
  122A-001            ← agitator on this vessel (if drawn on it)
  122L-001            ← connected line
SUB-EQUIPMENT under 122L-001:
  122V-001            ← hand valve on that line
EQUIPMENT (instruments on the vessel):
  122LC-001
```

## KSD-only rules

- Prefer ITEM / KRETS / PIPEID strings from the dossier over guessed tags.
- Valves `###V-###` sit under the line they are drawn on, not under the mill area code.
- Peer equipment with a different area code (e.g. 126 vs 122) → `peers`.
- Description style: `122E-001 SW PULPER`, `126P-001 PMP`, `126LC-001 LVL CTRL`.
