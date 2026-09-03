"""Shared client for fal.ai hosted try-on endpoints.

fal responses don't include a dollar amount, so we attach an ESTIMATED per-image
price from the model card and reconcile against the fal billing dashboard in
COST_LEDGER.md after each session.
"""
import base64
import mimetypes
import os
import time

import fal_client
import requests

# estimated per-image USD, keyed by model key (see config.MODELS) — from the fal
# model cards (best-virtual-try-on-apis-2026).
EST_PRICE = {
    "flux-tryon-pro": 0.038,   # $0.0375 / MP, ~1 MP output
    "image-apps-v2": 0.040,
    "leffa": 0.100,            # fal price; self-host would be ~$0.003
    "kolors-fal": 0.070,
    "fashn-fal": 0.075,
}


def _data_uri(path: str) -> str:
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def _result_url(result: dict) -> str:
    # endpoints return either {"images": [{"url": ...}]} or {"image": {"url": ...}}
    if result.get("images"):
        first = result["images"][0]
        return first["url"] if isinstance(first, dict) else first
    img = result.get("image")
    if isinstance(img, dict):
        return img["url"]
    return img


def run(model_key: str, endpoint: str, arguments: dict, out_path: str) -> dict:
    assert os.getenv("FAL_KEY"), "FAL_KEY not set in .env"
    t0 = time.perf_counter()
    result = fal_client.subscribe(endpoint, arguments=arguments, with_logs=False)
    url = _result_url(result)
    with open(out_path, "wb") as f:
        f.write(requests.get(url, timeout=90).content)
    return {
        "cost_usd": EST_PRICE.get(model_key, 0.0),
        "gpu_seconds": None,          # hosted -> no GPU-seconds; wall time is the speed metric
        "wall_hint_sec": round(time.perf_counter() - t0, 2),
    }
