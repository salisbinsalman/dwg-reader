PYTHON ?= python3
SCRIPT ?= dwg_pure_dump.py
INPUT ?= inputs/Broke\ System.dwg
OUT ?= outputs

# Best hierarchy combo from GT sweep (~61.8% micro tag F1)
MODEL_ID ?= eu.anthropic.claude-sonnet-4-6
PROMPT_FILE ?= pid_hierarchy_gt_v7_floc.md
AWS_REGION ?= eu-west-2
AWS_PROFILE ?= foundrydev
TAGS ?= 35-24L009,35-24P519
LIMIT ?= 10
JOBS ?= 1
SKIP_EXISTING ?=
# Empty = all inventory FUNCTION kinds (equipment + instrument + line).
KINDS ?=

.PHONY: help check-odafc run run-json run-json-splits semantic semantic-run inventory inventory-run enrich hierarchy hierarchy-cad hierarchy-ai hierarchy-orch hierarchy-orch-dry floc equipment sap floc-test equipment-test valve-classify valve-test hierarchy-experiments hierarchy-vendors hierarchy-eval all all-prep full forensic structural structural-aspose clean-prev clean-outputs abbreviations-json

help:
	@echo "Targets:"
	@echo "  make check-odafc            # verify ODA File Converter visibility"
	@echo "  make run                    # full dump -> Excel workbook"
	@echo "  make run-json               # dump + JSON structural cache"
	@echo "  make inventory              # P&ID inventory workbook"
	@echo "  make enrich                 # tags/line-binding/loops/tables enrichment"
	@echo "  make hierarchy              # CAD connectivity hierarchy + local DWG crops"
	@echo "  make hierarchy-ai           # viewer shots + Bedrock hierarchy (best model/prompt)"
	@echo "  make hierarchy-orch         # inventory FUNCTIONs → hierarchy vs GT (LIMIT=$(LIMIT), JOBS=$(JOBS))"
	@echo "  make hierarchy-orch-dry     # list first LIMIT inventory FUNCTIONs + GT child counts"
	@echo "  make floc                   # hierarchy CSV → SAP Functional Location xlsx"
	@echo "  make equipment              # hierarchy CSV → SAP Equipment xlsx"
	@echo "  make valve-classify         # tight per-valve crop + legend → valve_types.json"
	@echo "  make sap                    # both SAP templates (floc + equipment)"
	@echo "  make floc-test              # unit tests for FLOC path/export (no Bedrock)"
	@echo "  make equipment-test         # unit tests for Equipment export (no Bedrock)"
	@echo "  make valve-test             # unit tests for per-tag valve locate/parent/type"
	@echo "  make abbreviations-json     # rebuild inputs/sml_abbreviations.json from SML xlsx"
	@echo "  make hierarchy-experiments  # sweep models/prompts vs GT"
	@echo "  make hierarchy-vendors      # Kimi/Mistral/Gemma/Nova/Qwen/OpenAI-OSS sweep"
	@echo "  make hierarchy-eval         # score outputs/*hierarchy_orchestrator.csv vs GT"
	@echo "  make hierarchy-vision       # CAD hierarchy + Bedrock confirm/reject only"
	@echo "  make all                    # FULL: dump→inventory→enrich→hierarchy-orch→FLOC+Equipment (LIMIT=$(LIMIT))"
	@echo "  make all-prep               # dump→inventory→enrich only (no Bedrock)"
	@echo "  make clean-prev             # remove prior outputs for INPUT stem only"
	@echo "  make clean-outputs          # remove generated outputs"
	@echo ""
	@echo "Layout: Excel/CSV in outputs/; images in outputs/evidence/;"
	@echo "        JSON in outputs/jsons/; logs in outputs/logs/"
	@echo "Best hierarchy: MODEL_ID=$(MODEL_ID)"
	@echo "                PROMPT_FILE=$(PROMPT_FILE)"
	@echo "LIMIT=$(LIMIT)  (hierarchy + FLOC + Equipment; 0 = all inventory FUNCTIONs)"
	@echo "JOBS=$(JOBS)    (orchestrator parallel workers; 1 = sequential)"
	@echo "KINDS=$(KINDS)  (empty = all kinds; e.g. KINDS=equipment)"
	@echo "Example:        make all LIMIT=10"
	@echo "                make all LIMIT=0   # full drawing, all 177 FUNCTIONs"
	@echo "                make sap LIMIT=10  # regenerate both SAP workbooks only"

check-odafc:
	@$(PYTHON) -c 'import dwg_pure_dump as d; p=d.configure_odafc(); from ezdxf.addons import odafc; print("odafc_installed:", odafc.is_installed()); print("odafc_path:", p or getattr(odafc, "unix_exec_path", None))'

run:
	$(PYTHON) "$(SCRIPT)" --input "$(INPUT)" --output-dir "$(OUT)"

run-json:
	$(PYTHON) "$(SCRIPT)" --input "$(INPUT)" --output-dir "$(OUT)" --write-json

run-json-splits:
	$(PYTHON) "$(SCRIPT)" --input "$(INPUT)" --output-dir "$(OUT)" --write-json-splits

semantic:
	$(PYTHON) dwg_semantic_extract.py --input "$(INPUT)" --output-dir "$(OUT)"

semantic-run: run semantic

inventory:
	$(PYTHON) dwg_pid_inventory.py --input "$(INPUT)" --output-dir "$(OUT)"

inventory-run: run inventory

enrich:
	$(PYTHON) dwg_pid_enrich.py --input "$(INPUT)" --output-dir "$(OUT)"

hierarchy:
	AWS_PROFILE="$(AWS_PROFILE)" $(PYTHON) dwg_pid_hierarchy_vision.py --input "$(INPUT)" --output-dir "$(OUT)" --tags "$(TAGS)" --model-id "$(MODEL_ID)" --region "$(AWS_REGION)"

hierarchy-ai:
	@mkdir -p "$(OUT)/logs"
	AWS_PROFILE="$(AWS_PROFILE)" $(PYTHON) dwg_pid_hierarchy_ai.py --input "$(INPUT)" --output-dir "$(OUT)" --tags "$(TAGS)" --model-id "$(MODEL_ID)" --region "$(AWS_REGION)" --prompt-file "$(PROMPT_FILE)" 2>&1 | tee "$(OUT)/logs/hierarchy-ai.log"

hierarchy-orch-dry:
	$(PYTHON) run_hierarchy_orchestrator.py --input "$(INPUT)" --output-dir "$(OUT)" --limit $(LIMIT) $(if $(KINDS),--kinds "$(KINDS)",) --dry-run

hierarchy-orch:
	@mkdir -p "$(OUT)/logs"
	AWS_PROFILE="$(AWS_PROFILE)" PYTHONUNBUFFERED=1 $(PYTHON) run_hierarchy_orchestrator.py --input "$(INPUT)" --output-dir "$(OUT)" --limit $(LIMIT) --jobs $(JOBS) $(if $(KINDS),--kinds "$(KINDS)",) --model-id "$(MODEL_ID)" --region "$(AWS_REGION)" --prompt-file "$(PROMPT_FILE)" --aws-profile "$(AWS_PROFILE)" $(if $(SKIP_EXISTING),--skip-existing,) 2>&1 | tee "$(OUT)/logs/hierarchy-orchestrator.log"

floc:
	$(PYTHON) export_sap_floc.py --input "$(INPUT)" --output-dir "$(OUT)" --limit $(LIMIT)

equipment:
	$(PYTHON) export_sap_equipment.py --input "$(INPUT)" --output-dir "$(OUT)" --limit $(LIMIT)

valve-classify:
	@mkdir -p "$(OUT)/logs"
	AWS_PROFILE="$(AWS_PROFILE)" PYTHONUNBUFFERED=1 $(PYTHON) dwg_valve_classify.py --input "$(INPUT)" --output-dir "$(OUT)" --model-id "$(MODEL_ID)" --region "$(AWS_REGION)" --jobs $(JOBS) $(if $(SKIP_EXISTING),--skip-existing,) 2>&1 | tee "$(OUT)/logs/valve-classify.log"

sap: floc equipment

floc-test:
	$(PYTHON) -m unittest test_floc_export.py -v

abbreviations-json:
	$(PYTHON) scripts/build_sml_abbreviations_json.py

equipment-test:
	$(PYTHON) -m unittest test_equipment_export.py -v

valve-test:
	$(PYTHON) -m unittest test_valve_classify.py test_sit_valve_classification.py -v

hierarchy-experiments:
	@mkdir -p "$(OUT)/logs"
	AWS_PROFILE="$(AWS_PROFILE)" $(PYTHON) run_hierarchy_experiments.py --input "$(INPUT)" --output-dir "$(OUT)" --tags "$(TAGS)" --region "$(AWS_REGION)" --prepare-shots 2>&1 | tee "$(OUT)/logs/hierarchy-experiments.log"

hierarchy-vendors:
	@mkdir -p "$(OUT)/logs"
	AWS_PROFILE="$(AWS_PROFILE)" $(PYTHON) run_hierarchy_experiments.py --input "$(INPUT)" --output-dir "$(OUT)" --tags "$(TAGS)" --region "$(AWS_REGION)" --vendor-sweep --no-early-stop --prompts "$(PROMPT_FILE)" 2>&1 | tee "$(OUT)/logs/hierarchy-vendors.log"

hierarchy-eval:
	$(PYTHON) eval_hierarchy_gt.py --gt inputs/gt_hierarchy_broke_system.xlsx --pred "$(OUT)/Broke System.hierarchy_orchestrator.csv"

hierarchy-vision:
	AWS_PROFILE="$(AWS_PROFILE)" $(PYTHON) dwg_pid_hierarchy_vision.py --input "$(INPUT)" --output-dir "$(OUT)" --tags "$(TAGS)" --model-id "$(MODEL_ID)" --region "$(AWS_REGION)" --vision-confirm

hierarchy-cad: hierarchy

# CAD-only prep (no Bedrock / FLOC).
all-prep: run-json inventory enrich

# End-to-end: dump → inventory → enrich → hierarchy (LIMIT) → FLOC + Equipment.
all: all-prep hierarchy-orch

full: all

forensic:
	$(PYTHON) "$(SCRIPT)" --input "$(INPUT)" --output-dir "$(OUT)" --skip-structural

structural:
	$(PYTHON) "$(SCRIPT)" --input "$(INPUT)" --output-dir "$(OUT)" --skip-forensic --write-json

structural-aspose:
	$(PYTHON) "$(SCRIPT)" --input "$(INPUT)" --output-dir "$(OUT)" --skip-forensic --enable-aspose-fallback --write-json

clean-prev:
	@$(PYTHON) -c 'from pathlib import Path; from dwg_pure_dump import clear_previous_outputs, safe_name; import sys; inp=Path(sys.argv[1]).expanduser(); out=Path(sys.argv[2]).expanduser(); clear_previous_outputs(out, safe_name(inp))' "$(INPUT)" "$(OUT)"

clean-outputs:
	rm -f "$(OUT)"/*.xlsx
	rm -f "$(OUT)"/*.csv
	rm -f "$(OUT)"/*.png
	rm -f "$(OUT)"/evidence/*.png
	rm -f "$(OUT)"/*.json
	rm -f "$(OUT)"/jsons/*.json
	rm -f "$(OUT)"/logs/*.log
	rm -f "$(OUT)"/evidence/_valve_crops/*.png
	rm -f "$(OUT)"/evidence/_valve_crops/*.meta.json
	rm -f "$(OUT)"/jsons/_orchestrator_parts/*.csv
	rm -f "$(OUT)"/jsons/_orchestrator_parts/*.json
	@echo "Cleared Excel, CSV, evidence, jsons/, logs/, valve crops, and orchestrator parts under $(OUT)/"
