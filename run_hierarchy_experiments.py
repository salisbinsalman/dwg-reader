#!/usr/bin/env python3
"""Try model × prompt combinations until GT accuracy >= target."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from eval_hierarchy_gt import evaluate, load_gt_rows, rows_from_hierarchy_csv
from dwg_pure_dump import json_path, jsons_dir, logs_dir

ROOT = Path(__file__).resolve().parent

DEFAULT_MODELS = [
    "eu.anthropic.claude-sonnet-4-6",
]

# Multi-vendor vision sweep (Gemini / GPT-4o not on this Bedrock account)
VENDOR_SWEEP_MODELS = [
    "moonshotai.kimi-k2.5",                 # Kimi (Moonshot) vision
    "mistral.ministral-3-14b-instruct",     # Mistral vision
    "mistral.magistral-small-2509",         # Mistral vision
    "google.gemma-3-27b-it",                # Google Gemma vision (not Gemini)
    "google.gemma-3-12b-it",
    "amazon.nova-pro-v1:0",                 # Amazon Nova vision
    "qwen.qwen3-vl-235b-a22b",              # Qwen VL
    "openai.gpt-oss-120b-1:0",              # OpenAI OSS text-only (dossier fallback)
]

DEFAULT_PROMPTS = [
    "pid_hierarchy_gt_v4_dossier.md",
]


def run_one(
    *,
    model_id: str,
    prompt_file: str,
    input_dwg: str,
    out_dir: Path,
    tags: str,
    region: str,
    reuse_shots: bool,
) -> Dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / "dwg_pid_hierarchy_ai.py"),
        "--input",
        input_dwg,
        "--output-dir",
        str(out_dir),
        "--tags",
        tags,
        "--model-id",
        model_id,
        "--region",
        region,
        "--prompt-file",
        prompt_file,
        "--no-clean-prev",
    ]
    if reuse_shots:
        cmd.append("--reuse-shots")

    env = os.environ.copy()
    print(f"\n===== RUN model={model_id} prompt={prompt_file} =====")
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=False)
    pred_path = out_dir / "Broke System.hierarchy.csv"
    result: Dict[str, Any] = {
        "model_id": model_id,
        "prompt_file": prompt_file,
        "returncode": proc.returncode,
        "pred_path": str(pred_path),
    }
    if proc.returncode != 0 or not pred_path.exists():
        result["accuracy"] = 0.0
        result["error"] = "run_failed_or_missing_pred"
        return result

    # Archive this combo's outputs
    slug = (
        model_id.replace("/", "_").replace(":", "_").replace(".", "_")
        + "__"
        + prompt_file.replace(".md", "")
    )
    archive = out_dir / "experiments" / slug
    archive.mkdir(parents=True, exist_ok=True)
    for name in ("Broke System.hierarchy.csv",):
        src = out_dir / name
        if src.exists():
            (archive / name).write_bytes(src.read_bytes())
    ai_json = json_path(out_dir, "Broke System.hierarchy_ai.json")
    if ai_json.exists():
        (archive / ai_json.name).write_bytes(ai_json.read_bytes())

    gt_rows = load_gt_rows(ROOT / "inputs" / "gt_hierarchy_broke_system.csv")
    pred_rows = rows_from_hierarchy_csv(pred_path)
    report = evaluate(pred_rows, gt_rows)
    result["accuracy"] = report["accuracy"]
    result["micro_tag_f1"] = report["micro_tag_f1"]
    result["macro_tag_f1"] = report["macro_tag_f1"]
    result["micro"] = report["micro"]
    result["per_function"] = {
        k: {
            "tag_f1": v["tag_f1"]["f1"],
            "missing": v["missing"],
            "extra": v["extra"][:12],
        }
        for k, v in report["per_function"].items()
    }
    score_path = json_path(out_dir, f"score__{slug}.json")
    # Keep per-run score next to archive and also under jsons/
    (archive / "score.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    score_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"SCORE {result['accuracy']*100:.1f}%  "
        f"(P={report['micro']['precision']*100:.1f} R={report['micro']['recall']*100:.1f})"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--tags", default="35-24L009,35-24P519")
    parser.add_argument("--region", default=os.environ.get("AWS_REGION") or "eu-west-2")
    parser.add_argument("--target", type=float, default=0.60)
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--prompts", default=",".join(DEFAULT_PROMPTS))
    parser.add_argument(
        "--vendor-sweep",
        action="store_true",
        help="Sweep Kimi/Mistral/Gemma/Nova/Qwen/OpenAI-OSS (ignores --models default)",
    )
    parser.add_argument(
        "--no-early-stop",
        action="store_true",
        help="Run all combos even after hitting --target",
    )
    parser.add_argument(
        "--prepare-shots",
        action="store_true",
        help="Render viewer shots once before the sweep",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = logs_dir(out_dir)
    jsons_dir(out_dir)
    if args.vendor_sweep:
        models = list(VENDOR_SWEEP_MODELS)
    else:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    prompts = [p.strip() for p in args.prompts.split(",") if p.strip()]

    if args.prepare_shots or not (out_dir / "evidence" / "Broke System.viewer_35-24L009.png").exists():
        prep = [
            sys.executable,
            str(ROOT / "dwg_pid_hierarchy_ai.py"),
            "--input",
            args.input,
            "--output-dir",
            str(out_dir),
            "--tags",
            args.tags,
            "--shots-only",
        ]
        print("Preparing viewer shots...")
        subprocess.run(prep, cwd=str(ROOT), check=False)

    leaderboard: List[Dict[str, Any]] = []
    best: Dict[str, Any] = {"accuracy": -1.0}

    for prompt in prompts:
        for model in models:
            row = run_one(
                model_id=model,
                prompt_file=prompt,
                input_dwg=args.input,
                out_dir=out_dir,
                tags=args.tags,
                region=args.region,
                reuse_shots=True,
            )
            leaderboard.append(row)
            if row.get("accuracy", 0) > best.get("accuracy", -1):
                best = row
            if row.get("accuracy", 0) >= args.target and not args.no_early_stop:
                print(f"\nTARGET MET: {row['accuracy']*100:.1f}% with {model} / {prompt}")
                summary = {"target": args.target, "best": best, "leaderboard": leaderboard, "stopped_early": True}
                board = json_path(out_dir, "leaderboard.json")
                board.write_text(json.dumps(summary, indent=2), encoding="utf-8")
                (out_dir / "experiments" / "leaderboard.json").write_text(
                    json.dumps(summary, indent=2), encoding="utf-8"
                )
                print(json.dumps(summary, indent=2))
                return 0

    summary = {"target": args.target, "best": best, "leaderboard": leaderboard, "stopped_early": False}
    board = json_path(out_dir, "leaderboard.json")
    board.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "experiments" / "leaderboard.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n===== LEADERBOARD =====")
    for row in sorted(leaderboard, key=lambda r: r.get("accuracy", 0), reverse=True):
        print(
            f"{row.get('accuracy', 0)*100:5.1f}%  {row.get('model_id')}  {row.get('prompt_file')}  "
            f"{row.get('error', '')}"
        )
    print(f"\nBest: {best.get('accuracy', 0)*100:.1f}%")
    print(f"Leaderboard JSON: {board}")
    print(f"Logs dir: {log_dir}")
    return 0 if best.get("accuracy", 0) >= args.target else 1


if __name__ == "__main__":
    raise SystemExit(main())
