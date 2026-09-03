"""IDM-VTON runner + saree/kurti optimization.

Adapted from yisol/IDM-VTON `gradio_demo/app.py`. Baseline IDM-VTON only repaints
an UPPER-body mask with a generic prompt, so on saree / kurti / lehenga it leaves
the lower half of the person untouched -> the assignment's known failure.

`tag == "optimized"` switches on:
  1. Category-aware mask region  (models.common.CATEGORY_TO_PART): full-length
     categories get 'dresses' (torso+legs+arm) instead of 'upper_body'.
  2. Category-aware prompt        (models.common.garment_prompt): explicit
     "draped saree with pallu" / "long kurti tunic" so the diffusion prior puts
     fabric below the hip.
  3. Category-aware diffusion params (models.common.idm_params): +steps, tuned
     guidance for heavy drape.
  4. Face/hands paste-back from the original for full-length runs (identity).

Baseline (no tag) reproduces the stock demo: 'upper_body', generic prompt, 30 steps.
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from .common import CATEGORY_TO_PART, garment_prompt, idm_params

REPO = Path("/workspace/repos/IDM-VTON")
CKPT = Path("/workspace/ckpts/IDM-VTON")           # diffusers folders + densepose/humanparsing/openpose
DENSEPOSE_PKL = "./ckpt/densepose/model_final_162be9.pkl"
DENSEPOSE_CFG = "./configs/densepose_rcnn_R_50_FPN_s1x.yaml"
W, H = 768, 1024


DEMO = REPO / "gradio_demo"   # apply_net.py, utils_mask.py, vendored densepose/ live here


def _prep_repo():
    """Wire up the repo so imports + weight paths resolve.

    - apply_net / utils_mask / densepose are under gradio_demo/, not repo root.
    - gradio_demo/detectron2 ships a cp39 _C.so that can't load on py3.12; the
      pip detectron2 (cu128 wheel) works, so neutralise the vendored copy.
    - Parsing()/OpenPose()/apply_net read weights from REPO/ckpt/.
    """
    stale = DEMO / "detectron2"
    if stale.is_dir() and not (DEMO / "_detectron2_disabled").exists():
        stale.rename(DEMO / "_detectron2_disabled")

    # The repo ships ckpt/<sub>/ dirs full of 25-byte LFS stubs; replace them with
    # links to the real HF weights.
    dst = REPO / "ckpt"
    dst.mkdir(exist_ok=True)
    for sub in ("densepose", "humanparsing", "openpose", "image_encoder", "ip_adapter"):
        src = CKPT / sub
        link = dst / sub
        if not src.exists():
            continue
        if link.is_symlink() and link.resolve() == src.resolve():
            continue
        if link.exists() or link.is_symlink():
            import shutil
            shutil.rmtree(link, ignore_errors=True)
            try:
                link.unlink()
            except (OSError, FileNotFoundError):
                pass
        link.symlink_to(src)


def load():
    os.chdir(REPO)
    _prep_repo()

    # IDM-VTON's preprocess/ code uses bare imports (`from utils.transforms ...`,
    # `from datasets... import`) that collide with CatVTON's utils.py / the HF
    # `datasets` lib if another model was loaded first in the same process.
    # Drop the poisoned modules and any sibling repo from the path.
    sys.path[:] = [p for p in sys.path
                   if "/repos/CatVTON" not in p and "/repos/Leffa" not in p]
    for m in list(sys.modules):
        if m in ("utils", "datasets", "parsing_api") or m.startswith(("utils.", "datasets.")):
            del sys.modules[m]

    for p in (str(DEMO), str(REPO),
              str(REPO / "preprocess" / "humanparsing"),
              str(REPO / "preprocess" / "openpose")):
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)

    import torch
    from transformers import (CLIPImageProcessor, CLIPVisionModelWithProjection,
                              CLIPTextModel, CLIPTextModelWithProjection, AutoTokenizer)
    from diffusers import DDPMScheduler, AutoencoderKL
    from torchvision import transforms

    from src.tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline
    from src.unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref
    from src.unet_hacked_tryon import UNet2DConditionModel
    from preprocess.humanparsing.run_parsing import Parsing
    from preprocess.openpose.run_openpose import OpenPose
    import apply_net

    base = str(CKPT)
    dt = torch.float16

    unet = UNet2DConditionModel.from_pretrained(base, subfolder="unet", torch_dtype=dt)
    unet.requires_grad_(False)
    unet_encoder = UNet2DConditionModel_ref.from_pretrained(base, subfolder="unet_encoder", torch_dtype=dt)
    unet_encoder.requires_grad_(False)
    tok1 = AutoTokenizer.from_pretrained(base, subfolder="tokenizer", use_fast=False)
    tok2 = AutoTokenizer.from_pretrained(base, subfolder="tokenizer_2", use_fast=False)
    scheduler = DDPMScheduler.from_pretrained(base, subfolder="scheduler")
    te1 = CLIPTextModel.from_pretrained(base, subfolder="text_encoder", torch_dtype=dt)
    te2 = CLIPTextModelWithProjection.from_pretrained(base, subfolder="text_encoder_2", torch_dtype=dt)
    img_enc = CLIPVisionModelWithProjection.from_pretrained(base, subfolder="image_encoder", torch_dtype=dt)
    vae = AutoencoderKL.from_pretrained(base, subfolder="vae", torch_dtype=dt)
    for m in (unet_encoder, img_enc, vae, unet, te1, te2):
        m.requires_grad_(False)

    pipe = TryonPipeline.from_pretrained(
        base, unet=unet, vae=vae, feature_extractor=CLIPImageProcessor(),
        text_encoder=te1, text_encoder_2=te2, tokenizer=tok1, tokenizer_2=tok2,
        scheduler=scheduler, image_encoder=img_enc, torch_dtype=dt,
    )
    pipe.unet_encoder = unet_encoder
    pipe.to("cuda")
    pipe.unet_encoder.to("cuda")

    parsing_model = Parsing(0)
    openpose_model = OpenPose(0)
    openpose_model.preprocessor.body_estimation.model.to("cuda")

    dp_args = apply_net.create_argument_parser().parse_args(
        ("show", DENSEPOSE_CFG, DENSEPOSE_PKL, "dp_segm", "-v",
         "--opts", "MODEL.DEVICE", "cuda"))

    tensor_tf = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize([0.5], [0.5])])
    return {"pipe": pipe, "parsing": parsing_model, "openpose": openpose_model,
            "dp_args": dp_args, "tensor_tf": tensor_tf}


def _pose_img(handle, human_img):
    from detectron2.data.detection_utils import convert_PIL_to_numpy, _apply_exif_orientation
    a = _apply_exif_orientation(human_img.resize((384, 512)))
    a = convert_PIL_to_numpy(a, format="BGR")
    args = handle["dp_args"]
    out = args.func(args, a)[:, :, ::-1]
    return Image.fromarray(out).resize((W, H))


def infer(handle, person: Image.Image, garment: Image.Image, category: str,
          tag: str = "") -> Image.Image:
    import torch
    from utils_mask import get_mask_location

    optimized = tag == "optimized"
    # Baseline = the naive per-category mask a first-time user would pick (lower
    # for pants, upper for everything else incl. Indian wear -> the known failure).
    # Optimized escalates the long garments to a full-body mask.
    baseline_part = "lower_body" if category in ("jeans", "trousers") else "upper_body"
    part = CATEGORY_TO_PART[category] if optimized else baseline_part
    des = garment_prompt(category) if optimized else f"the {category}"
    prm = idm_params(category) if optimized else dict(num_inference_steps=30, guidance_scale=2.0, seed=42)

    human_img = person.resize((W, H))
    garm_img = garment.convert("RGB").resize((W, H))

    keypoints = handle["openpose"](human_img.resize((384, 512)))
    model_parse, _ = handle["parsing"](human_img.resize((384, 512)))
    mask, _ = get_mask_location("hd", part, model_parse, keypoints)
    mask = mask.resize((W, H))

    if optimized and part == "dresses":
        # The person may be wearing a scarf / dupatta / stole that hangs OUTSIDE
        # the body silhouette -> get_mask_location misses it and it leaves an
        # artefact beside the new garment. Union it into the mask so it's repainted.
        from scipy.ndimage import binary_dilation
        pm = np.array(model_parse.resize((W, H), Image.NEAREST))
        extra = pm == 11                      # LIP label 11 = scarf / dupatta / stole
        if extra.any():
            extra = binary_dilation(extra, iterations=8)
            m = np.array(mask.convert("L"))
            m[extra] = 255
            mask = Image.fromarray(m)

    pose_img = _pose_img(handle, human_img)

    pipe = handle["pipe"]
    tf = handle["tensor_tf"]
    with torch.no_grad(), torch.cuda.amp.autocast():
        pe, npe, ppe, nppe = pipe.encode_prompt(
            "model is wearing " + des, num_images_per_prompt=1,
            do_classifier_free_guidance=True,
            negative_prompt="monochrome, lowres, bad anatomy, worst quality, low quality")
        pe_c, _, _, _ = pipe.encode_prompt(
            "a photo of " + des, num_images_per_prompt=1,
            do_classifier_free_guidance=False,
            negative_prompt="monochrome, lowres, bad anatomy, worst quality, low quality")

        pose_t = tf(pose_img).unsqueeze(0).to("cuda", torch.float16)
        garm_t = tf(garm_img).unsqueeze(0).to("cuda", torch.float16)
        gen = torch.Generator("cuda").manual_seed(prm["seed"])
        out = pipe(
            prompt_embeds=pe.to("cuda", torch.float16),
            negative_prompt_embeds=npe.to("cuda", torch.float16),
            pooled_prompt_embeds=ppe.to("cuda", torch.float16),
            negative_pooled_prompt_embeds=nppe.to("cuda", torch.float16),
            num_inference_steps=prm["num_inference_steps"],
            generator=gen, strength=1.0,
            pose_img=pose_t, text_embeds_cloth=pe_c.to("cuda", torch.float16),
            cloth=garm_t, mask_image=mask, image=human_img,
            height=H, width=W, ip_adapter_image=garm_img,
            guidance_scale=prm["guidance_scale"],
        )[0][0]

    if optimized and part == "dresses" and category in ("saree", "lehenga", "coat", "coat-w"):
        # Restore the original face + hair on full-body runs where the long
        # 'dresses' mask reaches the neck and the model can drift on identity.
        # Tight label set (2 hair, 13 face) so no clothing is ever pasted back.
        from PIL import ImageFilter
        pm = np.array(model_parse.resize((W, H), Image.NEAREST))
        keep = (np.isin(pm, [2, 13]).astype("uint8") * 255)
        keep_img = Image.fromarray(keep).filter(ImageFilter.GaussianBlur(3))
        out = Image.composite(human_img, out, keep_img)
    return out
