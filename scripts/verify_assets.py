"""Contact sheet of the downloaded test set so you can eyeball it before testing.

  python scripts/verify_assets.py        -> writes assets/_contact_sheet.png + prints a report

Checks: file present, opens, portrait-ish, min resolution. Flags anything off.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config  # noqa: E402
MIN_W, MIN_H = 384, 512
THUMB = (256, 341)


def check(p: Path):
    if not p.exists():
        return None, "MISSING"
    try:
        im = Image.open(p).convert("RGB")
    except Exception as e:  # noqa: BLE001
        return None, f"UNOPENABLE ({e})"
    w, h = im.size
    flags = []
    if w < MIN_W or h < MIN_H:
        flags.append(f"low-res {w}x{h}")
    if h < w:
        flags.append("landscape (want portrait)")
    return im, ", ".join(flags) or "ok"


def main():
    items = [("person", k, Path(ROOT, v)) for k, v in config.PERSON_IMAGES.items()]
    items += [("garment", c, Path(ROOT, config.garment_path(c))) for c in config.CATEGORIES]

    cols = 6
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * THUMB[0], rows * (THUMB[1] + 22)), "white")
    d = ImageDraw.Draw(sheet)

    print(f"{'kind':8} {'name':10} {'status'}")
    bad = 0
    for i, (kind, name, path) in enumerate(items):
        im, status = check(path)
        if status not in ("ok",):
            bad += 1
        print(f"{kind:8} {name:10} {status}")
        x, y = (i % cols) * THUMB[0], (i // cols) * (THUMB[1] + 22)
        if im:
            im.thumbnail(THUMB)
            sheet.paste(im, (x, y + 22))
        d.text((x + 2, y + 4), f"{name} [{status}]", fill="black")

    out = ROOT / "assets/_contact_sheet.png"
    sheet.save(out)
    print(f"\ncontact sheet -> {out}")
    print("ALL GOOD" if bad == 0 else f"{bad} item(s) need attention")


if __name__ == "__main__":
    main()
