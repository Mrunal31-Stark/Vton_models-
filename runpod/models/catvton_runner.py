"""CatVTON runner (Zheng-Chong/CatVTON).

Adapted from the repo's app.py. CatVTON is a single lightweight inpainting
pipeline; garment type drives the agnostic mask ("upper" | "lower" | "overall").
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from .common import CATEGORY_TO_PART

REPO = Path("/workspace/repos/CatVTON")
CKPT = Path("/workspace/ckpts/CatVTON")
BASE = "booksforcharlie/stable-diffusion-inpainting"  # repo default base_model_path

W, H = 768, 1024
_MAP = {"upper_body": "upper", "lower_body": "lower", "dresses": "overall"}


def load():
    # If IDM-VTON was loaded first in this process it poisoned sys.path/sys.modules
    # with its vendored `utils` / `model` / `datasets` packages -> CatVTON's
    # `from utils import compute_vae_encodings` then resolves to the wrong module.
    sys.path[:] = [p for p in sys.path if "/repos/IDM-VTON" not in p and "/repos/Leffa" not in p]
    for m in list(sys.modules):
        if m in ("utils", "model", "datasets", "parsing_api") or m.startswith(
                ("utils.", "model.", "datasets.")):
            del sys.modules[m]
    sys.path.insert(0, str(REPO))

    import torch
    from model.pipeline import CatVTONPipeline
    from model.cloth_masker import AutoMasker
    from diffusers.image_processor import VaeImageProcessor

    pipe = CatVTONPipeline(
        base_ckpt=BASE,
        attn_ckpt=str(CKPT),
        attn_ckpt_version="mix",
        weight_dtype=torch.float16,
        use_tf32=True,
        device="cuda",
    )
    masker = AutoMasker(
        densepose_ckpt=str(CKPT / "DensePose"),
        schp_ckpt=str(CKPT / "SCHP"),
        device="cuda",
    )
    mask_proc = VaeImageProcessor(
        vae_scale_factor=8, do_normalize=False,
        do_binarize=True, do_convert_grayscale=True,
    )
    return {"pipe": pipe, "masker": masker, "mask_proc": mask_proc}


def _repaint(result: Image.Image, person: Image.Image, mask: Image.Image) -> Image.Image:
    r = np.array(result).astype(float)
    p = np.array(person.resize(result.size)).astype(float)
    m = (np.array(mask.convert("L").resize(result.size)).astype(float) / 255.0)[..., None]
    out = r * m + p * (1 - m)
    return Image.fromarray(out.clip(0, 255).astype("uint8"))


def infer(handle, person: Image.Image, garment: Image.Image, category: str,
          tag: str = "") -> Image.Image:
    import torch
    from utils import resize_and_crop, resize_and_padding

    # CatVTON's "overall" mask covers the whole body -> on a long coat it wipes
    # the person and inpaints just the garment. Coats are still an upper garment
    # for CatVTON's purposes.
    cloth_type = "upper" if category in ("coat", "coat-w") else _MAP[CATEGORY_TO_PART[category]]
    person_img = resize_and_crop(person, (W, H))
    cloth_img = resize_and_padding(garment, (W, H))

    mask = handle["masker"](person_img, cloth_type)["mask"]
    mask = handle["mask_proc"].blur(mask, blur_factor=9)

    result = handle["pipe"](
        image=person_img,
        condition_image=cloth_img,
        mask=mask,
        num_inference_steps=30,
        guidance_scale=2.5,
        generator=torch.Generator(device="cuda").manual_seed(42),
    )[0]
    return _repaint(result, person_img, mask)
