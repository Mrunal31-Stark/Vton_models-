"""FLUX Pro Virtual Try-On (fal-ai/flux-pro/v1/vto).

Prompt-directed: it takes natural-language styling instructions, so we feed the
rich per-category prompt from config.garment_prompt_full(). $0.0375/MP (~Rs 3.4).
"""
import config
from adapters._fal_common import _data_uri, run

_BASE = ("A natural front-facing full-body studio photo on a plain background, "
         "the person's face, hair, body shape and pose unchanged. ")


def generate(person_path, garment_path, category, out_path, spec, tag=""):
    args = {
        "human_image_url": _data_uri(person_path),
        "garment_image_url": _data_uri(garment_path),
        "prompt": _BASE + config.garment_prompt_full(category),
        "output_format": "png",
        "seed": 42,
    }
    return run("flux-tryon-pro", spec["fal_endpoint"], args, out_path)
