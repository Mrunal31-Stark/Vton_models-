"""IDM-VTON adapter -> RunPod pod."""
from adapters._runpod_common import call


def generate(person_path, garment_path, category, out_path, spec, tag=""):
    return call("idm-vton", person_path, garment_path, category, out_path, tag)
