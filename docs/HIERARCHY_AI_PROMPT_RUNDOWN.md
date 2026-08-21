# Hierarchy AI — step-by-step rundown

What we send to the model, how screenshots are made, and what comes back.

**Full DWG → dump → inventory → enrich → AI → scores (all models):** [`FULL_PIPELINE_RUNDOWN.md`](./FULL_PIPELINE_RUNDOWN.md)

**Defaults (best so far)**

| Setting | Value |
|---|---|
| Model | `eu.anthropic.claude-sonnet-4-6` |
| Prompt template | `prompts/pid_hierarchy_gt_v8.md` |
| Script | `dwg_pid_hierarchy_ai.py` |
| Command | `make hierarchy-ai TAGS=35-24L008,35-24P509` |

---

## Big picture (one pass per equipment tag)

```text
DWG
 └─ dump / inventory / enrich   (CAD facts)
 └─ for each TAG:
      1. find parent XY
      2. render viewer screenshot (PNG)
      3. build CAD dossier + candidate tags
      4. fill prompt template
      5. send text + PNG → Bedrock
      6. parse JSON → hierarchy CSV rows
```

Each Bedrock call is **one FUNCTION** (e.g. `35-24L008`). We do **not** send the whole sheet at once.

---

## Prerequisites (must already exist)

Run the upstream pipeline first:

```bash
make all          # or: dump → inventory → enrich
```

Needed inputs under `outputs/jsons/`:

| File | Used for |
|---|---|
| `Broke System.pid_enrichment.json` | tag register, title block, line bindings |
| `Broke System.pid_inventory.json` | nearby lines / valves / instruments |
| `Broke System.structural_dump.json` | nearby drawing text tokens |
| `inputs/Broke System.dwg` | ODA → viewer raster |

---

## Step-by-step: one tag (`35-24L008`)

### Step 0 — Choose tags

```bash
make hierarchy-ai TAGS=35-24L008,35-24P509
```

Script splits on commas → `["35-24L008", "35-24P509"]` and loops.

---

### Step 1 — Load CAD context

From enrichment JSON:

1. **Title / plant context** (from title block attributes)

```text
SITE:        Shotton Paper Mill, United Kingdom
LINE:        Shotton PM3
PROCESS:     Broke System
SUB-PROCESS: BR1          ← hardcoded when process name contains "broke"
```

2. **Parent equipment** for the tag (from `tag_register`)

Example for `35-24L008`:

```text
resolved_tag:        35-24L008
category:            process_equipment
block_name:          PPI_1302A-25_0
XY:                  (660.0, 297.5)
nearby_descriptions: WINDER PULPER; HP-33G2; 800 BDTPD
```

If no parent coords → skip that tag with a warning.

---

### Step 2 — Take the screenshot (viewer crop)

This is **not** a manual AutoCAD screenshot. We render a local crop from the DWG via **ODA File Converter + ezdxf drawing backend**.

#### 2a. Open the drawing

```text
DWG → odafc.readfile() → ezdxf document in memory
```

#### 2b. Decide the camera window (adaptive zoom)

Function: `adaptive_view_window()`

- Center on parent XY
- Look at nearby tags in the register
- **Sparse area** (big vessel) → zoom out (larger window, up to ~`crop-half` = 165 CAD units)
- **Dense skid** (pump) → slightly tighter (down toward `crop-half-min` ≈ 105)
- Always keep room so attached lines / peer equipment stay visible

Result: a square-ish CAD window `(xmin, ymin, xmax, ymax)` around the parent.

#### 2c. Decide the red PARENT box

Function: `parent_highlight_box()`

- Cluster same-tag symbols near the parent (radius ~55 CAD units)
- Pad ~24 units
- This box is **only the parent machine**, not the whole crop

#### 2d. Rasterize entities in the window

Function: `viewer_screenshot()`

1. Collect modelspace entities whose bbox intersects the window  
2. Draw them with `ezdxf` Frontend → PyMuPDF backend  
3. Export PNG at **260 DPI** (default)  
4. Overlay a thick **red rectangle** + label `PARENT 35-24L008`

#### 2e. Write the file

```text
outputs/evidence/Broke System.viewer_35-24L008.png
```

Console looks like:

```text
[shot] 35-24L008: N ents, window=WxH -> Broke System.viewer_35-24L008.png (width x height)
```

**Why a crop, not the full sheet?**  
Full P&IDs are huge and noisy. The crop forces the model to read *this* equipment’s neighbourhood. The red box tells it which symbol is FUNCTION.

**Flags**

| Flag | Meaning |
|---|---|
| `--shots-only` | Write PNGs; skip Bedrock |
| `--reuse-shots` | Keep existing evidence PNGs |
| `--crop-half` / `--crop-half-min` | Zoom window size |
| `--dpi` | Raster resolution (default 260) |

---

### Step 3 — Build the CAD dossier (text evidence pack)

Function: `build_equipment_dossier()` — pulls everything within ~200 CAD units of the parent.

Sections (real shape):

```text
Parent tag: 35-24L008
Parent category/block: process_equipment / PPI_1302A-25_0
Parent XY: (660.0, 297.5)
Nearby descriptions: WINDER PULPER; HP-33G2; 800 BDTPD

Same-tag CAD family:
- process_equipment @ (660.0,297.5) block=PPI_1302A-25_0 nearby=…
- motors / valves / instruments with same resolved tag …

Nearby line numbers (short ids preferred in output):
- 35-24-009  full=35-24-009-PP-600-E10H2A  d=46  layer=P-LINEPOS
- 35-24-011  full=35-24-011-PP-250-E10H2A  d=107 …
- …

Nearby devices (valves/instruments/pumps/…):
- valves: …  d=113  block=PPI_0900A
- instruments: … 
- …

Nearby peer primary equipment (do NOT nest under parent):
- 35-24P509 (pumps, d=…)

Nearby drawing text tokens:
- short tags / numbers found in text entities near the crop
```

Full sample saved at:

`docs/examples/sample_dossier_35-24L008.txt`

---

### Step 4 — Collect candidate tags (whitelist)

Function: `collect_candidate_tags()` — nearby tags from register + inventory + structural text (~220 unit radius).

Example shortlist for `35-24L008`:

```text
35-24L008, 35-24P509, 35-24-180, 35-24-1094, 35-24-226,
35-24-178, 35-24-009, 35-24-181, 35-24-008.2, 35-24-184,
35-24-007, 35-24-008.1, 35-24LV2-513, …
```

Full list: `docs/examples/sample_candidates_35-24L008.txt`

The model should prefer these (and dossier short line ids) over inventing new tags.

---

### Step 5 — Fill the prompt template

Template: `prompts/pid_hierarchy_gt_v8.md`

Placeholders substituted by `build_hierarchy_prompt()` / `load_prompt()`:

| Placeholder | Filled with |
|---|---|
| `$site` | Shotton Paper Mill, United Kingdom |
| `$line` | Shotton PM3 |
| `$process` | Broke System |
| `$sub_process` | BR1 |
| `$tag` | 35-24L008 |
| `$parent_dossier` | Step 3 dossier text |
| `$candidates` | Step 4 comma-separated list |

The template also includes:

1. Role (“senior tagging engineer…”)  
2. Locked plant context  
3. CAD dossier  
4. Candidate tags  
5. **Worked examples** (vessel style vs pump style — teach *shape*, not copy tags)  
6. Ownership rules (peers ≠ children; short line ids; XOR EQUIPMENT/SUB-EQUIPMENT)  
7. Required **JSON schema** for the answer  

Full filled prompt sample:

`docs/examples/sample_prompt_35-24L008.md`

---

### Step 6 — What actually goes to Bedrock

One `converse` call per tag:

```text
content = [
  { "text":  <filled prompt ~6k chars> },
  { "image": { "format": "png", "source": { "bytes": <viewer PNG> } } }
]
```

| Piece | Role |
|---|---|
| Text prompt | Rules + plant context + dossier + candidates + examples |
| Image | Viewer crop with red PARENT box |

**Vision exception:** text-only models (e.g. `openai.gpt-oss`) get the prompt only, plus a note to use dossier/candidates without inventing.

---

### Step 7 — Model response (JSON)

Expected shape:

```json
{
  "sub_process": "BR1",
  "function": "35-24L008",
  "rows": [
    {"equipment": "35-24-009", "subequipment": "", "mask": ""},
    {"equipment": "35-24LC-…", "subequipment": "", "mask": ""},
    {"equipment": "", "subequipment": "35-24-…", "mask": ""}
  ],
  "peers": [{"tag": "35-24P509", "evidence": "adjacent pump, not child"}],
  "notes": [],
  "confidence": "high"
}
```

Rules we enforce in post-processing / prompt:

- FUNCTION cell = parent tag string  
- Children = tags only  
- Line numbers as **short** form (`35-24-192`, not full pipe string)  
- One of EQUIPMENT or SUB-EQUIPMENT per row  
- Peers listed separately, not nested  

---

### Step 8 — Write outputs

Per run:

| Output | Path |
|---|---|
| Hierarchy CSV | `outputs/Broke System.hierarchy.csv` |
| GT-shaped CSV | `outputs/Broke System.hierarchy_gt.csv` |
| Raw AI JSON | `outputs/jsons/Broke System.hierarchy_ai.json` |
| Viewer PNGs | `outputs/evidence/Broke System.viewer_<TAG>.png` |
| Run log | `outputs/logs/hierarchy-ai.log` |

CSV nesting matches the ground-truth workbook style:

```text
SITE → LINE → PROCESS → SUB-PROCESS → FUNCTION → EQUIPMENT → SUB-EQUIPMENT
```

---

## Worked example (prompt teaching section)

These are **inside** the prompt so the model learns the sheet pattern (do not treat as real children of `$tag`):

### Example A — vessel / pulper style

```text
SUB-PROCESS=BR1
FUNCTION=35-24L001
EQUIPMENT:
  35-24LC-101          <- level instrument on vessel
  35-24-101            <- nozzle / connected line short id
  35-24-102
  35-24L001.1
SUB-EQUIPMENT:
  under 35-24-102 -> 35-24-104
```

### Example B — pump style

```text
SUB-PROCESS=BR1
FUNCTION=35-24P501
EQUIPMENT:
  35-24P501
  35-24-501.1
  35-24-111            <- suction
  35-24-112            <- discharge
SUB-EQUIPMENT under suction/discharge:
  35-24-113, 35-24LV1-501, 35-24XS-501, …
```

---

## Mini example of the full packet for `35-24L008`

**1. Image attached**

`outputs/evidence/Broke System.viewer_35-24L008.png`  
(red box labelled `PARENT 35-24L008` on the Winder Pulper)

**2. Text packet (abbreviated)**

```text
You are a senior tagging engineer…

## Locked plant context
- SITE: Shotton Paper Mill, United Kingdom
- LINE: Shotton PM3
- PROCESS: Broke System
- SUB-PROCESS: BR1
- FUNCTION: 35-24L008

## CAD dossier for this parent
Parent tag: 35-24L008
Parent category/block: process_equipment / PPI_1302A-25_0
Nearby descriptions: WINDER PULPER; HP-33G2; 800 BDTPD
Nearby line numbers: 35-24-009, 35-24-011, 35-24-013, …
Nearby peer primary equipment: 35-24P509 (do NOT nest)

## Candidate tags near the crop
35-24L008, 35-24P509, 35-24-009, 35-24-181, …

## Worked examples …
## STRICT JSON only { ... }
```

**3. Model returns JSON rows → flattened into hierarchy CSV**

---

## How to reproduce locally

```bash
# 1) CAD extract (once)
make all

# 2) Hierarchy for specific equipment
make hierarchy-ai TAGS=35-24L008,35-24P509

# 3) Screenshots only (debug zoom)
python3 dwg_pid_hierarchy_ai.py --shots-only --tags 35-24L008

# 4) Score vs ground truth (if GT file present)
make hierarchy-eval
# or: python3 eval_hierarchy_gt.py ...
```

Inspect:

```text
outputs/evidence/Broke System.viewer_35-24L008.png   ← what the model saw
docs/examples/sample_prompt_35-24L008.md             ← what the model read (sample)
outputs/Broke System.hierarchy.csv                   ← sheet output
```

---

## Pipeline diagram

```text
┌──────────────────┐
│ inputs/*.dwg     │
└────────┬─────────┘
         │ make all
         ▼
┌──────────────────┐     ┌─────────────────────────────┐
│ enrichment JSON  │────▶│ pick parent XY + title ctx  │
│ inventory JSON   │     └──────────────┬──────────────┘
│ structural JSON  │                    │
└──────────────────┘          ┌─────────┴─────────┐
                              ▼                   ▼
                    ┌─────────────────┐  ┌──────────────────┐
                    │ viewer PNG      │  │ dossier +        │
                    │ (ODA + ezdxf)   │  │ candidates       │
                    │ + red PARENT    │  │                  │
                    └────────┬────────┘  └────────┬─────────┘
                             │                    │
                             └─────────┬──────────┘
                                       ▼
                          ┌────────────────────────┐
                          │ prompt template v4     │
                          │ + image bytes          │
                          │ → Bedrock Claude 4.6   │
                          └────────────┬───────────┘
                                       ▼
                          ┌────────────────────────┐
                          │ JSON → hierarchy CSV   │
                          └────────────────────────┘
```

---

## One-line summary for stakeholders

We send a **local CAD crop with a red parent box**, plus a **prepared briefing** (plant context, nearby line/device facts, candidate tag whitelist, and worked examples)—not a blank photo of the whole drawing.
