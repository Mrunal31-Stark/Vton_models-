"""image-apps-v2 virtual try-on (fal-ai/image-apps-v2/virtual-try-on).

No prompt / no garment-type field. $0.04/image, 4K output, pose preserved.
"""
from adapters._fal_common import _data_uri, run


def generate(person_path, garment_path, category, out_path, spec, tag=""):
    args = {
        "person_image_url": _data_uri(person_path),
        "clothing_image_url": _data_uri(garment_path),
        "preserve_pose": True,
        "aspect_ratio": "3:4",
    }
    return run("image-apps-v2", spec["fal_endpoint"], args, out_path)
