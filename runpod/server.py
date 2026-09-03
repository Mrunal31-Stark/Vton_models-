"""Eval server for the open-source try-on models. Runs on the RunPod pod.

  POST /tryon   (multipart: model, category, tag, person, garment)
  -> {"image_b64": ..., "gpu_seconds": <float>}

Models are lazy-loaded on first use so the pod boots fast and only pays VRAM
for what you actually test. `tag` == "optimized" turns on the category-aware
masking / prompt / param path in the IDM-VTON runner (baseline otherwise).
"""
import base64
import io
import time
import traceback

import torch
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from models import catvton_runner, idm_vton_runner

RUNNERS = {
    "idm-vton": idm_vton_runner,
    "catvton": catvton_runner,
}
try:                                   # Leffa self-host is blocked by a diffusers
    from models import leffa_runner     # version conflict with IDM-VTON; tested via
    RUNNERS["leffa"] = leffa_runner     # fal instead. Keep it optional here.
except Exception:  # noqa: BLE001
    pass
_loaded = {}

app = FastAPI()


def _get(model: str):
    if model not in _loaded:
        _loaded[model] = RUNNERS[model].load()
    return _loaded[model]


@app.get("/health")
def health():
    return {"ok": True, "cuda": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "loaded": list(_loaded)}


@app.post("/tryon")
async def tryon(
    model: str = Form(...),
    category: str = Form(...),
    tag: str = Form(""),
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
):
    p_img = Image.open(io.BytesIO(await person.read())).convert("RGB")
    g_img = Image.open(io.BytesIO(await garment.read())).convert("RGB")

    try:
        handle = _get(model)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        out = RUNNERS[model].infer(handle, p_img, g_img, category, tag)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        gpu_seconds = time.perf_counter() - t0
    except Exception as e:  # noqa: BLE001
        return JSONResponse(status_code=500,
                            content={"error": repr(e), "trace": traceback.format_exc()})

    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return {"image_b64": base64.b64encode(buf.getvalue()).decode(),
            "gpu_seconds": round(gpu_seconds, 3)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
