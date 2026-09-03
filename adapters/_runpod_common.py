"""Shared client for the open-source models served by runpod/server.py.

The pod exposes ONE endpoint:  POST {RUNPOD_TRYON_URL}/tryon
  multipart form: model, category, person (file), garment (file)
  -> {"image_b64": "...", "gpu_seconds": 8.1}

Cost is GPU time, not a per-call price, so we convert:
  cost_usd = gpu_seconds/3600 * GPU_HOURLY_USD
Set GPU_HOURLY_USD to the pod's actual rate (RunPod shows it per pod).
"""
import base64
import os

import requests

GPU_HOURLY_USD = float(os.getenv("RUNPOD_GPU_HOURLY_USD", "0.69"))  # RTX 4090 community default
_TIMEOUT = 360


def call(model: str, person_path: str, garment_path: str, category: str,
         out_path: str, tag: str = "") -> dict:
    base = os.environ["RUNPOD_TRYON_URL"].rstrip("/")
    with open(person_path, "rb") as pf, open(garment_path, "rb") as gf:
        resp = requests.post(
            f"{base}/tryon",
            data={"model": model, "category": category, "tag": tag},
            files={"person": pf, "garment": gf},
            timeout=_TIMEOUT,
        )
    resp.raise_for_status()
    payload = resp.json()
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(payload["image_b64"]))
    gpu_s = float(payload.get("gpu_seconds", 0.0))
    return {"cost_usd": gpu_s / 3600.0 * GPU_HOURLY_USD, "gpu_seconds": gpu_s}
