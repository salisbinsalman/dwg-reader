"""
Generate docs/DWG_FORENSIC_ANALYSIS.html
Self-contained, searchable, filterable forensic analysis of all 84 DWGs.
Includes per-DWG block/tag → function/equipment/valve mapping section.
"""
from __future__ import annotations
import csv, json, pathlib

BASE = pathlib.Path(__file__).parent.parent
INV  = json.load(open(BASE / "outputs/dwg_per_file_inventory.json", encoding="utf-8"))
ROWS = list(csv.DictReader(open(BASE / "resources/sml_dwg_index_260806 (1).csv", encoding="utf-8")))
OUT  = BASE / "docs/DWG_FORENSIC_ANALYSIS.html"

# ── Vocabulary sets for evidence ──────────────────────────────────────────────
FINN_ATTR_TAGS = {
    "VENIMI":"valve name","VEPOSITIO":"position","VEKOKO":"size",
    "VETYYPPI":"type","VEKEMIKAALI":"medium/chemical","VEVALMISTAJA":"manufacturer",
    "IVENIMI":"instrument name","LINJA":"pipeline ID","MOOPOS":"motor position",
    "MOOTEHO":"motor power","KORKEUS":"height","VEPAINE":"pressure",
    "VELAMPO":"temperature","SRVAS":"status responsible","SROIK":"status corrected",
    "KAAVIO":"cross-drawing ref","LAINIMI":"equipment name","LAIPOS":"equipment position",
    "LAIKAPA":"capacity","LAIMTEH":"rated power","LAIKIER":"rotation speed",
    "LAIJANN":"shaft tension",
}
FINN_BLOCKS    = ["VENTK","TOIMILV","TAKAISKU","VAROV","NUOLI","MOTOR","KOMPR","SEK2",
                  "VENT","TOIM","PUTK","PI0NUOPR","FIMPEC"]
ITA_LAYERS     = ["CARTIGLIO","NASCOSTA","LINEA-LINEETTA","VIEWPORT","LEGEND"]
ITA_BLOCKS     = ["RevisioniTesta","RevisioniRiga","Cartiglio","SquadraturaA1",
                  "IndiceRevisione","MetsoLogoA","ValmetStampForApproval",
                  "StampCertified","StampPreliminary"]
GOR_LINES      = ["COMPRESS_AIR_GOR","BACK_PRESSURE_GOR","GAS_LINE",
                  "COMPRESS_AIR_OTHERS","BACK_PRESSURE_OTHERS"]
SWE_BLOCKS     = ["REVHUVUD","METSOHUVUD","DRWSTAMPMETSO","PILH","PILV","POSNR"]
SWE_ATTRS      = {"KRETS":"circuit/loop tag","POSNR":"position number",
                  "BENÄMNING":"name/description","PIPEID":"pipe ID",
                  "PIPEDATA":"pipe data","TYPE":"type"}
SWE_LAYERS     = ["PS","BLANKETT","BLTEXT","DEFPOINTS","PS-IN","PS-PO","PS-FL"]

# ── Block → mapping table ─────────────────────────────────────────────────────
# (category, SAP/process role, description, icon)
BLOCK_EXACT: dict[str, tuple] = {
    # Valmet Valves
    "VENTK":        ("Valve",        "Hand valve (ball/gate)",         "Instrument → SAP Valve record; type: HV",       "🔵"),
    "VENT":         ("Valve",        "Valve (generic)",                "Instrument → SAP Valve record",                 "🔵"),
    "TOIMILV":      ("Valve",        "Actuated / control valve",       "Instrument → SAP Valve record; type: CV/FV",    "🔵"),
    "TAKAISKU":     ("Valve",        "Check / non-return valve",       "Instrument → SAP Valve record; type: CV",       "🔵"),
    "VAROV":        ("Valve",        "Safety / relief valve",          "Instrument → SAP Valve record; type: SV",       "🔵"),
    "TOIM":         ("Valve",        "Actuator",                       "Linked to parent valve Equipment record",       "🔵"),
    "SEK2":         ("Equipment",    "Reducer / transition fitting",   "SAP Equipment — fitting",                       "⚙️"),
    # Valmet Equipment
    "MOTOR":        ("Equipment",    "Motor drive unit",               "SAP Equipment Master — motor; tag from MOOPOS", "⚙️"),
    "KOMPR":        ("Equipment",    "Compressor",                     "SAP Equipment Master — compressor",             "⚙️"),
    # Valmet Instruments / Flow
    "NUOLI":        ("Pipeline",     "Flow direction arrow",           "Connectivity: encoded in LIN_FROM/LIN_TO",      "→"),
    "PI0NUOPR":     ("Pipeline",     "Pipeline connector (flow diag)", "Carries PUT-attrs: DN, PN, material, medium",   "→"),
    # KSD
    "REVHUVUD":     ("Title Block",  "Revision header",                "Drawing metadata — revision table",             "📋"),
    "METSOHUVUD":   ("Title Block",  "Metso/Valmet title block",       "Drawing metadata — title, sheet, project",      "📋"),
    "DRWSTAMPMETSO":("Title Block",  "Drawing stamp / approval mark",  "Drawing metadata",                              "📋"),
    "PILH":         ("Pipeline",     "Horizontal pipe continuation",   "Cross-sheet ref stored in BENÄMNING attr",      "→"),
    "PILV":         ("Pipeline",     "Vertical pipe continuation",     "Cross-sheet ref stored in BENÄMNING attr",      "↑"),
    "POSNR":        ("Instrument",   "Position number tag bubble",     "Carries KRETS (loop tag) + POSNR attributes",   "📊"),
    "T":            ("Instrument",   "Instrument bubble",              "Carries instrument type from KRETS tag",        "📊"),
    "SPEC":         ("Equipment",    "Equipment specification tag",    "Links to equipment spec document",              "📄"),
    # GOR
    "LOOPDCS":      ("Instrument",   "DCS control loop bubble",        "Each insert = one instrument loop → SAP tag",   "📊"),
    "COIL":         ("Equipment",    "Coil / heat exchange element",   "SAP Equipment Master — heat exchanger",         "⚙️"),
    # Shared title block / utility
    "CARTIGLIO":    ("Title Block",  "Italian title block (Cartiglio)","Drawing metadata — title, revision, client",    "📋"),
    "REVISIONIRIGA":("Title Block",  "Revision row",                   "Drawing metadata — revision history row",       "📋"),
    "REVISIONITESTA":("Title Block", "Revision header",                "Drawing metadata",                              "📋"),
    "METSOLOGO":    ("Title Block",  "Metso/Valmet logo block",        "Drawing metadata",                              "📋"),
    "STAMPCERTIFIED":("Title Block", "Certified stamp",                "Drawing metadata — approval status",            "📋"),
    "STAMPPRELIMINARY":("Title Block","Preliminary stamp",             "Drawing metadata — draft status",               "📋"),
    "VALMETSTAMPFORAPPROVAL":("Title Block","For-approval stamp",      "Drawing metadata",                              "📋"),
    "INSULATION LEG":("Equipment",  "Insulation detail symbol",        "Visual — insulation coverage marker",           "⚙️"),
    "GENAXEH":      ("CAD Utility",  "Arrow / annotation helper",      "Drawing geometry — no process data",            "—"),
    "AME_NIL":      ("CAD Utility",  "AutoMech null reference",        "Drawing geometry — no process data",            "—"),
    "AME_SOL":      ("CAD Utility",  "AutoMech solid reference",       "Drawing geometry — no process data",            "—"),
    "PS-INIT":      ("CAD Utility",  "KSD drawing initialiser block",  "Drawing geometry — no process data",            "—"),
    "PS-INTXT":     ("CAD Utility",  "KSD text initialiser",           "Drawing geometry — no process data",            "—"),
    "LA-INIT":      ("CAD Utility",  "Layer initialiser block",        "Drawing geometry — no process data",            "—"),
    "QUADRATURAA1":("Title Block",   "A1+ drawing border / frame",     "Drawing geometry — title area border",          "📋"),
}

# Prefix-based matching (checked after exact)
BLOCK_PREFIXES: list[tuple[str, tuple]] = [
    ("P7A",         ("Instrument", "DCS instrument loop bubble",    "PCAD-POS-INFO XDATA → type, area, pos ID, desc", "📊")),
    ("PPI_",        ("Instrument", "Process instrument",            "Instrument loop → SAP tag via PCAD XDATA",       "📊")),
    ("FIMPEC",      ("Valve",      "FIMPEC valve classification",   "PS-21 FIMPEC code → valve type in SAP",          "🔵")),
    ("VENTTIILI",   ("Valve",      "Valve (Finnish: venttiili)",    "SAP Valve record",                               "🔵")),
    ("SQUADRATURA", ("Title Block","Drawing border / frame",        "Drawing geometry — no process data",             "📋")),
    ("INDICEREV",   ("Title Block","Revision index marker",         "Drawing metadata",                               "📋")),
    ("METSOLOGO",   ("Title Block","Metso/Valmet logo",             "Drawing metadata",                               "📋")),
    ("VALMETSTAMP", ("Title Block","Valmet approval stamp",         "Drawing metadata",                               "📋")),
    ("A$C",         ("CAD Utility","Anonymous/embedded block",      "Drawing geometry — no process data",             "—")),
    ("PS_",         ("Instrument", "KSD process instrument symbol", "Carries KSD instrument attributes",              "📊")),
    ("PILH",        ("Pipeline",   "Horizontal pipe continuation",  "Cross-sheet reference in BENÄMNING",             "→")),
    ("PILV",        ("Pipeline",   "Vertical pipe continuation",    "Cross-sheet reference in BENÄMNING",             "↑")),
    ("REVHUVUD",    ("Title Block","Revision header",               "Drawing metadata",                               "📋")),
]

# How each block / prefix was identified — plain-English evidence for the UI column
# Keys match BLOCK_EXACT keys OR BLOCK_PREFIXES first-element (prefix strings)
BLOCK_ID_REASON: dict[str, str] = {
    # Exact — Valmet valves
    "VENTK":
        "Finnish: 'venttiili' = valve (dictionary) · Every insert carries VENIMI (valve name), VEPOSITIO (position tag), VEKEMIKAALI (medium) attrs — read from dwg_per_file_inventory.json · Position tag format matches PS-21 standard PDF RAU4EG1433.04 §3 · No other ecosystem uses this block name",
    "VENT":
        "Finnish: 'venttiili' = valve · Generic valve block; same attribute set as VENTK (VEPOSITIO, VENIMI) · Observed across CHEM/OCC Valmet drawings in inventory",
    "TOIMILV":
        "Finnish: 'toimilaiteventtiili' = actuated valve (toimilaite=actuator, venttiili=valve) · TOIM- root consistently identifies actuated blocks across all Valmet drawings · Observed in dwg_per_file_inventory.json block lists",
    "TAKAISKU":
        "Finnish: 'takaisku' = check/non-return valve · Unique block name — appears only in Valmet CHEM/OCC drawings, never in GOR or KSD · Confirmed by cross-file inspection of dwg_per_file_inventory.json",
    "VAROV":
        "Finnish: 'varoventtiili' = safety/relief valve (varo=caution/guard, venttiili=valve) · Unique Valmet block name; cross-file check confirms 0 occurrences in GOR/KSD drawings",
    "TOIM":
        "Finnish: 'toimilaite' = actuator · Appears alongside parent valve block inserts (e.g. TOIMILV) · Observed in block definition lists in Valmet drawings",
    # Exact — Valmet equipment
    "SEK2":
        "Valmet internal naming: SEK2 = reducer/secondary fitting · Block carries equipment-type attributes (LAIPOS, LAINIMI) · Consistent across CHEM/OCC Valmet drawings; not present in GOR/KSD",
    "MOTOR":
        "English 'MOTOR' — carries MOOPOS (motor position tag format from PS-21 RAU4EG1433 §5: 'MM-SSYYY-M1') and MOOTEHO (rated power kW) attributes · Present across all 35 Valmet DWGs; attribute names confirmed in dwg_per_file_inventory.json",
    "KOMPR":
        "Engineering abbreviation: KOMPR = compressor (Finnish/engineering shorthand) · Block carries equipment-type attrs (LAIPOS, LAIKAPA) · Identified by context in Valmet equipment layer (FIMPEC_EQUIP)",
    "COIL":
        "English 'COIL' = heat-exchange coil · Appears only in GORA*/GORB* drawings (GOR ecosystem) — confirmed by cross-file check in inventory · No Finnish/Swedish naming → Italian origin implied by ecosystem membership",
    "INSULATION LEG":
        "Block name self-describes: insulation detail/legend symbol · No process data attributes; purely visual · Observed in Valmet drawings on P-INSULATION layer",
    "SPEC":
        "KSD block: 'SPEC' = equipment specification tag · Links insert to specification document via BENÄMNING attr · Observed only in parseable KSDM* drawings in inventory",
    # Exact — pipeline
    "NUOLI":
        "Finnish: 'nuoli' = arrow · Flow direction marker on pipe polylines · Confirmed by consistent placement at pipe segment endpoints in Valmet P&IDs; no process data attrs",
    "PI0NUOPR":
        "Block name decoded: 'PI0' = flow diagram prefix (all RAU6401* files use PI0* layer/block naming), 'NUOPR' = connector · Only in RAU6401* flow drawings · Carries PUT-prefix attrs (PUTDN, PUTPN, PUTMATE, PUTAINE) — PUT-prefix documented in Valmet flow diagram convention observed in DWG data",
    "PILH":
        "KSD block: Swedish 'pil' = arrow, 'H' = horisontell (horizontal) · BENÄMNING attr value contains cross-sheet reference text e.g. 'KSDM160104103 sh.03' — format matches KSD standard KSDM160104_010.00 drawing numbering",
    "PILV":
        "KSD block: Swedish 'pil' = arrow, 'V' = vertikal · Same BENÄMNING cross-sheet ref pattern as PILH · Observed in parseable KSD drawings in inventory",
    # Exact — KSD instruments
    "POSNR":
        "KSD standard KSDM160104_010.00 (resources/Naming Standards/Naming_Tissue/) explicitly names POSNR as the position number field · Block carries KRETS (circuit/loop tag) + POSNR attrs · Sample values in DWGs: KRETS='126LC', POSNR='001' — match KSD standard format §4",
    "T":
        "KSD generic instrument bubble · Short block name 'T' appears only in KSDM* drawings — cross-file check in inventory confirms 0 in Valmet/GOR · Carries KSD attribute schema (KRETS, POSNR, BENÄMNING)",
    # Exact — GOR
    "LOOPDCS":
        "GOR CAD block for DCS control loop · Appears in 100% of GORA*/GORB* drawings and 0% of Valmet/KSD drawings — verified by cross-file block list in dwg_per_file_inventory.json · Each insert carries only '02' attr (IDOK internal block marker) · No GOR standard document provided; classified by exclusion + IDOK app ID fingerprint",
    # Exact — title blocks
    "REVHUVUD":
        "Swedish: 'revisionshuvud' = revision header (revision + huvud=head) · Appears only in KSDM* drawings · Carries Swedish revision attrs; consistent with KSD title block structure in KSD standard §2",
    "METSOHUVUD":
        "Metso/Valmet corporate block: 'METSOHUVUD' = Metso header (huvud=head in Swedish) · Observed in KSD and some Valmet drawings — Metso is the parent company of both Valmet and the KSD delivery scope",
    "DRWSTAMPMETSO":
        "Metso drawing stamp block · Drawing metadata only; no process data · Observed in title block area of Valmet drawings (same layer as METSOHUVUD)",
    "CARTIGLIO":
        "Italian: 'cartiglio' = title cartouche (standard Italian technical drawing term) · Present in 100% of GORA*/GORB* drawings and 0% of Valmet/KSD drawings — verified by cross-file block list in dwg_per_file_inventory.json · No GOR standard provided; Italian vocabulary + exclusion criterion = GOR",
    "REVISIONIRIGA":
        "Italian: 'revisioni riga' = revision row (revisioni=revisions, riga=row/line) · GOR revision table row block · Confirmed by co-occurrence with CARTIGLIO in all GOR drawings",
    "REVISIONITESTA":
        "Italian: 'revisioni testa' = revision header (testa=head) · GOR revision table header block · Italian vocabulary + GOR ecosystem membership",
    "METSOLOGO":
        "Metso/Valmet company logo block · Drawing metadata only · Observed in title block area across Valmet and KSD drawings (both Metso-affiliated)",
    "STAMPCERTIFIED":
        "Valmet drawing status stamp — 'CERTIFIED' suffix self-describes · Observed in Valmet drawings alongside STAMPPRELIMINARY and VALMETSTAMPFORAPPROVAL as a family",
    "STAMPPRELIMINARY":
        "Valmet drawing status stamp — 'PRELIMINARY' suffix self-describes · Observed in Valmet drawings at draft stage",
    "VALMETSTAMPFORAPPROVAL":
        "Valmet drawing stamp — 'FOR APPROVAL' suffix self-describes · All three VALMETSTAMP* variants observed in Valmet drawing title block area; confirms Valmet authorship",
    "QUADRATURAA1":
        "Italian: 'squadratura A1' = A1 paper-size drawing border (squadratura=framing/border in Italian technical drawing) · Observed in all GORA*/GORB* drawings · Italian vocabulary + GOR ecosystem",
    # Exact — CAD utility
    "GENAXEH":
        "AutoCAD geometry helper — name pattern (GEN prefix + AXE) matches AutoCAD geometric annotation utilities · No process data attrs; zero attribute tags · Observed as high-count insert in many drawings but carries no instrument/equipment data",
    "AME_NIL":
        "AutoMECH assembly null reference — AME prefix = AutoMECH (Autodesk mechanical CAD module) · Drawing geometry only; confirmed by zero attrs and AME_SOL co-occurrence",
    "AME_SOL":
        "AutoMECH solid reference — same AME prefix family as AME_NIL · Drawing geometry only; no process content",
    "PS-INIT":
        "KSD drawing initialiser — 'PS-INIT' block sets up layer visibility and drawing environment on open · Observed only in KSDM* drawings · No attrs; drawing setup only",
    "PS-INTXT":
        "KSD text initialiser — companion to PS-INIT for text style setup · Observed only in KSDM* drawings · No process data",
    "LA-INIT":
        "Layer initialiser block — sets up layer defaults on drawing open · Observed across multiple ecosystems as a CAD setup block; no process attrs",
    # Prefix — Valmet instruments
    "P7A":
        "Prefix 'P7A*': Valmet internal naming for DCS instrument bubble (7-segment display style) · Instrument type confirmed by PCAD-POS-INFO XDATA field [1] = type code (LT/LC/FI/PI/TI/…) — XDATA schema reverse-engineered from raw DWG data in dwg_per_file_inventory.json · Type codes match instrument letter table in PS-21 standard RAU4EG1433.04 §3 · Confirmed across all 44 Valmet CHEM/OCC DWGs",
    "PPI_":
        "Prefix 'PPI_*': Valmet Process P&I instrument bubble (PPI = Process P&I) · Instrument type confirmed by PCAD-POS-INFO XDATA on every insert — field [1] = type code (FI/LI/TI/PI/…), field [2] = area code, field [0] = position ID · XDATA schema reverse-engineered from dwg_per_file_inventory.json; type codes cross-checked against PS-21 PDF RAU4EG1433 §3 · 100–200 instances per drawing; confirmed in 40+ Valmet DWGs",
    # Prefix — Valmet valves
    "FIMPEC":
        "Prefix 'FIMPEC*': Valmet PS-21 FIMPEC valve classification code family · 'FIMPEC' is a Valmet standard valve coding system — codes encode valve type, material, end connections · Observed as block name prefix across Valmet CHEM/OCC drawings; each variant = a specific valve type combination",
    "VENTTIILI":
        "Prefix 'VENTTIILI*': Finnish 'venttiili' = valve (same root as VENTK) · Variant valve block family used in specific Valmet drawings · Carries standard valve attrs (VEPOSITIO, VENIMI) — confirmed by attr inspection in inventory",
    # Prefix — GOR title blocks
    "SQUADRATURA":
        "Prefix 'SQUADRATURA*': Italian 'squadratura' = drawing frame/border · GOR block family for A1+ paper border variants · All GORA*/GORB* drawings use this family; confirmed by cross-file block list in inventory · Italian vocabulary = GOR",
    "INDICEREV":
        "Prefix 'INDICEREV*': Italian 'indice revisioni' = revision index · GOR revision tracking block family · Multiple variants for different revision row positions (INDICEREV_180° etc.) · Co-occurs with CARTIGLIO in all GOR drawings",
    # Prefix — Valmet / shared
    "VALMETSTAMP":
        "Prefix 'VALMETSTAMP*': Valmet drawing stamp variant family (for-approval, preliminary, certified) · Self-describing names · Observed only in Valmet drawing title block areas; confirms Valmet authorship",
    # Prefix — CAD utility
    "A$C":
        "Prefix 'A$C*': AutoCAD anonymous/embedded block naming convention — AutoCAD auto-generates 'A$C' names for geometry extracted from external references or wblocked sections · Confirmed by AutoCAD documentation; no process meaning in any ecosystem",
    # Prefix — KSD
    "PS_":
        "Prefix 'PS_*': KSD process symbol naming (PS = Process Symbol) · Carries KRETS (loop circuit tag) + POSNR (position number) attrs — both documented in KSD standard KSDM160104_010.00 §4 (resources/Naming Standards/Naming_Tissue/) · Confirmed in 10 parseable KSDM* drawings; sample KRETS='126LC', POSNR='001'",
}

# ── Attribute tag → mapping table ─────────────────────────────────────────────
# (SAP/process field, description, icon)
ATTR_TAG_MAP: dict[str, tuple] = {
    # Valmet — valve / equipment
    "LINJA":        ("Pipeline ID",     "Line/pipe identifier — maps to SAP FLOC line code",          "📐"),
    "VENIMI":       ("Valve Name",      "Descriptive name of valve (Finnish)",                         "🔵"),
    "VEPOSITIO":    ("Equipment Tag",   "Position tag → SAP Equipment number / FLOC",                 "🏷️"),
    "VEKOKO":       ("Size (DN)",       "Valve / pipe nominal diameter",                               "📏"),
    "VETYYPPI":     ("Type Code",       "Valve or equipment type code (Finnish abbrev.)",              "🔵"),
    "VEKEMIKAALI":  ("Medium",          "Process medium / chemical (Finnish)",                         "💧"),
    "VEVALMISTAJA": ("Manufacturer",    "Equipment manufacturer → SAP Manufacturer field",             "🏭"),
    "IVENIMI":      ("Instrument Name", "Instrument descriptive name",                                 "📊"),
    "LAINIMI":      ("Equip. Name",     "Equipment descriptive name → SAP description",               "⚙️"),
    "LAIPOS":       ("Equip. Tag",      "Equipment position tag → SAP Equipment number",              "🏷️"),
    "LAIKAPA":      ("Capacity",        "Equipment rated capacity",                                    "📊"),
    "LAIMTEH":      ("Rated Power",     "Equipment rated power (kW)",                                  "⚙️"),
    "LAIKIER":      ("Speed (RPM)",     "Shaft rotation speed",                                        "⚙️"),
    "LAIJANN":      ("Shaft Tension",   "Shaft / belt tension",                                        "⚙️"),
    "MOOPOS":       ("Motor Tag",       "Motor position tag → SAP Equipment (linked to parent)",       "⚙️"),
    "MOOTEHO":      ("Motor Power",     "Motor rated power (kW) → SAP characteristic",                "⚙️"),
    "KORKEUS":      ("Elevation",       "Installation height / elevation",                             "📏"),
    "VEPAINE":      ("Design Press.",   "Design pressure (bar) → SAP characteristic",                  "📊"),
    "VELAMPO":      ("Design Temp.",    "Design temperature (°C) → SAP characteristic",               "📊"),
    "SRVAS":        ("Status – Author", "Drawing status responsible person",                           "📋"),
    "SROIK":        ("Status – Check",  "Drawing status corrected / checked by",                      "📋"),
    "KAAVIO":       ("Cross-sheet Ref", "References another drawing by ID (inter-drawing link)",       "🔗"),
    # Valmet — flow diagram PUT-prefix
    "PUTAINE":      ("Medium (flow)",   "Pipe medium / fluid code → SAP pipe spec",                   "💧"),
    "PUTDN":        ("Pipe DN",         "Nominal pipe diameter → SAP pipe characteristic",             "📏"),
    "PUTPN":        ("Pipe PN",         "Nominal pressure rating PN → SAP pipe characteristic",       "📊"),
    "PUTMATE":      ("Pipe Material",   "Pipe material code → SAP material characteristic",           "📐"),
    "PUTPAIN":      ("Oper. Pressure",  "Operating pressure → SAP characteristic",                    "📊"),
    "PUTLAMM":      ("Oper. Temp.",     "Operating temperature → SAP characteristic",                 "📊"),
    "PUTVIRT":      ("Flow Rate",       "Process flow rate → SAP characteristic",                     "📊"),
    "PUTKAP":       ("Capacity",        "Pipe / section capacity",                                     "📊"),
    "PUTTIH":       ("Density",         "Fluid density",                                               "📊"),
    "PUTOSAS":      ("Sub-process",     "Sub-process / area code for pipeline",                        "📐"),
    "PUTLINJ":      ("Line ID (flow)",  "Pipeline line ID in flow diagram",                            "📐"),
    "PUTAILY":      ("Flow Direction",  "Flow direction code",                                         "→"),
    # KSD
    "KRETS":        ("Loop Tag",        "Circuit / instrument loop tag e.g. 126LC (area=126, type=LC)","📊"),
    "POSNR":        ("Position No.",    "Instrument/equipment serial within loop → SAP tag suffix",    "🏷️"),
    "BENÄMNING":    ("Description",     "Equip/instrument name OR cross-sheet continuation ref",       "📝"),
    "PIPEID":       ("Pipeline ID",     "Pipe line identifier → SAP FLOC pipeline segment",           "📐"),
    "PIPEDATA":     ("Pipe Spec",       "Pipe specification string (DN, PN, material)",               "📐"),
    "TYPE":         ("Type Code",       "Equipment / instrument type code",                            "🔵"),
    "SHEET":        ("Sheet No.",       "Drawing sheet number",                                        "📋"),
    # GOR
    "02":           ("GOR Marker",      "IDOK internal block marker — not a process data attribute",   "ℹ️"),
}

GOR_LAYER_MAP = {
    "1-TAG AND INSTRUMENTS GOR": ("Instrument Tags",  "TEXT entities: {area}{type}{seq} e.g. 162TI2, 162TT1",    "📊"),
    "1-EQUIPMENT GOR":           ("Equipment Tags",   "TEXT entities: equipment position/description",            "⚙️"),
    "1-VALVE TEXT GOR":          ("Valve Tags",       "TEXT entities: valve position / handle valve tags",        "🔵"),
    "1-AIR GOR":                 ("Air Lines",        "LWPOLYLINE with linetype COMPRESS_AIR_GOR",               "💨"),
    "1-WATER GOR":               ("Water Lines",      "LWPOLYLINE — process water piping",                       "💧"),
    "1-GAS GOR":                 ("Gas Lines",        "LWPOLYLINE with linetype GAS_LINE",                       "🔥"),
    "1-PNEUMATIC GOR":           ("Pneumatic Lines",  "LWPOLYLINE — pneumatic instrument air",                   "💨"),
    "1-BACKPRESSURE GOR":        ("Backpressure",     "LWPOLYLINE with linetype BACK_PRESSURE_GOR",              "📊"),
    "1-FLOW TEXT GOR":           ("Flow Text",        "TEXT entities — flow annotations",                        "📝"),
    "1- DELIVERY LIMITS":        ("Delivery Limit",   "Drawing boundary — GOR vs customer scope",                "📐"),
    "2-AIR CUSTOMER":            ("Customer Air",     "LWPOLYLINE — customer-supplied air lines",                "💨"),
    "2-WATER CUSTOMER":          ("Customer Water",   "LWPOLYLINE — customer-supplied water lines",              "💧"),
    "2-WATER CUSTOMER (DOT)":    ("Customer Water",   "LWPOLYLINE — customer water (dotted = future/design)",    "💧"),
    "2-GAS CUSTOMER":            ("Customer Gas",     "LWPOLYLINE — customer-supplied gas lines",                "🔥"),
    "2-PNEUMATIC CUSTOMER":      ("Customer Pneu.",   "LWPOLYLINE — customer pneumatic lines",                   "💨"),
    "2-EQUIPMENT CUSTOMER":      ("Customer Equip.",  "TEXT/INSERT — customer-supplied equipment",               "⚙️"),
    "2-BACKPRESSURE CUSTOMER":   ("Cust. Backpr.",    "LWPOLYLINE — customer backpressure lines",                "📊"),
    "2-HYDRAULIC CUSTOMER":      ("Customer Hyd.",    "LWPOLYLINE — customer hydraulic lines",                   "📊"),
    "CARTIGLIO":                 ("Title Block",      "Title block layer — drawing metadata",                    "📋"),
    "LEGEND":                    ("Legend",           "Drawing symbol legend",                                   "📋"),
    "VIEWPORT":                  ("Viewport",         "Paper-space viewport",                                    "—"),
}


# ── Lookup helpers ────────────────────────────────────────────────────────────
def lookup_block(bname: str) -> tuple | None:
    """Returns (category, role, sap_mapping, icon, how_identified) or None."""
    key = bname.upper().replace(" ","").replace("-","").replace("_","")
    for k, v in BLOCK_EXACT.items():
        if k.upper().replace(" ","").replace("-","").replace("_","") == key:
            reason = BLOCK_ID_REASON.get(k, f"Exact block name match — '{k}' is a known CAD library block")
            return (*v, reason)
    for prefix, v in BLOCK_PREFIXES:
        if bname.upper().startswith(prefix.upper()):
            reason = BLOCK_ID_REASON.get(prefix, f"Prefix match — blocks starting '{prefix}' identified by naming convention")
            return (*v, reason)
    return None


def lookup_attr(tag: str) -> tuple | None:
    return ATTR_TAG_MAP.get(tag.upper(), ATTR_TAG_MAP.get(tag))


# ── Build per-DWG block + tag mapping records ─────────────────────────────────
def build_block_mappings(v: dict, eco: str) -> list[dict]:
    rows = []
    for b in v.get("top_insert_blocks", [])[:25]:
        name  = b["name"]
        count = b["count"]
        m = lookup_block(name)
        if not m:
            continue
        category, role, sap_mapping, icon, how_ident = m
        rows.append({"name": name, "count": count,
                     "category": category, "role": role,
                     "sap_mapping": sap_mapping, "icon": icon,
                     "how_ident": how_ident})
    return rows


def build_attr_mappings(v: dict) -> list[dict]:
    rows = []
    for tag, info in list(v.get("attribute_tags", {}).items())[:20]:
        m = lookup_attr(tag)
        if not m:
            # still include it, just mark as unmapped
            rows.append({"tag": tag, "count": info["count"],
                         "sample": (info.get("sample") or "")[:50],
                         "field": "Unknown", "description": "—", "icon": "❓"})
            continue
        field, description, icon = m
        rows.append({"tag": tag, "count": info["count"],
                     "sample": (info.get("sample") or "")[:50],
                     "field": field, "description": description, "icon": icon})
    return rows


def build_gor_layer_mappings(v: dict) -> list[dict]:
    """For GOR DWGs: layer name → semantic type mapping, with text entity count."""
    layer_names = set(v.get("layers", []))
    # count text samples per layer
    layer_text_count: dict[str,int] = {}
    for ts in v.get("text_samples", []):
        l = ts["layer"]
        layer_text_count[l] = layer_text_count.get(l, 0) + 1

    rows = []
    for lname in sorted(layer_names):
        m = GOR_LAYER_MAP.get(lname)
        if not m:
            continue
        semantic, description, icon = m
        rows.append({"layer": lname, "semantic": semantic,
                     "description": description, "icon": icon})
    return rows


# ── Evidence builder (unchanged from before) ─────────────────────────────────
def build_evidence(fname: str, v: dict, csv_row: dict) -> list[dict]:
    eco = classify(fname)
    ev: list[dict] = []
    ag      = v.get("appid_groups", {})
    layers  = v.get("layers", [])
    blocks  = [b["name"] for b in v.get("blocks_defined", [])]
    attrs   = list(v.get("attribute_tags", {}).keys())
    lttypes = [lt["name"] for lt in v.get("linetypes", [])]
    tb      = v.get("title_block", {})
    conn    = v.get("connectivity", {})
    is_failed = "error" in v

    if eco == "valmet":
        is_flow = "RAU6401" in fname
        if ag.get("has_pcad"):
            ev.append({"icon":"✅","text":
                f"PCAD_ app IDs present ({ag.get('pcad_count',0)} registered) — "
                "Valmet proprietary Plant CAD: PCAD-POS-INFO stores instrument type, area, position ID; "
                "PI-LNKREF cross-links bubble↔tag; LIN_FROM/LIN_TO encodes pipe connectivity"})
        if ag.get("genius_count",0) > 0:
            ev.append({"icon":"✅","text":
                f"GENIUS_ app IDs present ({ag.get('genius_count',0)}) — "
                "Genius Plant Design AutoCAD add-on, used across all Valmet deliveries"})
        p_found  = [l for l in layers if any(l.startswith(p) for p in ["P-","FIMPEC_"])]
        pi_found = [l for l in layers if any(l.startswith(p) for p in ["PI0","PI1","PI3","PI4","PI5"])]
        if is_flow and pi_found:
            ev.append({"icon":"✅","text":
                f"PI-prefix layer scheme (flow diagram sub-type, older Valmet convention): "
                f"{', '.join(pi_found[:6])}"})
            ev.append({"icon":"ℹ️","text":
                "RAU6401 filename = Valmet flow diagram (not P&ID) — uses PI0NUOPR connector block "
                "with PUT-prefix pipe attributes (DN, PN, material, medium, temp, flow rate) "
                "instead of LIN_FROM/LIN_TO connectivity"})
        elif p_found:
            ev.append({"icon":"✅","text":
                f"P-prefix layer scheme (PS-21 standard naming): {', '.join(p_found[:6])}"
                + (f" … +{len(p_found)-6} more" if len(p_found)>6 else "")})
        finn_b = [b for b in blocks if any(b.upper().startswith(f.upper()) for f in FINN_BLOCKS)]
        if finn_b:
            meanings = {"VENTK":"ball valve","TOIMILV":"actuated valve","TAKAISKU":"check valve",
                        "VAROV":"safety valve","MOTOR":"motor drive","NUOLI":"direction arrow",
                        "KOMPR":"compressor","SEK2":"reducer"}
            with_mean = [f"{b} ({meanings.get(b.upper()[:5],'')})" if b.upper()[:5] in {k.upper():k for k in meanings} else b
                         for b in finn_b[:5]]
            ev.append({"icon":"✅","text":
                f"Finnish block library: {', '.join(finn_b[:5])}"
                + (f" … +{len(finn_b)-5} more" if len(finn_b)>5 else "")})
        finn_a = {t:FINN_ATTR_TAGS[t] for t in attrs if t in FINN_ATTR_TAGS}
        if finn_a:
            ev.append({"icon":"✅","text":
                f"Finnish attribute tags: {', '.join(f'{k} ({v2})' for k,v2 in list(finn_a.items())[:6])}"
                + (f" … +{len(finn_a)-6} more" if len(finn_a)>6 else "")})
        tb_parts = [f"{k}: {tb[k]}" for k in ["PROJECT1","DRAWINGID","TITLE1","SHEET"] if tb.get(k)]
        if tb_parts:
            ev.append({"icon":"✅","text": "Structured title block: " + " | ".join(tb_parts)})
        if "LIN_FROM" in conn.get("rel_fields",""):
            ev.append({"icon":"✅","text":
                f"LIN_FROM/LIN_TO connectivity graph ({conn.get('rel_record_count','?')} records) — "
                "full P&ID flow graph is machine-reconstructable"})
        elif not is_flow:
            ev.append({"icon":"⚠️","text":
                "LIN_FROM/LIN_TO connectivity not detected — "
                "may use older short-code layer scheme or contain only static equipment"})
        short = [l for l in layers if l in ["I","T","R","RA","HY","LA","PKV","VEP"]]
        if short:
            ev.append({"icon":"ℹ️","text":
                f"Short-code layer scheme (older Valmet variant): {', '.join(short)} — "
                "predates P-prefix naming but same PS-21 standard"})

    elif eco == "gor":
        if ag.get("has_idok"):
            ev.append({"icon":"✅","text":
                f"IDOK_ app IDs present ({ag.get('idok_count',0)}) — "
                "Italian process P&ID automation tool, exclusive to GOR in this dataset "
                "(IDOK_INSTRUMENT, IDOK_LAYOUT, IDOK_PROCESS_1/2, IDOK_SKALA)"})
        if not ag.get("has_pcad"):
            ev.append({"icon":"✅","text":
                "No PCAD_ app IDs — confirms NOT Valmet PS-21 (all 35 Valmet drawings carry PCAD_)"})
        if ag.get("genius_count",0) > 0:
            ev.append({"icon":"✅","text":
                f"GENIUS_ app IDs present ({ag.get('genius_count',0)}) — Genius Plant Design "
                "shared with Valmet but here without PCAD_, confirming GOR ecosystem"})
        ev.append({"icon":"✅","text":
            "Username 'gorceschma' — GOR + CE (Central Europe): directly identifies GOR S.r.l."})
        ita_l = [l for l in layers if any(il.lower() in l.lower() for il in ITA_LAYERS)
                 or l.startswith("1-") or l.startswith("2-")]
        if ita_l:
            ev.append({"icon":"✅","text":
                f"Italian/GOR layer naming: {', '.join(ita_l[:6])} — "
                "CARTIGLIO (title block), 1-prefix=GOR supply, 2-prefix=customer supply"})
        ita_b = [b for b in blocks if any(ib.lower() in b.lower() for ib in ITA_BLOCKS)]
        if ita_b:
            ev.append({"icon":"✅","text":
                f"Italian block names: {', '.join(ita_b[:5])} — "
                "Cartiglio (Italian title block), RevisioniTesta, SquadraturaA1++"})
        gor_lt = [lt for lt in lttypes if lt in GOR_LINES]
        if gor_lt:
            patterns = {"COMPRESS_AIR_GOR":"----/\\---- (GOR air)",
                        "BACK_PRESSURE_GOR":"----X---- (backpressure)",
                        "GAS_LINE":"----GAS---- (gas piping)",
                        "COMPRESS_AIR_OTHERS":"..../\\.... (customer air)",
                        "BACK_PRESSURE_OTHERS":"....X.... (customer backpressure)"}
            ev.append({"icon":"✅","text":
                "GOR-specific linetypes encode medium: " +
                "; ".join(patterns.get(lt,lt) for lt in gor_lt)})
        n_attrs = len(attrs)
        if n_attrs <= 2:
            ev.append({"icon":"⚠️","text":
                f"Only {n_attrs} block attribute tag(s) — all engineering data is in plain TEXT entities "
                "on semantic layers; tag format: {{area}}{{type}}{{seq}} e.g. 162TI2, 162TT1"})
        ev.append({"icon":"ℹ️","text":
            "AC1024 (AutoCAD 2010) — 2 versions older than all other DWGs. "
            "No semantic connectivity: geometric tracing required."})

    elif eco == "ksd":
        ev.append({"icon":"✅","text":
            "Filename prefix 'KSDM160104' matches standard doc 'KSDM160104_010.00 Process Numbering System' — "
            "format: {mill}{area}{function}-{serial} e.g. 126A-001"})
        last_saved = csv_row.get("last_saved_by","")
        if last_saved:
            ev.append({"icon":"✅","text":
                f"Username '{last_saved}' — KSD prefix identifies KSD/Andritz as author"})
        if is_failed:
            ev.append({"icon":"❌","text":
                "Parse failed (DXFStructureError: missing ENDSEC tag) — "
                "evidence below derived from CSV metadata and filename only"})
            ev.append({"icon":"✅","text":
                "CSV: GENIUS_ app IDs registered, plant_appid_present=FALSE, no PCAD_ — "
                "same fingerprint as other KSD drawings in Code 12"})
        else:
            if ag.get("has_idok"):
                ev.append({"icon":"⚠️","text":
                    f"IDOK_ app IDs ({ag.get('idok_count',0)}) detected — KSD drawings share some IDOK_ "
                    "registrations; ecosystem confirmed KSD by filename + Swedish vocabulary"})
            elif not ag.get("has_pcad") and ag.get("genius_count",0) > 0:
                ev.append({"icon":"✅","text":
                    f"GENIUS_ only ({ag.get('genius_count',0)}), no PCAD_, no IDOK_ — "
                    "key fingerprint distinguishing KSD from Valmet (PCAD_) and GOR (IDOK_)"})
            swe_b = [b for b in blocks if any(sb.lower() in b.lower() for sb in SWE_BLOCKS)]
            if swe_b:
                ev.append({"icon":"✅","text":
                    f"Swedish block names: {', '.join(swe_b[:5])} — "
                    "REVHUVUD (revision header), METSOHUVUD (Metso title block), "
                    "PILH/PILV (pipe continuation with cross-sheet BENÄMNING refs)"})
            swe_a = {t:SWE_ATTRS[t] for t in attrs if t in SWE_ATTRS}
            if swe_a:
                ev.append({"icon":"✅","text":
                    f"Swedish attribute tags: {', '.join(f'{k} ({v2})' for k,v2 in list(swe_a.items())[:5])}"})
            swe_l = [l for l in layers if any(sl in l for sl in SWE_LAYERS)]
            if swe_l:
                ev.append({"icon":"✅","text":
                    f"Swedish/KSD layer naming: {', '.join(swe_l[:6])} — "
                    "PS (process), BLANKETT (form), BLTEXT (form text)"})
            if not conn.get("rel_fields"):
                ev.append({"icon":"ℹ️","text":
                    "No LIN_FROM/LIN_TO — connectivity via geometric tracing or BENÄMNING cross-refs"})
    return ev


def classify(fname: str) -> str:
    if "GORA" in fname or "GORB" in fname: return "gor"
    if "KSDM" in fname: return "ksd"
    return "valmet"


def fmt_entity_counts(ec: dict) -> str:
    if not ec: return "—"
    return ", ".join(f"{t}×{c}" for t,c in sorted(ec.items(), key=lambda x:-x[1])[:6])


def build_records() -> list[dict]:
    csv_by = {r["filename"]: r for r in ROWS}
    records, n = [], 0
    for folder in ["CHEM_PID","OCC_PID","PM03_PID","TM01_PID"]:
        for key in sorted(k for k in INV if k.startswith(folder + "/")):
            n += 1
            v    = INV[key]
            meta = v.get("_meta", {})
            fname    = meta.get("filename", key.split("/")[-1])
            csv_row  = csv_by.get(fname, {})
            eco      = classify(fname)
            is_failed= "error" in v

            if eco == "valmet":
                std = "Valmet PS-21 — Flow Diagram Sub-Type" if "RAU6401" in fname else "Valmet PS-21 (SML Standard 21)"
            elif eco == "gor":
                std = "GOR S.r.l. Company Standard"
            else:
                std = "KSD Process Numbering Standard (KSDM160104)"

            conn = v.get("connectivity", {})
            if is_failed:
                conn_badge, conn_text = "parse_failed", "Parse failed — no data"
            elif "LIN_FROM" in conn.get("rel_fields",""):
                conn_badge = "direct"
                conn_text  = f"LIN_FROM/LIN_TO ({conn.get('rel_record_count','?')} records)"
            elif "XData present" in conn.get("csv_assessment",""):
                conn_badge, conn_text = "xdata", "XDATA present, no named endpoints"
            else:
                conn_badge, conn_text = "none", "No semantic connectivity"

            tb    = v.get("title_block", {})
            title = tb.get("TITLE1") or tb.get("TITLE2") or csv_row.get("title","") or fname.replace(".dwg","")
            attr_tags = v.get("attribute_tags", {})

            records.append({
                "n": n, "key": key, "fname": fname, "folder": folder,
                "eco": eco, "standard": std,
                "is_failed": is_failed, "error": v.get("error",""),
                "title": title,
                "last_saved": meta.get("last_saved_by",""),
                "dwg_version": meta.get("dwg_version",""),
                "objects":   meta.get("object_count","—"),
                "entities":  sum(v.get("entity_type_counts",{}).values()) if not is_failed
                             else meta.get("entity_count","—"),
                "layers":    len(v.get("layers",[])),
                "blocks":    len(v.get("blocks_defined",[])),
                "attr_count": len(attr_tags),
                "entity_summary": fmt_entity_counts(v.get("entity_type_counts",{})),
                "conn_badge": conn_badge, "conn_text": conn_text,
                "top_attrs": [{"tag":t,"count":i["count"],"sample":(i.get("sample") or "")[:45]}
                              for t,i in list(attr_tags.items())[:8]],
                "text_samples": [{"layer":ts["layer"],
                                  "text":ts["text"].replace("\n"," ").strip()[:80]}
                                 for ts in v.get("text_samples",[])[:5]],
                "evidence": build_evidence(fname, v, csv_row),
                # NEW: mapping sections
                "block_mappings": build_block_mappings(v, eco),
                "attr_mappings":  build_attr_mappings(v),
                "gor_layer_mappings": build_gor_layer_mappings(v) if eco == "gor" else [],
            })
    return records


records = build_records()
js_data = json.dumps(records, ensure_ascii=False)
print(f"Built {len(records)} records, JSON size: {len(js_data)//1024} KB")

# ── Read and slice assessment tab content ─────────────────────────────────────
def _extract_panel(html: str, tab_id: str) -> str:
    start = html.find(f'<div id="tab-{tab_id}"')
    if start == -1:
        return ''
    sep = html.find('<!-- ═', start + 100)
    end_main = html.find('</div><!-- /.main', start)
    candidates = [x for x in [sep, end_main] if x > 0]
    end = min(candidates) if candidates else len(html)
    content = html[start:end].rstrip()
    return content.replace(' class="tab-panel active"', ' class="tab-panel"')

_ahtml = (BASE / "docs/DWG_SAP_RD_ASSESSMENT.html").read_text(encoding="utf-8")
PANEL_EXEC         = _extract_panel(_ahtml, 'exec')
PANEL_INVENTORY    = _extract_panel(_ahtml, 'inventory')
PANEL_STANDARDS    = _extract_panel(_ahtml, 'standards')
PANEL_CAPABILITIES = _extract_panel(_ahtml, 'capabilities')
PANEL_ARCHITECTURE = _extract_panel(_ahtml, 'architecture')
PANEL_QUESTIONS    = _extract_panel(_ahtml, 'questions')
PANEL_VOCAB        = _extract_panel(_ahtml, 'vocab')
# Assessment CSS (section/table/risk styles used by the embedded panels)
_css_block = _ahtml[_ahtml.find('<style>') + 7 : _ahtml.find('</style>')]

# ─────────────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DWG → SAP R&D Discovery Assessment — Shotton Mill Ltd</title>
<meta name="description" content="R&D Discovery Assessment for DWG to SAP conversion at Shotton Mill Ltd. 84 DWGs across 3 CAD ecosystems (Valmet PS-21, GOR Italian, KSD Swedish).">
<meta name="author" content="Ensemble Flux">
<style>
:root{
  --bg:#0d0f18;--surface:#151827;--surface2:#1d2035;--border:#252840;
  --accent:#7b96ff;--green:#34d399;--yellow:#fbbf24;--orange:#f97316;
  --red:#f87171;--blue:#60a5fa;--purple:#a78bfa;--teal:#2dd4bf;
  --text:#e2e8f0;--muted:#8897b3;--code-bg:#0d0f18;--r:8px;
  --doc-max:1280px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}

/* ── Document Header ── */
.doc-header{background:linear-gradient(180deg,#0d0f18 0%,#131626 100%);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:200}
.doc-header-top{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;padding:20px 40px 16px}
.doc-meta-line{font-size:10px;font-weight:600;letter-spacing:.9px;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.doc-title{font-size:22px;font-weight:800;color:#fff;letter-spacing:-.4px;line-height:1.2}
.doc-title span{color:var(--accent)}
.doc-chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.doc-chip{display:inline-flex;align-items:center;gap:5px;background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:3px 11px;font-size:11px;color:var(--muted);white-space:nowrap}
.doc-chip .dot{width:6px;height:6px;border-radius:50%;background:var(--green);flex-shrink:0}
.doc-right{display:flex;flex-direction:column;align-items:flex-end;gap:8px;flex-shrink:0}
.doc-status{background:rgba(123,150,255,.12);border:1px solid rgba(123,150,255,.25);color:var(--accent);border-radius:6px;padding:5px 14px;font-size:10px;font-weight:700;letter-spacing:.7px;text-transform:uppercase}
.doc-actions{display:flex;gap:6px}
.doc-btn{background:var(--surface2);border:1px solid var(--border);color:var(--muted);border-radius:6px;padding:5px 12px;font-size:11px;font-weight:500;cursor:pointer;font-family:inherit;transition:all .15s;white-space:nowrap}
.doc-btn:hover{border-color:var(--accent);color:var(--accent)}
.doc-btn.primary{background:rgba(123,150,255,.1);border-color:rgba(123,150,255,.3);color:var(--accent)}
.doc-btn.primary:hover{background:rgba(123,150,255,.2)}

/* ── Tab Nav ── */
.tab-nav{display:flex;gap:0;overflow-x:auto;scrollbar-width:none;padding:0 40px;border-top:1px solid var(--border)}
.tab-nav::-webkit-scrollbar{display:none}
.tab-btn{background:none;border:none;border-bottom:2px solid transparent;padding:9px 16px;font-size:12px;font-weight:500;color:var(--muted);cursor:pointer;white-space:nowrap;transition:color .15s,border-color .15s;font-family:inherit;letter-spacing:.1px}
.tab-btn:hover{color:var(--text)}
.tab-btn.active{color:#fff;border-bottom-color:var(--accent);font-weight:600}
.tab-nav-sep{width:1px;background:var(--border);margin:8px 0;flex-shrink:0}

/* ── Legend / Guide ── */
.guide{background:var(--surface);border-bottom:2px solid var(--border)}
.guide-hdr{display:flex;align-items:center;gap:10px;padding:12px 32px;cursor:pointer;user-select:none;border-bottom:1px solid transparent;transition:border-color .15s}
.guide-hdr:hover{background:rgba(255,255,255,.02)}
.guide-hdr.open{border-bottom-color:var(--border)}
.guide-hdr-left{display:flex;align-items:center;gap:10px;flex:1}
.guide-hdr h2{font-size:13px;font-weight:700;color:var(--text)}
.guide-tag{font-size:10px;background:rgba(108,140,255,.12);border:1px solid rgba(108,140,255,.3);color:var(--accent);border-radius:10px;padding:2px 8px;font-weight:600}
.guide-hint{font-size:11px;color:var(--muted)}
.guide-chev{color:var(--muted);font-size:11px;transition:transform .2s}
.guide-chev.open{transform:rotate(180deg)}
.guide-body{display:none;padding:20px 32px 24px;gap:20px}
.guide-body.open{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}

.gb{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:16px}
.gb-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}
.gb-rows{display:flex;flex-direction:column;gap:8px}
.gb-row{display:flex;gap:10px;align-items:flex-start}
.gb-term{font-size:12px;font-weight:700;color:var(--text);min-width:80px;flex-shrink:0;line-height:1.4}
.gb-def{font-size:12px;color:var(--muted);line-height:1.5}
.gb-def strong{color:var(--text)}
.gb-def code{font-size:10px;background:var(--code-bg);border:1px solid var(--border);border-radius:3px;padding:0 4px;color:#a8b9d0;font-family:'SF Mono',Consolas,monospace}

/* Ecosystem fingerprint grid */
.eco-fp{display:flex;flex-direction:column;gap:6px}
.eco-fp-row{display:flex;gap:0;border:1px solid var(--border);border-radius:6px;overflow:hidden;font-size:11px}
.eco-fp-signal{background:var(--code-bg);padding:6px 10px;color:var(--muted);font-weight:600;min-width:90px;flex-shrink:0;border-right:1px solid var(--border)}
.eco-fp-vals{display:flex;gap:1px;flex:1}
.eco-fp-val{padding:6px 8px;flex:1;font-size:10px;text-align:center;border-right:1px solid var(--border)}
.eco-fp-val:last-child{border-right:none}
.eco-fp-val.v{background:rgba(108,140,255,.08);color:var(--accent)}
.eco-fp-val.g{background:rgba(249,115,22,.08);color:var(--orange)}
.eco-fp-val.k{background:rgba(52,211,153,.08);color:var(--green)}

/* Category legend */
.cat-legend{display:flex;flex-direction:column;gap:6px}
.cl-row{display:flex;align-items:flex-start;gap:10px;padding:6px 8px;background:var(--code-bg);border:1px solid var(--border);border-radius:5px}
.cl-badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:3px;white-space:nowrap;flex-shrink:0}
.cl-badge.Valve{background:rgba(96,165,250,.12);color:var(--blue);border:1px solid rgba(96,165,250,.25)}
.cl-badge.Equipment{background:rgba(52,211,153,.1);color:var(--green);border:1px solid rgba(52,211,153,.25)}
.cl-badge.Instrument{background:rgba(167,139,250,.1);color:var(--purple);border:1px solid rgba(167,139,250,.25)}
.cl-badge.Pipeline{background:rgba(45,212,191,.1);color:var(--teal);border:1px solid rgba(45,212,191,.25)}
.cl-badge.TitleBlock{background:rgba(148,163,184,.1);color:var(--muted);border:1px solid rgba(148,163,184,.25)}
.cl-badge.Utility{background:rgba(46,50,71,.6);color:#475569;border:1px solid var(--border)}
.cl-text{font-size:11px;color:var(--muted);line-height:1.4}
.cl-text strong{color:var(--text)}

/* Connectivity legend */
.conn-legend{display:flex;flex-direction:column;gap:6px}
.conn-item{display:flex;gap:10px;align-items:flex-start;padding:8px 10px;background:var(--code-bg);border:1px solid var(--border);border-radius:5px}
.conn-dot-lg{width:11px;height:11px;border-radius:50%;flex-shrink:0;margin-top:3px}
.conn-dot-lg.direct{background:var(--green);box-shadow:0 0 6px rgba(52,211,153,.4)}
.conn-dot-lg.xdata{background:var(--yellow);box-shadow:0 0 6px rgba(251,191,36,.4)}
.conn-dot-lg.none{background:var(--orange);box-shadow:0 0 6px rgba(249,115,22,.4)}
.conn-dot-lg.failed{background:var(--red);box-shadow:0 0 6px rgba(248,113,113,.4)}
.conn-item-text{font-size:11px;color:var(--muted);line-height:1.5}
.conn-item-text strong{color:var(--text);display:block;margin-bottom:1px}

/* ── Controls ── */
.controls{display:flex;gap:10px;flex-wrap:wrap;padding:12px 32px;background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:71px;z-index:100;align-items:center}
.search-wrap{position:relative;flex:1;min-width:220px;max-width:320px}
.search-wrap input{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:7px 12px 7px 32px;color:var(--text);font-size:13px;outline:none}
.search-wrap input:focus{border-color:var(--accent)}
.search-wrap .ico{position:absolute;left:9px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}
.fg{display:flex;gap:5px;flex-wrap:wrap;align-items:center}
.fl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
.pill{background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:3px 11px;font-size:11px;color:var(--muted);cursor:pointer;transition:all .15s;white-space:nowrap;user-select:none}
.pill:hover{border-color:var(--accent);color:var(--text)}
.pill.active{background:rgba(108,140,255,.15);border-color:var(--accent);color:var(--accent);font-weight:600}
#stats{margin-left:auto;font-size:12px;color:var(--muted);white-space:nowrap}
#stats strong{color:var(--text)}

/* ── Grid ── */
.grid{padding:20px 32px;display:flex;flex-direction:column;gap:16px}
.no-results{padding:60px;text-align:center;color:var(--muted)}

/* ── Card ── */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);overflow:hidden}
.card-head{padding:13px 16px;display:flex;align-items:flex-start;gap:10px;cursor:pointer;user-select:none}
.card-head:hover{background:rgba(255,255,255,.02)}
.cnum{font-size:11px;font-weight:700;color:var(--muted);min-width:26px;padding-top:1px}
.cta{flex:1;min-width:0}
.cfname{font-size:13px;font-weight:700;color:#fff;word-break:break-all;margin-bottom:2px}
.cdtitle{font-size:11px;color:var(--muted);margin-bottom:5px}
.cchips{display:flex;gap:5px;flex-wrap:wrap}
.eco-badge{display:inline-flex;align-items:center;gap:3px;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600}
.eco-badge.valmet{background:rgba(108,140,255,.12);border:1px solid rgba(108,140,255,.3);color:var(--accent)}
.eco-badge.gor{background:rgba(249,115,22,.12);border:1px solid rgba(249,115,22,.3);color:var(--orange)}
.eco-badge.ksd{background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.3);color:var(--green)}
.tag{display:inline-flex;align-items:center;background:var(--surface2);border:1px solid var(--border);border-radius:4px;padding:2px 7px;font-size:10px;color:var(--muted)}
.tag.g{border-color:rgba(52,211,153,.3);color:var(--green);background:rgba(52,211,153,.06)}
.tag.r{border-color:rgba(248,113,113,.3);color:var(--red);background:rgba(248,113,113,.06)}
.tag.y{border-color:rgba(251,191,36,.3);color:var(--yellow);background:rgba(251,191,36,.06)}
.tag.o{border-color:rgba(249,115,22,.3);color:var(--orange);background:rgba(249,115,22,.06)}
.tag.b{border-color:rgba(96,165,250,.3);color:var(--blue);background:rgba(96,165,250,.06)}
.chevron{color:var(--muted);font-size:11px;padding-top:3px;transition:transform .2s;flex-shrink:0}
.card.open .chevron{transform:rotate(180deg)}
.card-body{display:none}
.card.open .card-body{display:block}

/* ── Card sections ── */
.cs{padding:14px 16px;border-top:1px solid var(--border)}
.cs-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);margin-bottom:10px;display:flex;align-items:center;gap:8px}
.cs-title::after{content:'';flex:1;height:1px;background:var(--border)}

/* Standard box */
.std-box{background:var(--code-bg);border:1px solid var(--border);border-radius:6px;padding:13px 15px;margin-bottom:12px}
.std-hdr{display:flex;align-items:center;gap:8px;margin-bottom:9px}
.std-name{font-size:13px;font-weight:700;color:#fff}
.conf{font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;background:rgba(52,211,153,.12);color:var(--green);border:1px solid rgba(52,211,153,.3)}
.ev-list{display:flex;flex-direction:column;gap:6px}
.ev-item{display:flex;gap:8px;font-size:12px;line-height:1.6;color:var(--muted)}
.ev-icon{flex-shrink:0;width:15px;text-align:center;margin-top:1px}
code{font-size:11px;background:var(--surface2);border:1px solid var(--border);border-radius:3px;padding:0 4px;color:#a8b9d0;font-family:'SF Mono',Consolas,monospace}

/* Metrics */
.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:10px}
.metric{background:var(--code-bg);border:1px solid var(--border);border-radius:8px;padding:11px 10px;text-align:center}
.mval{font-size:24px;font-weight:800;color:#fff;line-height:1;letter-spacing:-.5px}
.mlbl{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-top:5px}
.ebrk-chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.ebrk-chip{font-size:10px;font-family:'SF Mono',Consolas,monospace;background:var(--code-bg);border:1px solid var(--border);border-radius:4px;padding:2px 7px;color:var(--muted);white-space:nowrap}
.ebrk-chip b{color:var(--text);font-weight:700}

/* Connectivity */
.conn-row{display:flex;align-items:center;gap:10px;font-size:12px;padding:9px 12px;background:var(--code-bg);border:1px solid var(--border);border-radius:7px}
.cdot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.cdot.direct{background:var(--green);box-shadow:0 0 6px rgba(52,211,153,.5)}
.cdot.xdata{background:var(--yellow);box-shadow:0 0 6px rgba(251,191,36,.4)}
.cdot.none{background:var(--orange);box-shadow:0 0 6px rgba(249,115,22,.4)}
.cdot.parse_failed{background:var(--red);box-shadow:0 0 6px rgba(248,113,113,.4)}

/* ── NEW: Mapping tables ── */
.map-section{display:grid;grid-template-columns:1fr 1fr;gap:0}
@media(max-width:760px){.map-section{grid-template-columns:1fr}}
.map-panel{border-right:1px solid var(--border)}
.map-panel:last-child{border-right:none}
.map-panel .cs{border-top:none}

.mt{width:100%;border-collapse:collapse;font-size:11px}
.mt th{background:var(--surface2);color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.5px;padding:6px 10px;text-align:left;border-bottom:1px solid var(--border);white-space:nowrap}
.mt td{padding:6px 10px;border-bottom:1px solid rgba(46,50,71,.4);vertical-align:top}
.mt tr:last-child td{border-bottom:none}
.mt tr:hover td{background:rgba(255,255,255,.015)}

/* Block name column */
.mt td.bname{font-family:'SF Mono',Consolas,monospace;font-size:11px;color:var(--blue);white-space:nowrap;max-width:160px;overflow:hidden;text-overflow:ellipsis}
.mt td.cnt{text-align:right;color:var(--text);font-weight:600;white-space:nowrap}
/* Category pill in table */
.cat{display:inline-block;border-radius:3px;padding:1px 6px;font-size:10px;font-weight:600;white-space:nowrap}
.cat.Valve{background:rgba(96,165,250,.12);color:var(--blue);border:1px solid rgba(96,165,250,.25)}
.cat.Equipment{background:rgba(52,211,153,.1);color:var(--green);border:1px solid rgba(52,211,153,.25)}
.cat.Instrument{background:rgba(167,139,250,.1);color:var(--purple);border:1px solid rgba(167,139,250,.25)}
.cat.Pipeline{background:rgba(45,212,191,.1);color:var(--teal);border:1px solid rgba(45,212,191,.25)}
.cat.Title\ Block,.cat.TitleBlock{background:rgba(148,163,184,.1);color:var(--muted);border:1px solid rgba(148,163,184,.25)}
.cat.CAD\ Utility,.cat.CADUtility{background:rgba(46,50,71,.5);color:#475569;border:1px solid var(--border)}
.cat.GOR\ Marker,.cat.GORMarker{background:rgba(249,115,22,.1);color:var(--orange);border:1px solid rgba(249,115,22,.25)}
/* Attr field */
.mt td.field{color:var(--teal);font-size:10px;white-space:nowrap}
.mt td.sap{color:var(--muted);font-size:10px;max-width:200px}
.mt td.how-ident{font-size:10px;color:var(--muted);max-width:240px;cursor:help;padding-right:6px}
.how-clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.45;color:var(--green)}
.how-more{display:inline-block;margin-left:3px;font-size:9px;color:var(--accent);opacity:.7;vertical-align:middle}
.mt td.sample{font-family:'SF Mono',Consolas,monospace;font-size:10px;color:#a8b9d0;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
/* GOR layer row */
.mt td.lname{font-family:'SF Mono',Consolas,monospace;font-size:10px;color:var(--orange);max-width:200px;overflow:hidden;text-overflow:ellipsis}
.mt td.sem{color:var(--text);font-size:10px;white-space:nowrap}
.mt td.ldesc{color:var(--muted);font-size:10px}

/* Unmapped note */
.unmapped-note{font-size:11px;color:var(--muted);font-style:italic;padding:6px 0}

/* Fail banner */
.fail-banner{background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.2);border-radius:6px;padding:11px 14px;display:flex;gap:10px;align-items:flex-start;font-size:12px;color:var(--muted)}

/* Two-col utility */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:0}
@media(max-width:700px){.two-col{grid-template-columns:1fr}}
.two-col .cs{border-left:1px solid var(--border)}
.two-col .cs:first-child{border-left:none}

/* Text sample */
.tsrow{display:flex;gap:8px;align-items:baseline;padding:5px 0;border-bottom:1px solid rgba(46,50,71,.4);font-size:11px}
.tsrow:last-child{border-bottom:none}
.tslyr{font-size:9px;color:var(--accent);font-family:'SF Mono',Consolas,monospace;white-space:nowrap;background:rgba(108,140,255,.1);border:1px solid rgba(108,140,255,.2);border-radius:3px;padding:1px 5px;flex-shrink:0;max-width:90px;overflow:hidden;text-overflow:ellipsis}
.tstxt{color:var(--text);line-height:1.4}

/* Folder divider */
.fdiv{display:flex;align-items:center;gap:12px;margin:8px 0 2px;padding:0 2px}
.fdiv-lbl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);white-space:nowrap}
.fdiv-line{flex:1;height:1px;background:var(--border)}
.fdiv-cnt{font-size:10px;color:var(--muted);white-space:nowrap}

/* ── Tab panel visibility ── */
.tab-panel{display:none}
.tab-panel.active{display:block}
/* ── Forensic tab sticky controls offset (header ~130px) ── */
.tab-panel#tab-forensic .controls{top:130px}

/* ── Footer ── */
.doc-footer{border-top:1px solid var(--border);padding:18px 40px;display:flex;align-items:center;justify-content:space-between;margin-top:40px;background:var(--surface)}
.doc-footer-left{font-size:11px;color:var(--muted)}
.doc-footer-left strong{color:var(--text)}
.doc-footer-right{font-size:11px;color:var(--muted);text-align:right}

/* ── Print / Export ── */
@media print{
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  @page{margin:15mm 12mm;size:A4 landscape}
  body{background:#0d0f18!important;font-size:9pt}
  .doc-header{position:static!important;border-bottom:1px solid #252840!important}
  .doc-header-top{padding:14px 20px 12px!important}
  .doc-title{font-size:16pt!important}
  .doc-actions,.tab-nav,.controls,.guide,.chevron,.doc-btn,.card-head .chevron{display:none!important}
  .doc-right{flex-direction:row;align-items:center;gap:12px}
  .tab-panel{display:block!important;page-break-before:always}
  #tab-forensic{page-break-before:auto}
  .card{page-break-inside:avoid;margin-bottom:6px!important}
  .card-body{display:block!important}
  .card-head{cursor:default!important}
  .grid{padding:12px 20px!important;gap:8px!important}
  .main section,.section{padding:12px 20px!important}
  .doc-footer{padding:10px 20px!important;margin-top:20px!important}
  .no-print{display:none!important}
}
</style>
</head>
<body>

<div class="doc-header">
  <div class="doc-header-top">
    <div>
      <div class="doc-meta-line">Ensemble Flux &nbsp;·&nbsp; Shotton Mill Ltd, UK &nbsp;·&nbsp; Internal R&amp;D Report</div>
      <h1 class="doc-title">DWG <span>→</span> SAP Converter &nbsp;<span style="color:var(--border);font-weight:300">|</span>&nbsp; Discovery Assessment</h1>
      <div class="doc-chips">
        <span class="doc-chip"><span class="dot"></span>84 DWGs indexed</span>
        <span class="doc-chip">3 CAD Ecosystems</span>
        <span class="doc-chip">Valmet PS-21 · GOR Italian · KSD Swedish</span>
        <span class="doc-chip">August 2026</span>
      </div>
    </div>
    <div class="doc-right">
      <div class="doc-status">Discovery Phase · Draft</div>
      <div class="doc-actions no-print">
        <button class="doc-btn" onclick="expandAll()" title="Expand all drawing cards">Expand All</button>
        <button class="doc-btn primary" onclick="window.print()" title="Export to PDF via browser print">&#8595; Export PDF</button>
      </div>
    </div>
  </div>
  <nav class="tab-nav">
    <button class="tab-btn" onclick="showTab('exec',this)">Executive Summary</button>
    <div class="tab-nav-sep"></div>
    <button class="tab-btn" onclick="showTab('inventory',this)">Inventory &amp; Provenance</button>
    <button class="tab-btn active" onclick="showTab('forensic',this)">Forensic Analysis</button>
    <button class="tab-btn" onclick="showTab('standards',this)">Standards &amp; Resources</button>
    <button class="tab-btn" onclick="showTab('capabilities',this)">Extraction Capabilities</button>
    <button class="tab-btn" onclick="showTab('architecture',this)">Architecture &amp; Roadmap</button>
    <div class="tab-nav-sep"></div>
    <button class="tab-btn" onclick="showTab('questions',this)">Questions for Rachael</button>
    <button class="tab-btn" onclick="showTab('vocab',this)">Vocabulary</button>
  </nav>
</div>

<div class="main">

<div id="tab-forensic" class="tab-panel active">
<div class="controls">
  <div class="search-wrap">
    <span class="ico">🔍</span>
    <input id="search" type="text" placeholder="Search filename, tag, block, layer…" oninput="render()">
  </div>
  <div class="fg">
    <span class="fl">Ecosystem</span>
    <span class="pill active" onclick="setF('eco','all',this)">All</span>
    <span class="pill" onclick="setF('eco','valmet',this)">🇫🇮 Valmet</span>
    <span class="pill" onclick="setF('eco','gor',this)">🇮🇹 GOR</span>
    <span class="pill" onclick="setF('eco','ksd',this)">🇸🇪 KSD</span>
  </div>
  <div class="fg">
    <span class="fl">Folder</span>
    <span class="pill active" onclick="setF('folder','all',this)">All</span>
    <span class="pill" onclick="setF('folder','CHEM_PID',this)">CHEM</span>
    <span class="pill" onclick="setF('folder','OCC_PID',this)">OCC</span>
    <span class="pill" onclick="setF('folder','PM03_PID',this)">PM03</span>
    <span class="pill" onclick="setF('folder','TM01_PID',this)">TM01</span>
  </div>
  <div class="fg">
    <span class="fl">Connectivity</span>
    <span class="pill active" onclick="setF('conn','all',this)">All</span>
    <span class="pill" onclick="setF('conn','direct',this)">✅ LIN_FROM/TO</span>
    <span class="pill" onclick="setF('conn','none',this)">🔴 None</span>
    <span class="pill" onclick="setF('conn','parse_failed',this)">❌ Failed</span>
  </div>
  <div id="stats"></div>
</div>

<!-- ══════════════════════════════════════════════════════════════════
     LEGEND / GUIDE
════════════════════════════════════════════════════════════════════ -->
<div class="guide">
  <div class="guide-hdr" id="guide-hdr" onclick="toggleGuide()">
    <div class="guide-hdr-left">
      <span style="font-size:16px">📖</span>
      <h2>How to Read This Report</h2>
      <span class="guide-tag">Legend</span>
      <span class="guide-hint">DWG concepts · ecosystem identification · block categories · connectivity</span>
    </div>
    <span class="guide-chev" id="guide-chev">▼</span>
  </div>

  <div class="guide-body" id="guide-body">

    <!-- Block 1: DWG file concepts -->
    <div class="gb">
      <div class="gb-title">DWG File Concepts</div>
      <div class="gb-rows">
        <div class="gb-row">
          <div class="gb-term">Objects</div>
          <div class="gb-def">Total count of <strong>everything</strong> stored in the file — entities, block definitions, layers, text styles, linetypes, app ID registrations, XDATA records. A healthy Valmet P&ID: <strong>5,000–20,000</strong>. GOR: ~7,000–8,000. KSD: ~60–2,000.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">Entities</div>
          <div class="gb-def">Drawable elements in <strong>model space</strong> only: lines, circles, arcs, text, polylines, and block inserts (placed symbols). Excludes definitions and metadata.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">Blocks</div>
          <div class="gb-def">Reusable <strong>symbol definitions</strong> — the library. E.g. one block definition <code>VENTK</code> defines a ball valve symbol. Definitions count is how many unique symbols are defined.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">Block Inserts</div>
          <div class="gb-def">Each <strong>placement</strong> of a block on the drawing. <code>VENTK ×42</code> means 42 ball valves placed. Count × block name = equipment tally.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">Attr Tags</div>
          <div class="gb-def"><strong>Structured data fields</strong> attached to a block insert — like form fields on a symbol. Tag = field name (e.g. <code>VEPOSITIO</code>), value = the data (e.g. <code>35-26-FV-001</code>). Valmet: ~1,800 per drawing. GOR: ~1 per drawing. KSD: ~270.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">Layers</div>
          <div class="gb-def">Named <strong>organisational groups</strong> for entities. Layer name encodes equipment type or medium: Valmet uses <code>P-WATER</code>, <code>P-STEAM2</code>; GOR uses <code>1-AIR GOR</code>, <code>1-TAG AND INSTRUMENTS GOR</code>; KSD uses <code>PS</code>, <code>BLANKETT</code>.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">XDATA</div>
          <div class="gb-def"><strong>Extended Entity Data</strong> — custom structured data attached to any entity by a registered app. Valmet's <code>PCAD-POS-INFO</code> XDATA stores instrument type, area code, position ID, and description on each instrument bubble. <code>LIN_FROM / LIN_TO</code> XDATA on pipe polylines encodes connectivity.</div>
        </div>
        <div class="gb-row">
          <div class="gb-term">App IDs</div>
          <div class="gb-def">Software <strong>registration keys</strong> for XDATA. Which app IDs are registered is the primary ecosystem fingerprint: <code>PCAD_</code> = Valmet · <code>IDOK_</code> = GOR · <code>GENIUS_</code> only = KSD.</div>
        </div>
      </div>
    </div>

    <!-- Block 2: How we identify the standard -->
    <div class="gb">
      <div class="gb-title">How We Identify the Standard</div>
      <div class="gb-def" style="margin-bottom:12px">Four independent signals are cross-checked. All must agree — no single signal is used in isolation.</div>
      <div class="eco-fp">
        <div class="eco-fp-row" style="border:none;border-radius:0;background:none;font-size:9px;padding:0 0 4px 0">
          <div class="eco-fp-signal"></div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v" style="font-weight:700">🇫🇮 Valmet</div>
            <div class="eco-fp-val g" style="font-weight:700">🇮🇹 GOR</div>
            <div class="eco-fp-val k" style="font-weight:700">🇸🇪 KSD</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">App IDs</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">PCAD_ + GENIUS_</div>
            <div class="eco-fp-val g">IDOK_ + GENIUS_</div>
            <div class="eco-fp-val k">GENIUS_ only</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">Filename</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">PCSG / STOD / RAU</div>
            <div class="eco-fp-val g">GORA / GORB</div>
            <div class="eco-fp-val k">KSDM160104</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">Username</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">jani.linden, nina.niittykumpu…</div>
            <div class="eco-fp-val g">gorceschma</div>
            <div class="eco-fp-val k">ksdwenzhec</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">Layer lang.</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">Finnish (P-WATER, PKV)</div>
            <div class="eco-fp-val g">Italian (CARTIGLIO)</div>
            <div class="eco-fp-val k">Swedish (BLANKETT)</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">Block lang.</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">Finnish (VENTK, TOIMILV)</div>
            <div class="eco-fp-val g">Italian (Cartiglio, RevisioniTesta)</div>
            <div class="eco-fp-val k">Swedish (REVHUVUD, METSOHUVUD)</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">Data density</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">~1,800 attr tags / DWG</div>
            <div class="eco-fp-val g">~1 attr tag / DWG</div>
            <div class="eco-fp-val k">~270 attr tags / DWG</div>
          </div>
        </div>
        <div class="eco-fp-row">
          <div class="eco-fp-signal">Standard doc</div>
          <div class="eco-fp-vals">
            <div class="eco-fp-val v">SML PS-21 PDF ✅</div>
            <div class="eco-fp-val g">None ❌</div>
            <div class="eco-fp-val k">KSDM160104_010.00 ⚠️</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Block 3: Block categories -->
    <div class="gb">
      <div class="gb-title">Block Categories — What Each Maps To</div>
      <div class="gb-def" style="margin-bottom:12px">Blocks are classified by name lookup and prefix matching. Each category maps to a different SAP object type.</div>
      <div class="cat-legend">
        <div class="cl-row">
          <span class="cl-badge Valve">🔵 Valve</span>
          <div class="cl-text"><strong>Hand / control / check / safety valves</strong><br>Block names: <code>VENTK</code> (ball), <code>TOIMILV</code> (actuated), <code>TAKAISKU</code> (check), <code>VAROV</code> (safety relief)<br>→ SAP: Equipment record, Valve type classification</div>
        </div>
        <div class="cl-row">
          <span class="cl-badge Equipment">⚙️ Equipment</span>
          <div class="cl-text"><strong>Motors, pumps, compressors, reducers, heat exchangers</strong><br>Block names: <code>MOTOR</code>, <code>KOMPR</code>, <code>SEK2</code>, <code>COIL</code><br>→ SAP: Equipment Master record, linked to FLOC position</div>
        </div>
        <div class="cl-row">
          <span class="cl-badge Instrument">📊 Instrument</span>
          <div class="cl-text"><strong>Measurement &amp; control loop bubbles</strong><br>TI=temp indicator, LI=level, FI=flow, PI=pressure, LC/FC/TC=control<br>Block names: <code>P7Axxx</code>, <code>PPI_xxx</code> (Valmet) · <code>LOOPDCS</code> (GOR) · <code>T</code>, <code>PS_xxx</code> (KSD)<br>→ SAP: Instrument record; tag from PCAD XDATA or KRETS attr</div>
        </div>
        <div class="cl-row">
          <span class="cl-badge Pipeline">→ Pipeline</span>
          <div class="cl-text"><strong>Pipe connectors, flow arrows, cross-sheet references</strong><br><code>NUOLI</code> (direction arrow), <code>PI0NUOPR</code> (flow diagram connector), <code>PILH</code>/<code>PILV</code> (KSD cross-sheet continuation)<br>→ SAP: FLOC pipeline segment; connectivity graph edge</div>
        </div>
        <div class="cl-row">
          <span class="cl-badge TitleBlock">📋 Title Block</span>
          <div class="cl-text"><strong>Drawing metadata, revision table, stamps</strong><br><code>Valmet_TB01</code> / <code>VALMET_R_OTS</code> (Valmet) · <code>Cartiglio</code> (GOR) · <code>METSOHUVUD</code> (KSD)<br>→ SAP: Document Management, drawing revision history</div>
        </div>
        <div class="cl-row">
          <span class="cl-badge Utility">— CAD Utility</span>
          <div class="cl-text"><strong>Drawing geometry helpers — no process data</strong><br><code>GENAXEH</code>, <code>AME_NIL</code>, <code>PS-INIT</code>, anonymous <code>A$C…</code> blocks<br>→ Excluded from SAP extraction</div>
        </div>
      </div>
    </div>

    <!-- Block 4: Connectivity -->
    <div class="gb">
      <div class="gb-title">Connectivity — How Pipe Topology Is Encoded</div>
      <div class="gb-def" style="margin-bottom:12px">Connectivity determines whether the P&ID flow graph can be reconstructed automatically or requires spatial geometry analysis.</div>
      <div class="conn-legend">
        <div class="conn-item">
          <div class="conn-dot-lg direct"></div>
          <div class="conn-item-text">
            <strong>LIN_FROM / LIN_TO (Valmet PS-21 only)</strong>
            Named endpoints stored as PCAD_ XDATA on each pipe polyline. Every pipe segment knows exactly what it connects from and to. Enables <strong>full automated P&ID graph reconstruction</strong> — no geometry analysis needed. Record count shown in brackets.
          </div>
        </div>
        <div class="conn-item">
          <div class="conn-dot-lg xdata"></div>
          <div class="conn-item-text">
            <strong>XDATA present, no named endpoints</strong>
            Custom app data exists on entities (GENIUS_, IDOK_) but no LIN_FROM/LIN_TO schema. Connectivity cannot be read directly — requires inspection of specific app ID schemas. Applies to most GOR and some KSD drawings.
          </div>
        </div>
        <div class="conn-item">
          <div class="conn-dot-lg none"></div>
          <div class="conn-item-text">
            <strong>No semantic connectivity</strong>
            Pipe routing is LWPOLYLINE geometry only. Connectivity must be inferred from <strong>spatial proximity</strong> of polyline endpoints (geometric tracing). KSD cross-sheet refs are encoded in <code>BENÄMNING</code> attribute text (e.g. <code>KSDM160104103 sh.03</code>).
          </div>
        </div>
        <div class="conn-item">
          <div class="conn-dot-lg failed"></div>
          <div class="conn-item-text">
            <strong>Parse failed — no entity data</strong>
            ODA File Converter produced malformed DXF output (<code>DXFStructureError: missing ENDSEC tag</code>). Affects <strong>15 of 25 KSD DWGs</strong>. Only CSV-level metadata is available. Requires alternative parser (LibreDWG) or PDF fallback.
          </div>
        </div>
      </div>
      <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--border)">
        <div class="gb-title" style="margin-bottom:8px">Attribute Tag → SAP Field Quick Reference</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 16px;font-size:11px">
          <div><code>VEPOSITIO</code> → <span style="color:var(--teal)">Equipment / Valve Tag</span></div>
          <div><code>KRETS</code> → <span style="color:var(--teal)">Loop / Instrument Tag</span></div>
          <div><code>LINJA</code> → <span style="color:var(--teal)">Pipeline ID → FLOC line</span></div>
          <div><code>POSNR</code> → <span style="color:var(--teal)">Position serial no.</span></div>
          <div><code>VENIMI</code> → <span style="color:var(--teal)">Valve name (Finnish)</span></div>
          <div><code>BENÄMNING</code> → <span style="color:var(--teal)">Description / cross-ref</span></div>
          <div><code>VEKEMIKAALI</code> → <span style="color:var(--teal)">Process medium</span></div>
          <div><code>PIPEID</code> → <span style="color:var(--teal)">Pipeline segment ID</span></div>
          <div><code>VEVALMISTAJA</code> → <span style="color:var(--teal)">Manufacturer</span></div>
          <div><code>PUTDN/PUTPN</code> → <span style="color:var(--teal)">Pipe DN / PN rating</span></div>
          <div><code>MOOPOS/MOOTEHO</code> → <span style="color:var(--teal)">Motor tag / power</span></div>
          <div><code>KAAVIO</code> → <span style="color:var(--teal)">Cross-drawing reference</span></div>
        </div>
      </div>
    </div>

  </div><!-- /.guide-body -->
</div><!-- /.guide -->

<div class="grid" id="grid"></div>
</div><!-- /#tab-forensic -->

""" + PANEL_EXEC + "\n" + PANEL_INVENTORY + "\n" + PANEL_STANDARDS + "\n" + PANEL_CAPABILITIES + "\n" + PANEL_ARCHITECTURE + "\n" + PANEL_QUESTIONS + "\n" + PANEL_VOCAB + r"""

</div><!-- /.main -->

<footer class="doc-footer no-print">
  <div class="doc-footer-left">
    <strong>DWG → SAP Discovery Assessment</strong> &nbsp;·&nbsp; Shotton Mill Ltd &nbsp;·&nbsp; Ensemble Flux &nbsp;·&nbsp; August 2026
  </div>
  <div class="doc-footer-right">
    84 DWGs &nbsp;·&nbsp; 3 Ecosystems &nbsp;·&nbsp; Draft v1.0 &nbsp;·&nbsp; Internal Use Only
  </div>
</footer>

<style>
""" + _css_block + r"""
</style>
<script>
function showTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  if (btn) btn.classList.add('active');
  if (name === 'forensic') render();
}
function expandAll() {
  if (!document.getElementById('grid').innerHTML) render();
  document.querySelectorAll('.card').forEach(c => {
    c.classList.add('open');
    openCards.add(parseInt(c.id.replace('c','')));
  });
}
const DATA = """ + js_data + r""";
function toggleGuide(){
  const body=document.getElementById('guide-body');
  const chev=document.getElementById('guide-chev');
  const open=body.style.display==='block';
  body.style.display=open?'none':'block';
  chev.textContent=open?'▼':'▲';
}
const F = {eco:'all',folder:'all',conn:'all'};
function setF(k,v,el){
  F[k]=v;
  el.closest('.fg').querySelectorAll('.pill').forEach(p=>p.classList.remove('active'));
  el.classList.add('active');
  render();
}
function matches(r){
  const q=document.getElementById('search').value.trim().toLowerCase();
  if(F.eco!=='all'&&r.eco!==F.eco)return false;
  if(F.folder!=='all'&&r.folder!==F.folder)return false;
  if(F.conn!=='all'&&r.conn_badge!==F.conn)return false;
  if(!q)return true;
  const hay=[r.fname,r.title,r.folder,r.standard,r.last_saved,
    ...r.top_attrs.map(a=>a.tag+' '+a.sample),
    ...(r.block_mappings||[]).map(b=>b.name+' '+b.role),
    ...(r.attr_mappings||[]).map(a=>a.tag+' '+a.field+' '+a.sample),
    ...r.evidence.map(e=>e.text),r.entity_summary
  ].join(' ').toLowerCase();
  return q.split(/\s+/).every(t=>hay.includes(t));
}

const EM={valmet:{flag:'🇫🇮',lbl:'Valmet PS-21'},gor:{flag:'🇮🇹',lbl:'GOR Italian'},ksd:{flag:'🇸🇪',lbl:'KSD Swedish'}};
const CM={direct:{cls:'direct',lbl:'LIN_FROM/LIN_TO direct graph'},
          xdata:{cls:'xdata',lbl:'XDATA, no named endpoints'},
          none:{cls:'none',lbl:'No semantic connectivity'},
          parse_failed:{cls:'parse_failed',lbl:'Parse failed'}};
const CC={direct:'g',xdata:'y',none:'o',parse_failed:'r'};

function evHTML(ev){
  if(!ev.length)return'<div class="unmapped-note">No evidence (parse failed)</div>';
  return'<div class="ev-list">'+ev.map(e=>`<div class="ev-item"><span class="ev-icon">${e.icon}</span><span>${e.text}</span></div>`).join('')+'</div>';
}

// ── Block mapping table ──────────────────────────────────────────────────────
function blockMapHTML(bm){
  if(!bm||!bm.length)return'<div class="unmapped-note">No mappable blocks in top inserts (title-block / utility blocks only, or parse failed)</div>';
  return`<table class="mt">
    <thead><tr><th>Block</th><th style="text-align:right">Count</th><th>Category</th><th>Process Role</th><th>Evidence</th><th>SAP Mapping</th></tr></thead>
    <tbody>${bm.map(b=>{
      const hi=b.how_ident||'—';
      const first=hi.split(' · ')[0];
      const hasMore=hi.includes(' · ');
      const safe=hi.replace(/"/g,'&quot;');
      return`<tr>
        <td class="bname" title="${b.name}">${b.name}</td>
        <td class="cnt">${b.count}×</td>
        <td><span class="cat ${b.category}">${b.icon} ${b.category}</span></td>
        <td style="color:var(--text);font-size:11px;max-width:130px">${b.role}</td>
        <td class="how-ident" title="${safe}"><div class="how-clamp">${first}</div>${hasMore?'<span class="how-more">+more ⓘ</span>':''}</td>
        <td class="sap">${b.sap_mapping}</td>
      </tr>`;
    }).join('')}</tbody>
  </table>`;
}

// ── Attribute tag mapping table ──────────────────────────────────────────────
function attrMapHTML(am){
  if(!am||!am.length)return'<div class="unmapped-note">No attribute tags found — data in plain TEXT entities (GOR) or parse failed</div>';
  return`<table class="mt">
    <thead><tr><th>Attribute Tag</th><th style="text-align:right">Count</th><th>Field / Function</th><th>SAP / Converter Mapping</th><th>Example Value</th></tr></thead>
    <tbody>${am.map(a=>`<tr>
      <td class="bname" title="${a.tag}">${a.tag}</td>
      <td class="cnt">${a.count}×</td>
      <td class="field">${a.icon} ${a.field}</td>
      <td class="sap">${a.description}</td>
      <td class="sample" title="${a.sample}">${a.sample||'<em style="color:var(--border)">—</em>'}</td>
    </tr>`).join('')}</tbody>
  </table>`;
}

// ── GOR layer semantic table ─────────────────────────────────────────────────
function gorLayerHTML(gl){
  if(!gl||!gl.length)return'';
  return`<div class="cs">
    <div class="cs-title">GOR Layer → Data Type Mapping (text entities, no block attrs)</div>
    <table class="mt">
      <thead><tr><th>Layer</th><th>Data Type</th><th>Content / Pattern</th></tr></thead>
      <tbody>${gl.map(g=>`<tr>
        <td class="lname">${g.layer}</td>
        <td class="sem">${g.icon} ${g.semantic}</td>
        <td class="ldesc">${g.description}</td>
      </tr>`).join('')}</tbody>
    </table>
  </div>`;
}

function cardHTML(r){
  const em=EM[r.eco]||{flag:'?',lbl:r.eco};
  const cm=CM[r.conn_badge]||{cls:'none',lbl:r.conn_text};
  const vn=r.eco==='gor'?' · AC1024':' · AC1032';

  const failBanner=r.is_failed?`<div class="cs">
    <div class="fail-banner">
      <span style="font-size:18px">❌</span>
      <div>
        <strong style="color:var(--red)">Parse Failed</strong>
        <code style="color:var(--red);border-color:rgba(248,113,113,.3)">${r.error}</code><br>
        <span style="margin-top:3px;display:block">Evidence from CSV metadata and filename only. Objects (CSV): <strong style="color:var(--text)">${r.objects}</strong></span>
      </div>
    </div>
  </div>`:'';

  const eChips=r.entity_summary?r.entity_summary.split(', ').map(p=>{const m=p.match(/^(.+?)×(\d+)$/);return m?`<span class="ebrk-chip"><b>${m[2]}</b> ${m[1]}</span>`:`<span class="ebrk-chip">${p}</span>`;}).join(''):'';
  const bodyContent=r.is_failed?'':`
    <div class="two-col">
      <div class="cs">
        <div class="cs-title">Drawing Metrics</div>
        <div class="metrics">
          <div class="metric"><div class="mval">${r.objects}</div><div class="mlbl">Objects</div></div>
          <div class="metric"><div class="mval">${r.entities}</div><div class="mlbl">Entities</div></div>
          <div class="metric"><div class="mval">${r.layers}</div><div class="mlbl">Layers</div></div>
          <div class="metric"><div class="mval">${r.blocks}</div><div class="mlbl">Blocks</div></div>
          <div class="metric"><div class="mval">${r.attr_count}</div><div class="mlbl">Attr Tags</div></div>
        </div>
        ${eChips?`<div><div style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">Entity breakdown</div><div class="ebrk-chips">${eChips}</div></div>`:''}
      </div>
      <div class="cs">
        <div class="cs-title">Connectivity</div>
        <div class="conn-row"><div class="cdot ${cm.cls}"></div><span style="color:var(--text);font-weight:500">${r.conn_text}</span></div>
        ${r.text_samples.length?`<div style="margin-top:14px"><div class="cs-title" style="margin-bottom:6px">Text samples (model space)</div>${r.text_samples.map(s=>`<div class="tsrow"><span class="tslyr" title="${s.layer}">${s.layer}</span><span class="tstxt">${s.text}</span></div>`).join('')}</div>`:''}
      </div>
    </div>

    <div class="cs">
      <div class="cs-title">Block Inserts → Equipment / Valve / Instrument / Pipeline Mapping</div>
      ${blockMapHTML(r.block_mappings)}
    </div>

    <div class="cs">
      <div class="cs-title">Attribute Tags → Field / Function / SAP Mapping</div>
      ${attrMapHTML(r.attr_mappings)}
    </div>

    ${r.gor_layer_mappings&&r.gor_layer_mappings.length?gorLayerHTML(r.gor_layer_mappings):''}
  `;

  return`<div class="card" id="c${r.n}">
    <div class="card-head" onclick="tog(${r.n})">
      <div class="cnum">#${r.n}</div>
      <div class="cta">
        <div class="cfname">${r.fname}</div>
        ${r.title&&r.title!==r.fname.replace('.dwg','')?`<div class="cdtitle">${r.title}</div>`:''}
        <div class="cchips">
          <span class="eco-badge ${r.eco}">${em.flag} ${em.lbl}</span>
          <span class="tag">${r.folder}</span>
          <span class="tag">${r.last_saved||'—'}</span>
          <span class="tag">${r.objects} obj${vn}</span>
          ${r.is_failed?'<span class="tag r">❌ parse failed</span>':`<span class="tag ${CC[r.conn_badge]||''}">${cm.lbl}</span>`}
          <span class="tag">${r.attr_count} tags</span>
          ${(r.block_mappings||[]).length?`<span class="tag b">${r.block_mappings.length} blocks mapped</span>`:''}
        </div>
      </div>
      <div class="chevron">▼</div>
    </div>
    <div class="card-body">
      <div class="cs">
        <div class="cs-title">Standard Identification &amp; Evidence</div>
        <div class="std-box">
          <div class="std-hdr">
            <div class="std-name">${em.flag} ${r.standard}</div>
            <div class="conf">HIGH CONFIDENCE</div>
          </div>
          ${evHTML(r.evidence)}
        </div>
      </div>
      ${failBanner}
      ${bodyContent}
    </div>
  </div>`;
}

const FLBL={
  CHEM_PID:'🧪 CHEM_PID — Chemical Preparation (Valmet PS-21)',
  OCC_PID:'♻️ OCC_PID — OCC Recycled Fibre Plant (Valmet PS-21)',
  PM03_PID:'📄 PM03_PID — Paper Machine 3 (Valmet PS-21 + Flow Diagrams)',
  TM01_PID:'🏭 TM01_PID — Tissue Machine 1 (GOR Italian + KSD Swedish)',
};

let openCards=new Set();
function tog(n){
  const el=document.getElementById('c'+n);
  el.classList.toggle('open');
  openCards[el.classList.contains('open')?'add':'delete'](n);
}

function render(){
  const vis=DATA.filter(matches);
  document.getElementById('stats').innerHTML=`Showing <strong>${vis.length}</strong> of <strong>${DATA.length}</strong> drawings`;
  const grid=document.getElementById('grid');
  if(!vis.length){grid.innerHTML='<div class="no-results">No drawings match your filters.</div>';return;}
  let html='',lastF='';
  const fc={};vis.forEach(r=>{fc[r.folder]=(fc[r.folder]||0)+1});
  vis.forEach(r=>{
    if(r.folder!==lastF){
      lastF=r.folder;
      html+=`<div class="fdiv">
        <div class="fdiv-lbl">${FLBL[r.folder]||r.folder}</div>
        <div class="fdiv-line"></div>
        <div class="fdiv-cnt">${fc[r.folder]} drawing${fc[r.folder]!==1?'s':''}</div>
      </div>`;
    }
    html+=cardHTML(r);
  });
  grid.innerHTML=html;
  openCards.forEach(n=>{const el=document.getElementById('c'+n);if(el)el.classList.add('open')});
}
render();
</script>
</body>
</html>"""

OUT.write_text(HTML, encoding="utf-8")
print(f"Written → {OUT}  ({OUT.stat().st_size//1024} KB)")
