"""Bare-bones try-on UI - ONLY exists so the screen recording shows the required
user flow: upload person -> upload garment -> pick category + model -> see result.
No styling effort (assignment: "keep it bare-bones").

Talks to the self-hosted eval server on the RunPod pod (RUNPOD_TRYON_URL).
Serves idm-vton + catvton from the main server; leffa needs its own server so it
is only offered when RUNPOD_LEFFA_URL is set.
"""
import base64
import io
import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()
app = Flask(__name__)

CATEGORIES = ["saree", "kurti", "lehenga", "top", "jumpsuit",
              "t-shirt", "shirt", "coat", "jeans", "trousers"]
MODELS = ["idm-vton", "catvton"] + (["leffa"] if os.getenv("RUNPOD_LEFFA_URL") else [])


def _run(model, person_bytes, garment_bytes, category, optimized):
    base = (os.environ["RUNPOD_LEFFA_URL"] if model == "leffa"
            else os.environ["RUNPOD_TRYON_URL"]).rstrip("/")
    t0 = time.perf_counter()
    r = requests.post(
        f"{base}/tryon",
        data={"model": model, "category": category,
              "tag": "optimized" if optimized else ""},
        files={"person": ("p.jpg", io.BytesIO(person_bytes)),
               "garment": ("g.jpg", io.BytesIO(garment_bytes))},
        timeout=360,
    )
    r.raise_for_status()
    j = r.json()
    return j["image_b64"], round(j.get("gpu_seconds", time.perf_counter() - t0), 1)


@app.route("/", methods=["GET", "POST"])
def index():
    ctx = {"models": MODELS, "categories": CATEGORIES}
    if request.method == "POST":
        p = request.files["person"].read()
        g = request.files["garment"].read()
        try:
            img_b64, secs = _run(request.form["model"], p, g,
                                 request.form["category"],
                                 request.form.get("optimized") == "on")
            ctx.update(result=img_b64, secs=secs,
                       model=request.form["model"], category=request.form["category"],
                       optimized=request.form.get("optimized") == "on")
        except Exception as e:  # noqa: BLE001
            ctx["error"] = repr(e)
    return render_template("index.html", **ctx)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
