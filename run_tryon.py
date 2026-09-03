"""Bare-bones VTON evaluation harness.

Usage:
  python run_tryon.py --model idm-vton --category saree
  python run_tryon.py --model all --category all          # full 5x10 matrix
  python run_tryon.py --model idm-vton --category saree,kurti --tag optimized

Every run:
  - feeds the SAME person image + garment image per category to each model
  - times the generation
  - computes cost in USD and INR
  - writes a row to results/log.csv
  - saves the output image to results/outputs/<model>__<category>[__<tag>].png
"""
import argparse
import csv
import importlib
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

import config

load_dotenv()

LOG = Path("results/log.csv")
OUT_DIR = Path("results/outputs")
LOG_FIELDS = [
    "timestamp", "model", "category", "tag", "person", "garment",
    "gen_time_sec", "wall_sec", "cost_usd", "cost_inr", "within_speed", "within_cost",
    "output_path", "error",
]


def _adapter(model_key: str):
    spec = config.MODELS[model_key]
    mod = importlib.import_module(f"adapters.{spec['adapter']}")
    return mod, spec


def _append_log(row: dict):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def run_one(model_key: str, category: str, tag: str = "") -> dict:
    person_key = config.CATEGORIES[category]
    person = config.PERSON_IMAGES[person_key]
    garment = config.garment_path(category)
    mod, spec = _adapter(model_key)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{model_key}__{category}" + (f"__{tag}" if tag else "")
    out_path = OUT_DIR / f"{stem}.png"

    row = {k: "" for k in LOG_FIELDS}
    row.update({
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model_key, "category": category, "tag": tag,
        "person": person, "garment": garment, "output_path": str(out_path),
    })

    try:
        t0 = time.perf_counter()
        result = mod.generate(
            person_path=person, garment_path=garment,
            category=category, out_path=str(out_path), spec=spec, tag=tag,
        )
        wall = time.perf_counter() - t0
        # For self-hosted models the wall time includes base64 transfer through the
        # RunPod proxy; the model's true generation time is the server's gpu_seconds.
        # A production deployment calls the GPU directly, so gpu_seconds is the fair
        # speed number. fal adapters don't report it -> fall back to wall time.
        gen = float(result.get("gpu_seconds") or wall)
        cost_usd = float(result.get("cost_usd", 0.0))
        row.update({
            "gen_time_sec": round(gen, 2),
            "wall_sec": round(wall, 2),
            "cost_usd": round(cost_usd, 5),
            "cost_inr": round(cost_usd / config.USD_PER_INR, 3),
            "within_speed": gen < config.SPEED_CAP_SEC,
            "within_cost": (cost_usd / config.USD_PER_INR) < config.INR_COST_CAP,
        })
        print(f"  OK  {model_key:16} {category:10} {gen:5.1f}s (wall {wall:4.0f}s)  "
              f"Rs{row['cost_inr']:.2f}  -> {out_path}")
    except Exception as e:  # noqa: BLE001 - harness must not die mid-matrix
        row["error"] = repr(e)
        print(f"  ERR {model_key:16} {category:10} {e!r}")

    _append_log(row)
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True,
                   help="model key, comma list, or 'all'")
    p.add_argument("--category", required=True,
                   help="category, comma list, or 'all'")
    p.add_argument("--tag", default="", help="label for this run, e.g. 'optimized'")
    a = p.parse_args()

    models = list(config.MODELS) if a.model == "all" else a.model.split(",")
    cats = list(config.CATEGORIES) if a.category == "all" else a.category.split(",")

    spent = 0.0
    for m in models:
        for c in cats:
            r = run_one(m.strip(), c.strip(), a.tag.strip())
            spent += float(r.get("cost_usd") or 0.0)
            if spent >= config.BUDGET_CAP_USD:
                print(f"\n!! BUDGET CAP ${config.BUDGET_CAP_USD} reached "
                      f"(spent ${spent:.2f} this run). Stopping.")
                return
    print(f"\nDone. Approx spend this run: ${spent:.2f}")


if __name__ == "__main__":
    main()
