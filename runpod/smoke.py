"""Direct per-model smoke test on the pod (skips the HTTP server for clean tracebacks).

  python runpod/smoke.py catvton t-shirt
  python runpod/smoke.py idm-vton saree optimized
  python runpod/smoke.py leffa lehenga
"""
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from models import catvton_runner, idm_vton_runner, leffa_runner  # noqa: E402

RUNNERS = {"catvton": catvton_runner, "idm-vton": idm_vton_runner, "leffa": leffa_runner}
APP = Path("/workspace/app")
PERSONS = {"female": APP / "assets/persons/female.jpg", "male": APP / "assets/persons/male.jpg"}
FEMALE = {"saree", "kurti", "lehenga", "top", "jumpsuit"}


def main():
    model = sys.argv[1]
    category = sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 else ""

    person = Image.open(PERSONS["female" if category in FEMALE else "male"]).convert("RGB")
    garment = Image.open(APP / f"assets/garments/{category}.jpg").convert("RGB")

    r = RUNNERS[model]
    print(f"loading {model} ...")
    t0 = time.perf_counter()
    handle = r.load()
    print(f"  loaded in {time.perf_counter()-t0:.1f}s")

    print(f"infer {model} / {category} / tag={tag or '(baseline)'} ...")
    t0 = time.perf_counter()
    out = r.infer(handle, person, garment, category, tag)
    dt = time.perf_counter() - t0
    outp = APP / f"results/outputs/{model}__{category}{('__' + tag) if tag else ''}.png"
    outp.parent.mkdir(parents=True, exist_ok=True)
    out.save(outp)
    print(f"  OK {dt:.1f}s -> {outp}")


if __name__ == "__main__":
    main()
