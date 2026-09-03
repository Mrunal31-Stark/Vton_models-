"""Leffa-only eval server. Runs in /workspace/venv_leffa (diffusers 0.31) on :8001
because Leffa's vendored UNet needs a newer diffusers than IDM-VTON tolerates.

  POST /tryon  (multipart: model, category, tag, person, garment)
  -> {"image_b64": ..., "gpu_seconds": <float>}
"""
import base64
import io
import time
import traceback

import torch
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from models import leffa_runner

app = FastAPI()
_handle = None


@app.get("/health")
def health():
    return {"ok": True, "cuda": torch.cuda.is_available(), "loaded": _handle is not None}


@app.post("/tryon")
async def tryon(model: str = Form(...), category: str = Form(...), tag: str = Form(""),
                person: UploadFile = File(...), garment: UploadFile = File(...)):
    global _handle
    p_img = Image.open(io.BytesIO(await person.read())).convert("RGB")
    g_img = Image.open(io.BytesIO(await garment.read())).convert("RGB")
    try:
        if _handle is None:
            _handle = leffa_runner.load()
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        out = leffa_runner.infer(_handle, p_img, g_img, category, tag)
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
