"""Shared preprocessing used across runners.

CATEGORY_TO_PART maps each assignment category to the body region a VTON model
must repaint. This is the backbone of the IDM-VTON saree/kurti optimization:
those garments need a FULL-BODY mask (torso + legs + one arm for the pallu),
not the default UPPER mask, or the model leaves the lower half untouched.
"""

UPPER = "upper_body"
LOWER = "lower_body"
FULL = "dresses"  # full-length / one-piece silhouette

CATEGORY_TO_PART = {
    "saree": FULL,
    "lehenga": FULL,
    "jumpsuit": FULL,
    "kurti": FULL,      # long kurtis fall below the hip -> treat as full-length
    "coat": FULL,       # knee-length overcoat -> needs the long mask
    "coat-w": FULL,
    "top": UPPER,
    "t-shirt": UPPER,
    "shirt": UPPER,
    "jeans": LOWER,
    "trousers": LOWER,
}

# Per-category diffusion params for IDM-VTON. Heavy-drape Indian wear needs more
# steps + higher guidance to resolve pleats/dupatta without smearing.
IDM_PARAMS = {
    "saree":   dict(num_inference_steps=40, guidance_scale=2.5, seed=42),
    "lehenga": dict(num_inference_steps=40, guidance_scale=2.5, seed=42),
    "kurti":   dict(num_inference_steps=35, guidance_scale=2.2, seed=42),
    "jumpsuit":dict(num_inference_steps=35, guidance_scale=2.0, seed=42),
    "coat":    dict(num_inference_steps=32, guidance_scale=2.0, seed=42),
    "coat-w":  dict(num_inference_steps=35, guidance_scale=2.2, seed=42),
    "_default":dict(num_inference_steps=30, guidance_scale=2.0, seed=42),
}


def idm_params(category: str) -> dict:
    return IDM_PARAMS.get(category, IDM_PARAMS["_default"])


def garment_prompt(category: str) -> str:
    """Short prompt for IDM-VTON (CLIP text encoder, 77-token limit -> keep it terse)."""
    nice = {"kurti": "a long straight-cut Indian kurti tunic reaching below the knee, "
                     "with deep side slits and a smooth unbulky fit over the hips",
            "saree": "a floor-length draped Indian saree, pleats tucked at the center-front waist, "
                     "pallu pulled diagonally over the left shoulder, worn over a fitted "
                     "matching-colour short-sleeve blouse, midriff bare",
            "lehenga": "an Indian lehenga: high-waisted floor-length A-line skirt with metallic "
                       "embroidery, fitted cropped choli, sheer net dupatta over one shoulder",
            "coat": "wearing a knee-length wool overcoat over the outfit, front hanging open and "
                    "unbuttoned, notched lapel, long sleeves, the clothes underneath still visible",
            "coat-w": "a knee-length belted wool overcoat with a collar worn open over the outfit",
            "jumpsuit": "a full-length one-piece sleeveless jumpsuit, collared button bodice, "
                        "tie belt at the waist, wide-leg palazzo trousers draping to the floor"}
    return f"model is wearing {nice.get(category, 'the ' + category)}"


# Full user-supplied prompts live in config.GARMENT_PROMPT_FULL (shared with the
# fal adapters). IDM-VTON only uses the compressed garment_prompt() above.
