"""Merge results/log.csv (timings/cost) + results/scores.csv (1-5 rubric)
into results/comparison.md.

  python scripts/build_comparison.py

scores.csv notes may contain commas -> we parse with the csv module (not pandas)
and treat everything past column 9 as the note.
"""
import csv
import statistics
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"
SPEED_CAP, COST_CAP = 15.0, 4.0
AXES = ["fit", "drape", "texture_fidelity", "artifacts_inv", "face_body_preservation"]


def load_log():
    out = {}
    for row in csv.DictReader(open(R / "log.csv", encoding="utf-8")):
        if row.get("error"):
            continue
        out[(row["model"], row["category"], row["tag"])] = {
            "gen": float(row["gen_time_sec"]), "inr": float(row["cost_inr"]),
        }
    return out


def load_scores():
    out = {}
    with open(R / "scores.csv", encoding="utf-8") as f:
        for parts in csv.reader(f):
            if not parts or parts[0].startswith(("model", "#")):
                continue
            model, cat, tag = parts[0], parts[1], parts[2]
            vals = [int(x) for x in parts[3:8]]
            note = ",".join(parts[9:]) if len(parts) > 9 else ""
            out[(model, cat, tag)] = {"axes": dict(zip(AXES, vals)),
                                      "mean": round(statistics.mean(vals), 2), "note": note}
    return out


def main():
    log, sc = load_log(), load_scores()
    keys = sorted(set(log) | set(sc), key=lambda k: (k[0], k[2], k[1]))

    lines = ["# VTON model comparison\n",
             f"Gates: generation < {SPEED_CAP:.0f} s  &  cost < Rs {COST_CAP:.0f} per image.  "
             "All tested models clear both by a wide margin — so the decision is **accuracy**.\n",
             "| model | category | variant | gen s | Rs/img | fit | drape | texture | artifact-free | identity | mean | pass |",
             "|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|:--:|"]
    for k in keys:
        m, c, tag = k
        lg, s = log.get(k, {}), sc.get(k, {})
        ax = s.get("axes", {})
        row = [m, c, tag or "baseline",
               f"{lg.get('gen', float('nan')):.1f}" if lg else "-",
               f"{lg.get('inr', float('nan')):.2f}" if lg else "-",
               *[str(ax.get(a, "-")) for a in AXES],
               f"{s.get('mean', '-')}",
               "OK" if lg and lg["gen"] < SPEED_CAP and lg["inr"] < COST_CAP else "-"]
        lines.append("| " + " | ".join(row) + " |")

    # per-model / per-variant rollup
    lines += ["\n## Rollup (mean accuracy)\n",
              "| model / variant | categories | mean accuracy | worst category |",
              "|---|--:|--:|---|"]
    groups = {}
    for k, s in sc.items():
        groups.setdefault((k[0], k[2] or "baseline"), []).append((k[1], s["mean"]))
    for (m, tag), items in sorted(groups.items()):
        means = [v for _, v in items]
        worst = min(items, key=lambda t: t[1])
        lines.append(f"| {m} ({tag}) | {len(items)} | {statistics.mean(means):.2f} "
                     f"| {worst[0]} ({worst[1]}) |")

    # preserve any hand-written section below the marker
    MARK = "<!-- MANUAL BELOW -->"
    tail = ""
    md_path = R / "comparison.md"
    if md_path.exists() and MARK in md_path.read_text(encoding="utf-8"):
        tail = "\n" + MARK + md_path.read_text(encoding="utf-8").split(MARK, 1)[1]
    else:
        tail = "\n" + MARK + "\n(add per-category winners + recommendation here; kept across rebuilds)\n"

    md_path.write_text("\n".join(lines) + "\n" + tail, encoding="utf-8")
    print("wrote", md_path)


if __name__ == "__main__":
    main()
