CRITICAL: Output ONLY one JSON object. No markdown, no prose, no steps.
Format: {"type": "TOKEN", "attachment": "none"}

Classify the P&ID symbol tagged {TAG} using Image 5 (legend) as the only symbol dictionary.
This prompt is used for ALL drawing standards: SML/Shotton, GOR, Valmet PS-21, and others.
The legend covers every symbol type you may encounter across all standards.

Allowed "type" tokens:
  HV, NC, GLV, CHK, 3WV, SV, AV, AV-M, PRV, PLUG, AAV, GF, YSTR
Allowed "attachment" values:
  none, DRN, FLS, SMP

IMAGES
  Image 1 = marked crop. Yellow ring ≈ target. Follow the leader from "{TAG}" to the symbol.
  Image 2 = tight clean zoom of the target body (no ring) — fill, globe circle, check bar, actuator.
  Image 3 = below-target strip — drainage sump / trough.
  Image 4 = branch context — flushing L-hook, sampling funnel, 3rd port.
  Image 5 = legend (authoritative). Orange/red on navy. P&ID ink may be white or red; fill meaning is identical.

Ignore letters inside the tag ({TAG}). Classify the drawing symbol only.

════════════════════════════════════════
A. FIND THE TARGET (Image 1)
════════════════════════════════════════
Trace the leader / tag line from "{TAG}" to the symbol it touches. Classify that symbol only.
If the leader is unclear, use the symbol at the yellow-ring centre.
Nearby neighbours, title-block copies, and other tags are irrelevant.
If no valve/fitting/service symbol is visible → still pick the nearest bowtie/check/fitting at the ring.

════════════════════════════════════════
B. FITTINGS (Image 2) — check these FIRST
════════════════════════════════════════
  PLUG  — pipe end capped with a short perpendicular T-bar. No bowtie.
  AAV   — square (or diamond) with an X, stem down. Automatic AIR VENT / deaerator.
  GF    — upright rectangle with a dashed midline (gas filter).
  YSTR  — pipe with a 45° Y-branch stub (Y STRAINER). Not a bowtie.

════════════════════════════════════════
C. VALVE BODY (Image 2)
════════════════════════════════════════
Inspect EACH triangle of a bowtie separately (left vs right, or top vs bottom).
Solid fill = white, red, orange, or any opaque colour. Outline = dark interior, thin edges only.

INK CONVENTION (applies to all drawing standards):
  SML/Shotton: white ink on dark background = SOLID fill = NC or service-point valve.
  GOR: red/orange ink on navy legend; same token meanings apply to white/red on the drawing.
  Valmet PS-21: coloured fills follow the same legend conventions.
  In all cases: both triangles the same shade → both solid (NC) or both outline (HV) — never CHK.

BODY TABLE (first matching row wins):

  AV-M  Circle containing a readable letter M on a stem attached to the bowtie.

  AV    Actuator circle or solenoid box on a STEM that extends AWAY from the bowtie body.
        The stem is a visible rod connecting the bowtie junction to a circle/box that is
        physically OUTSIDE AND SEPARATED FROM the bowtie triangles.
        ⚠ AV cannot have the circle sitting BETWEEN or INSIDE the triangle tips — that is GLV.
        Tag letters (HV/FV/LV) do not make AV.

  SV    Safety / relief: angled body with a zigzag spring on the stem and a T-cap.

  PRV   Pressure reducing: bowtie plus stem to a circle/diaphragm with a downward pilot line.

  3WV   Three triangles meeting at one point (T), no actuator. Manual three-way.

  GLV   GLOBE VALVE (manual regulating, normally open):
        TWO OUTLINE triangles with a SMALL CIRCLE sitting AT THE BOWTIE CENTRE — at the exact
        point where the two triangle tips touch each other.
        The circle is the globe seat; it is INSIDE the bowtie body, not on a stem.
        ⚠ GLV requires BOTH triangles to be OUTLINE (hollow/empty interior, no fill).
          If EITHER triangle looks solid-filled → this is NOT GLV.
          Solid triangles + any nearby circle or hook = NC with a service-point attachment.
        ⚠ GLV circle vs AV actuator:
          GLV: circle is AT the junction of the two triangles — no stem between circle and body.
          AV:  circle is connected via a visible stem/rod that extends OUTSIDE the body.
        Works for GOR, SML, and Valmet drawings: the globe seat is always inside the bowtie.

  CHK   CHECK VALVE (non-return):
        (GOR) one solid triangle pointing flow-direction + a vertical bar at the tip; or two
              solid triangles pointing the SAME way split by a vertical bar.
        (SML) bowtie with EXACTLY ONE triangle solid-filled + the other outline-only.
        Also CHK if a diagonal bar crosses the bowtie centre.
        ⚠ Only pick CHK when the fill difference between the two triangles is CLEAR AND DISTINCT.
          If both triangles look identical (same shade, same fill) → NC or HV, not CHK.

  NC    Hand valve normally closed: BOTH bowtie triangles solid-filled. No actuator.
        When BOTH triangles appear the same shade (both white, both grey, both coloured) → NC.
        Ambiguous or identical fill → default to NC, not CHK.
        NC valves often carry a service-point attachment (DRN, FLS, SMP).
        ⚠ A solid bowtie near any small circle, L-hook, or pipe stub = NC + attachment, NOT GLV.

  HV    Hand valve normally open: BOTH bowtie triangles outline-only (hollow/empty interior).
        No centre circle, no actuator, no third triangle.
        Only pick CHK over HV when one triangle is CLEARLY more filled than the other.

NC / HV / CHK / GLV are mutually exclusive.

════════════════════════════════════════
D. SERVICE-POINT ATTACHMENT (Images 2, 3, 4)
════════════════════════════════════════
Attachments sit on a valve body (usually NC / solid bowtie). Pick EXACTLY one.

  SMP  SAMPLING — filled bowtie plus a hook/stem ending in a FUNNEL or small downward triangle.
       Not a floor sump box.

  FLS  FLUSHING — a short service stub ending in an OPEN BLUNT PIPE END pointing into open air.
       An L-hook or horizontal spool with NO arrow, funnel, or enclosure at the tip.
       ⚠ FLS vs DRN: if the stub end is OPEN with nothing there → FLS.
         If the stub end has arrows, funnel, or an enclosure → DRN.

  DRN  DRAINAGE — a branch from THIS bowtie (the one labeled {TAG}) reaches a floor drain/sump:
       • Large solid white downward arrows on THIS branch line → DRN
       • A row of small solid downward arrows (3–8 in a band) on THIS branch → DRN
       • A funnel or trapezoid at THIS branch end, with a further arrow/channel below → DRN
       • THIS branch entering a rectangular box, U-trough, sump recess, or basin → DRN
       ⚠ Drain indicators beside a DIFFERENT bowtie (with a different tag label visible nearby)
         do NOT count for this valve. Only what is directly attached to the {TAG} bowtie.
       Parallel branches each reaching the same tou → each is DRN.

  none No service-point geometry on THIS symbol.

Decision order: SMP → FLS → DRN → none.
Key FLS/DRN test: branch end is OPEN (→ FLS) or has ARROWS/FUNNEL/ENCLOSURE (→ DRN).
Do not mark DRN just because a drain trough exists elsewhere in the crop.

════════════════════════════════════════
E. EXAMPLES (legend → JSON)
════════════════════════════════════════
  Outline bowtie, nothing else                   → {"type":"HV","attachment":"none"}
  Solid bowtie, nothing else                     → {"type":"NC","attachment":"none"}
  Outline bowtie + circle AT triangle tips       → {"type":"GLV","attachment":"none"}
  Solid triangle pointing one way + vertical bar → {"type":"CHK","attachment":"none"}
  Half-filled bowtie (one solid, one open)       → {"type":"CHK","attachment":"none"}
  Solid bowtie + stepped line into a box         → {"type":"NC","attachment":"DRN"}
  Solid bowtie + two large downward arrows        → {"type":"NC","attachment":"DRN"}
  Solid bowtie + row of small downward arrows     → {"type":"NC","attachment":"DRN"}
  Solid bowtie + funnel/trapezoid then U-channel  → {"type":"NC","attachment":"DRN"}
  Solid bowtie + dedicated L-hook (open end)      → {"type":"NC","attachment":"FLS"}
  AV/actuator + funnel below → pipe to trough     → {"type":"AV","attachment":"DRN"}
  Solid bowtie + funnel (sampling cup)            → {"type":"NC","attachment":"SMP"}
  Solid bowtie near any circle or hook           → {"type":"NC","attachment":"FLS"} (not GLV)
  Outline bowtie + stem circle with M            → {"type":"AV-M","attachment":"none"}
  Bowtie + circle on external stem (GOR or SML) → {"type":"AV","attachment":"none"}
  Y-branch strainer                              → {"type":"YSTR","attachment":"none"}
  Both triangles same shade (ambiguous)          → {"type":"NC","attachment":"none"} (not CHK)

Return JSON only.
