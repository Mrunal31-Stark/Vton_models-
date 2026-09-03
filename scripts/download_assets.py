"""Fetch the frozen test set from assets/sources.json.

  python scripts/download_assets.py

Skips entries with an empty URL and reports them so you know what's still
missing. Re-run any time after editing sources.json.
"""
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "assets/sources.json").read_text())
UA = {"User-Agent": "Mozilla/5.0 (vizzle-vton-eval)"}


def fetch(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"  ok   {dest.relative_to(ROOT)}  ({len(r.content)//1024} KB)")


def main():
    missing = []
    for group, ext in (("persons", "jpg"), ("garments", "jpg")):
        for name, url in SRC[group].items():
            if name.startswith("_"):
                continue
            if not url or not url.startswith("http"):
                # empty, or a "MANUAL: ..." note -> file is expected to be placed by hand
                dest = ROOT / "assets" / group / f"{name}.{ext}"
                if dest.exists():
                    print(f"  keep {dest.relative_to(ROOT)}  (manually provided)")
                else:
                    missing.append(f"{group}/{name}  (manual - not found)")
                continue
            try:
                fetch(url, ROOT / "assets" / group / f"{name}.{ext}")
            except Exception as e:  # noqa: BLE001
                print(f"  FAIL {group}/{name}: {e}")
                missing.append(f"{group}/{name}")
    if missing:
        print("\nStill missing (add URLs to assets/sources.json):")
        for m in missing:
            print("  -", m)
    else:
        print("\nAll assets present.")


if __name__ == "__main__":
    main()
