"""Leffa virtual try-on (fal-ai/leffa/virtual-tryon).

Self-hosting Leffa needs diffusers ~0.27 which conflicts with the diffusers 0.25
IDM-VTON requires in the shared pod env (runpod/models/leffa_runner.py kept for
reference). fal price $0.10/img is over the Rs 4 cap; self-host would be ~Rs 0.3.
garment_type must be upper_body | lower_body | dresses.
"""
from adapters._fal_common import _data_uri, run

_TYPE = {
    "saree": "dresses", "lehenga": "dresses", "jumpsuit": "dresses", "kurti": "dresses",
    "coat": "upper_body", "top": "upper_body", "t-shirt": "upper_body",
    "shirt": "upper_body", "jeans": "lower_body", "trousers": "lower_body",
}


def generate(person_path, garment_path, category, out_path, spec, tag=""):
    args = {
        "human_image_url": _data_uri(person_path),
        "garment_image_url": _data_uri(garment_path),
        "garment_type": _TYPE.get(category, "upper_body"),
        "num_inference_steps": 40,
        "guidance_scale": 2.5,
        "seed": 42,
    }
    return run("leffa", spec["fal_endpoint"], args, out_path)
