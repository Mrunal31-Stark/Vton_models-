"""Leffa runner (franciszzj/Leffa) — VITON-HD virtual try-on path.

Adapted from the repo's app.py (LeffaPredictor.leffa_predict). Leffa takes an
explicit garment type ("upper_body" | "lower_body" | "dresses") straight from
models.common.CATEGORY_TO_PART, which is why it handles lehenga / jumpsuit /
saree more gracefully than baseline IDM-VTON.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from .common import CATEGORY_TO_PART

REPO = Path("/workspace/repos/Leffa")
CKPT = Path("/workspace/ckpts/Leffa")
W, H = 768, 1024


def _shim_diffusers():
    """Leffa vendors a ~0.27 UNet; we're pinned to diffusers 0.25 for IDM-VTON.
    The only missing import-time symbol is GLIGENTextBoundingboxProjection, and
    Leffa's try-on config never instantiates it (attention_type='default')."""
    import diffusers.models.embeddings as emb
    if not hasattr(emb, "GLIGENTextBoundingboxProjection"):
        import torch.nn as nn

        class GLIGENTextBoundingboxProjection(nn.Module):  # noqa: D401 - stub
            def __init__(self, *a, **k):
                super().__init__()

            def forward(self, *a, **k):
                raise RuntimeError("GLIGEN stub called - unexpected for Leffa try-on")

        emb.GLIGENTextBoundingboxProjection = GLIGENTextBoundingboxProjection


def load():
    sys.path.insert(0, str(REPO))
    _shim_diffusers()
    from leffa.transform import LeffaTransform
    from leffa.model import LeffaModel
    from leffa.inference import LeffaInference
    from leffa_utils.densepose_predictor import DensePosePredictor
    from preprocess.humanparsing.run_parsing import Parsing
    from preprocess.openpose.run_openpose import OpenPose

    parsing = Parsing(
        atr_path=str(CKPT / "humanparsing/parsing_atr.onnx"),
        lip_path=str(CKPT / "humanparsing/parsing_lip.onnx"),
    )
    openpose = OpenPose(body_model_path=str(CKPT / "openpose/body_pose_model.pth"))
    densepose = DensePosePredictor(
        config_path=str(CKPT / "densepose/densepose_rcnn_R_50_FPN_s1x.yaml"),
        weights_path=str(CKPT / "densepose/model_final_162be9.pkl"),
    )
    vt_model = LeffaModel(
        pretrained_model_name_or_path=str(CKPT / "stable-diffusion-inpainting"),
        pretrained_model=str(CKPT / "virtual_tryon.pth"),
        dtype="float16",
    )
    inference = LeffaInference(model=vt_model)
    return {
        "parsing": parsing, "openpose": openpose, "densepose": densepose,
        "inference": inference, "transform": LeffaTransform(),
    }


def infer(handle, person: Image.Image, garment: Image.Image, category: str,
          tag: str = "") -> Image.Image:
    from leffa_utils.utils import resize_and_center, get_agnostic_mask_hd

    part = CATEGORY_TO_PART[category]  # upper_body | lower_body | dresses
    src = resize_and_center(person.convert("RGB"), W, H)
    ref = resize_and_center(garment.convert("RGB"), W, H)
    src_arr = np.array(src)

    model_parse, _ = handle["parsing"](src.resize((384, 512)))
    keypoints = handle["openpose"](src.resize((384, 512)))
    mask = get_agnostic_mask_hd(model_parse, keypoints, part).resize((W, H))

    seg = handle["densepose"].predict_seg(src_arr)[:, :, ::-1]
    densepose = Image.fromarray(seg)

    data = handle["transform"]({
        "src_image": [src], "ref_image": [ref],
        "mask": [mask], "densepose": [densepose],
    })
    out = handle["inference"](
        data, ref_acceleration=False,
        num_inference_steps=30, guidance_scale=2.5, seed=42, repaint=True,
    )
    return out["generated_image"][0]
