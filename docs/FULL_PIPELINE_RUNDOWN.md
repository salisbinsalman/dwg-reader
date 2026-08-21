# Full pipeline rundown — DWG → hierarchy (with accuracies)

End-to-end path for `inputs/Broke System.dwg`, including what each stage produces, how we score, and model/prompt results from the pilot equipment (`35-24L009` + `35-24P519`).

**Related:** screenshot + prompt packet details → [`HIERARCHY_AI_PROMPT_RUNDOWN.md`](./HIERARCHY_AI_PROMPT_RUNDOWN.md)

---

## Verdict (defaults we ship)

| Item | Choice | Why |
|---|---|---|
| Model | `eu.anthropic.claude-sonnet-4-6` | Best micro tag F1 on pilot GT |
| Prompt | `prompts/pid_hierarchy_gt_v8.md` | Current shipping default (`make hierarchy-ai`) |
| Pilot score (L009 / P519) | **61.8%** micro tag F1 | Met ≥60% target |
| Follow-on (L008 / P509) | **56.0%** micro tag F1 | Same combo; more peer-bleed |

```bash
make all
make hierarchy-ai TAGS=35-24L009,35-24P519
make hierarchy-eval
```

---

## Stage map (step by step)

```text
0. Input DWG
1. Dump (forensic + structural)     make run-json / make all
2. Inventory (layer buckets)        make inventory
3. Enrich (tags, lines, loops)      make enrich
4. Hierarchy AI (shot + Bedrock)    make hierarchy-ai
5. Eval vs ground truth             make hierarchy-eval
```

`make all` = steps **1 → 2 → 3**. Hierarchy AI is separate because it needs AWS Bedrock.

---

## Step 0 — Input

| Item | Value |
|---|---|
| Drawing | `inputs/Broke System.dwg` |
| Site (from title block) | Shotton Paper Mill, United Kingdom |
| Line | Shotton PM3 |
| Process | Broke System |
| Sub-process (convention) | `BR1` |

---

## Step 1 — Dump (CAD → Excel + JSON)

**Command:** `make run-json` (or first part of `make all`)  
**Script:** `dwg_pure_dump.py`  
**How:** ODA File Converter opens DWG → ezdxf reads entities → forensic + structural extracts.

**Writes (conceptually):**

| Artifact | Location |
|---|---|
| Dump workbook | `outputs/Broke System.*.xlsx` (dump sheets) |
| Structural JSON | `outputs/jsons/Broke System.structural_dump.json` |
| Other dump JSON | under `outputs/jsons/` |

**What we get:** every block, text, line, handle, layer, XY — the raw fuel for later stages. No AI yet.

---

## Step 2 — Inventory (P&ID component buckets)

**Command:** `make inventory`  
**Script:** `dwg_pid_inventory.py`

Layer / block heuristics sort symbols into:

- pumps, motors, process equipment  
- valves, control valves, instruments  
- lines / line markers / fittings  
- title block, etc.

**Writes:**

| Artifact | Location |
|---|---|
| Inventory Excel | `outputs/Broke System.pid_inventory.xlsx` |
| Inventory JSON | `outputs/jsons/Broke System.pid_inventory.json` |

**Used later for:** nearby devices + line numbers in the AI **dossier** and **candidate tags**.

---

## Step 3 — Enrich (tag register + bindings)

**Command:** `make enrich`  
**Script:** `dwg_pid_enrich.py`

Builds engineer-facing structure:

- **Tag register** — resolved tags with category, block, XY, nearby text  
- **Line geometry bindings** — label ↔ pipe  
- **Loops / instruments**  
- **Title block** fields (SITE / LINE / PROCESS)

**Writes:**

| Artifact | Location |
|---|---|
| Enrichment Excel | `outputs/Broke System.pid_enrichment.xlsx` |
| Enrichment JSON | `outputs/jsons/Broke System.pid_enrichment.json` |

**Used later for:** parent XY, plant context, same-tag family, peers.

---

## Step 4 — Hierarchy AI (per FUNCTION tag)

**Command:**

```bash
make hierarchy-ai TAGS=35-24L009,35-24P519
# or
make hierarchy-ai TAGS=35-24L008,35-24P509
```

**Script:** `dwg_pid_hierarchy_ai.py`  
**Defaults:** Claude Sonnet 4.6 + `pid_hierarchy_gt_v8.md`

### Per-tag loop (e.g. `35-24L009`)

| # | Action | Detail |
|---|---|---|
| 4.1 | Pick parent | From tag register → category, block, XY |
| 4.2 | Adaptive zoom | Window ~105–165 CAD units; denser skids tighter |
| 4.3 | Viewer screenshot | ODA/ezdxf raster @ 260 DPI + **red PARENT box** → `outputs/evidence/Broke System.viewer_<TAG>.png` |
| 4.4 | CAD dossier | Nearby lines, devices, peers, drawing text (~200 u) |
| 4.5 | Candidate whitelist | Nearby tags (~220 u) |
| 4.6 | Fill prompt | Context + dossier + candidates + worked examples |
| 4.7 | Bedrock call | **Text + PNG** (vision models) |
| 4.8 | Parse JSON | EQUIPMENT / SUB-EQUIPMENT rows + peers |
| 4.9 | Append CSV | Nest under SITE → … → FUNCTION |

**Writes:**

| Artifact | Location |
|---|---|
| Hierarchy CSV | `outputs/Broke System.hierarchy.csv` |
| GT-shaped CSV | `outputs/Broke System.hierarchy_gt.csv` |
| Raw AI JSON | `outputs/jsons/Broke System.hierarchy_ai.json` |
| Evidence PNGs | `outputs/evidence/Broke System.viewer_*.png` |
| Log | `outputs/logs/hierarchy-ai.log` |

Full packet explanation + examples: [`HIERARCHY_AI_PROMPT_RUNDOWN.md`](./HIERARCHY_AI_PROMPT_RUNDOWN.md) and `docs/examples/`.

---

## Step 5 — Evaluate vs ground truth

**Command:** `make hierarchy-eval`  
**Script:** `eval_hierarchy_gt.py`  
**Pilot GT:** `resources/gt_hierarchy_broke_system.xlsx` (functions **L009** + **P519**)  
**Follow-on GT:** `inputs/gt_hierarchy_L008_P509.csv`

### How accuracy is defined

**Headline metric = micro tag F1**

- For each FUNCTION, take the set of child tags (EQUIPMENT ∪ SUB-EQUIPMENT)  
- Compare predicted set vs GT set  
- Aggregate TP / FP / FN across all functions → precision, recall, F1  

**Not** in the headline score:

- Row order  
- MASK column  
- Whether a tag sits in EQUIPMENT vs SUB-EQUIPMENT (placement F1 is reported separately when available)

So **61.8%** means: of the tags that should belong under those parents, the model’s child-tag sets match GT at that F1 — not “61.8% of the whole drawing.”

---

## Output layout

```text
outputs/
  Broke System.hierarchy.csv
  Broke System.hierarchy_gt.csv
  Broke System.pid_inventory.xlsx
  Broke System.pid_enrichment.xlsx
  evidence/          # viewer PNGs
  jsons/             # all pipeline JSON + scores
  logs/              # run logs
  experiments/       # model × prompt sweep folders + leaderboard.json
```

---

## Accuracies — pilot equipment (`35-24L009` + `35-24P519`)

GT: `resources/gt_hierarchy_broke_system.xlsx`

### Best run (historical v4 dossier sweep; shipping default is now v8)

| Metric | Value |
|---|---|
| Model | `eu.anthropic.claude-sonnet-4-6` |
| Prompt | `pid_hierarchy_gt_v4_dossier.md` |
| **Micro tag F1** | **61.8%** |
| Macro tag F1 | 61.6% |
| Precision / Recall | 48.8% / 84.0% |
| TP / FP / FN | 21 / 22 / 4 |
| L009 tag F1 | **68.6%** (0 missing vs GT set) |
| P519 tag F1 | **54.5%** |

Evidence folder for that experiment:

`outputs/experiments/eu_anthropic_claude-sonnet-4-6__pid_hierarchy_gt_v4_dossier/`

### Prompt sweep (same model: Claude Sonnet 4.6)

Shows why **v4 dossier** won.

| Prompt | Micro tag F1 | Precision | Recall |
|---|---:|---:|---:|
| `pid_hierarchy_gt_v1.md` | 32.8% | 26% | 44% |
| `pid_hierarchy_gt_v2.md` | 27.7% | 23% | 36% |
| `pid_hierarchy_gt_v3_fewshot.md` | 38.2% | 30% | 52% |
| **`pid_hierarchy_gt_v4_dossier.md`** | **61.8%** | **49%** | **84%** |
| `pid_hierarchy_gt_v5_tight.md` | 46.4% | 36% | 64% |
| `pid_hierarchy_gt_v6_examples.md` | 54.8% | 46% | 68% |

Takeaway: dossier + candidates + ownership rules beat “tight” or “more examples alone.”

---

## Model comparison — same prompt (`v4 dossier`), pilot tags

All scored on **L009 + P519** GT. Sorted by micro tag F1.

| Rank | Model | Micro F1 | L009 F1 | P519 F1 | Notes |
|---:|---|---:|---:|---:|---|
| 1 | **Claude Sonnet 4.6** (`eu.anthropic.claude-sonnet-4-6`) | **61.8%** | 68.6% | 54.5% | **Winner / default** |
| 2 | OpenAI GPT-OSS 120B (`openai.gpt-oss-120b-1:0`) | 58.8% | 68.7% | 50.0% | Text-only (no image); dossier-driven |
| 3 | Qwen3 VL 235B (`qwen.qwen3-vl-235b-a22b`) | 58.3% | 60.0% | 56.2% | Strong vision vendor |
| 4 | Kimi K2.5 (`moonshotai.kimi-k2.5`) | 57.5% | 56.4% | 58.8% | Best P519 among vendors |
| 5 | Gemma 3 27B (`google.gemma-3-27b-it`) | 57.1% | 62.9% | 52.4% | |
| 6 | Magistral Small (`mistral.magistral-small-2509`) | 56.1% | 55.0% | 57.1% | High recall, more extras |
| 7 | Gemma 3 12B (`google.gemma-3-12b-it`) | 55.7% | 62.9% | 50.0% | |
| 8 | Ministral 3 14B (`mistral.ministral-3-14b-instruct`) | 55.6% | 61.1% | 50.0% | |
| 9 | Amazon Nova Pro (`amazon.nova-pro-v1:0`) | 54.1% | 59.5% | 50.0% | |
| 10 | Claude Opus 4.6 (`eu.anthropic.claude-opus-4-6-v1`) | 50.9% | 51.6% | 50.0% | Weaker than Sonnet 4.6 here |
| 11 | Claude Opus 4.5 | 50.0% | 50.0% | 50.0% | |
| 12 | Claude Sonnet 4.5 | 48.0% | 40.0% | 56.0% | |

**Claude Haiku 4.5** was in earlier prompt sweeps (v1–v3) and topped out ~**42%** — not competitive once v4 + stronger Sonnets arrived.

### Pattern across models

- **Recall is usually high** (often 80–92%) — models find many real children.  
- **Precision is the limiter** — extras from nearby peer equipment / shared lines.  
- **Sonnet 4.6 + v4** had the best precision/recall balance on this GT.  
- **GPT-OSS** is surprisingly close **without** vision (dossier carries a lot).

Reproduce vendor sweep:

```bash
make hierarchy-vendors TAGS=35-24L009,35-24P519
```

Artifacts: `outputs/experiments/<model>__pid_hierarchy_gt_v4_dossier/score.json`

---

## Follow-on equipment (`35-24L008` + `35-24P509`)

Same default combo (Sonnet 4.6 + v4 dossier), different GT:

| Metric | Value |
|---|---|
| GT file | `inputs/gt_hierarchy_L008_P509.csv` |
| Score file | `outputs/jsons/score_L008_P509.json` |
| **Micro tag F1** | **56.0%** |
| Precision / Recall | 42.9% / 80.8% |
| L008 (Winder Pulper) F1 | **66.7%** |
| P509 (pump) F1 | **44.4%** |

Same failure mode as pilot pump: **high recall, peer / cross-equipment bleed** lowers precision (especially under P509).

---

## Quick reproduce checklist

```bash
# Full CAD extract
make all

# Pilot hierarchy (scored combo)
make hierarchy-ai TAGS=35-24L009,35-24P519
make hierarchy-eval

# Follow-on pair
make hierarchy-ai TAGS=35-24L008,35-24P509
python3 eval_hierarchy_gt.py \
  --gt inputs/gt_hierarchy_L008_P509.csv \
  --pred "outputs/Broke System.hierarchy_gt.csv"

# Model × prompt / vendor sweeps
make hierarchy-experiments
make hierarchy-vendors
```

---

## One-slide story

1. **Dump → inventory → enrich** turns the DWG into structured tags, lines, and coordinates (no AI).  
2. **Hierarchy AI** crops a viewer screenshot, builds a CAD briefing pack, and asks Bedrock for GT-shaped children per machine.  
3. On the pilot sheet (**L009 / P519**), **Claude Sonnet 4.6 + dossier prompt** hits **61.8%** micro tag F1 — best among Anthropic + vendor models we tried.  
4. On **L008 / P509**, same stack scores **56%** — still useful, but precision needs work around peer pumps.
