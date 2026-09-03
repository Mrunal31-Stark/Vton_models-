"""Leffa adapter -> RunPod pod."""
from adapters._runpod_common import call


def generate(person_path, garment_path, category, out_path, spec, tag=""):
    return call("leffa", person_path, garment_path, category, out_path, tag)
