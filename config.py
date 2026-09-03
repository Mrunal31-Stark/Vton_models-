"""Central config: clothing categories, person assignment, model registry."""

# The 10 assignment categories -> the person model each is tried on.
# Womenswear (saree/kurti/lehenga/top/jumpsuit) -> female model;
# menswear (t-shirt/shirt/jeans/trousers) -> male model;
# coat is tested on BOTH: "coat" (male, assets/garments/coat.jpg) and
# "coat-w" (female, assets/garments/extras/coat_women.jpg).
CATEGORIES = {
    "saree":    "female",
    "kurti":    "female",
    "lehenga":  "female",
    "top":      "female",
    "jumpsuit": "female",
    "t-shirt":  "male",
    "shirt":    "male",
    "jeans":    "male",
    "trousers": "male",
    "coat":     "male",
    "coat-w":   "female",
}

# category -> the underlying garment "kind" for prompts / masks (coat-w == coat).
BASE_CATEGORY = {"coat-w": "coat"}

PERSON_IMAGES = {
    "female": "assets/persons/female.jpg",
    "male":   "assets/persons/male.jpg",
}

_GARMENT_OVERRIDE = {
    "coat-w": "assets/garments/extras/coat_women.jpg",
}


def garment_path(category: str) -> str:
    return _GARMENT_OVERRIDE.get(category, f"assets/garments/{category}.jpg")


def base_category(category: str) -> str:
    return BASE_CATEGORY.get(category, category)

# Model registry. `kind`:
#   "runpod" -> POST to {RUNPOD_TRYON_URL}/tryon with model=<key>
#   "fal"    -> adapters/fal_*.py
MODELS = {
    "idm-vton": {"kind": "runpod", "adapter": "idm_vton",
                 "notes": "ECCV'24 baseline; weak on saree/kurti out of the box"},
    "leffa":    {"kind": "runpod", "adapter": "leffa",
                 "notes": "Meta; explicit upper/lower/dress mode, strong pose preservation. "
                          "Self-hosted in an ISOLATED venv (/workspace/venv_leffa, diffusers 0.31) "
                          "because its vendored UNet conflicts with the diffusers 0.25 IDM-VTON "
                          "needs. Same 4090 -> ~Rs 0.3/img. (fal price would be $0.10 = Rs 8.8, over cap.)"},
    "catvton":  {"kind": "runpod", "adapter": "catvton",
                 "notes": "lightweight, fastest, cheapest"},
    "flux-tryon-pro": {"kind": "fal", "adapter": "fal_flux",
                       "fal_endpoint": "fal-ai/flux-pro/v1/vto",
                       "notes": "hosted FLUX Pro VTO; $0.0375/MP ~= $0.038/img (Rs 3.4, UNDER cap); "
                                "takes a text prompt -> config.garment_prompt_full()"},
    "image-apps-v2":  {"kind": "fal", "adapter": "fal_image_apps",
                       "fal_endpoint": "fal-ai/image-apps-v2/virtual-try-on",
                       "notes": "hosted; $0.04/img (Rs 3.5, UNDER cap); 4K output"},
}

# Rich garment prompts (user-supplied) for models that take long text conditioning
# (FLUX, image-apps). IDM-VTON uses a compressed version (runpod/models/common.py)
# because its CLIP text encoder truncates at 77 tokens.
GARMENT_PROMPT_FULL = {
    "kurti": ("A long, straight-cut Indian kurti tunic in fluid silk-crepe, reaching below the "
              "knee; tailored bodice flowing into a relaxed drape, deep side slits from the waist, "
              "three-quarter sleeves, subtle mandarin collar, flat fabric with realistic seam "
              "shadows and a smooth unbulky fit over the hips."),
    "saree": ("A gracefully draped Indian saree in lightweight georgette/chiffon, floor-length; "
              "tightly gathered uniformly cascading pleats tucked at the center-front waist form a "
              "voluminous fluid skirt to the ankles; the pallu is pulled diagonally across the "
              "torso and secured over the left shoulder, falling freely down the back. Worn over a "
              "FITTED MATCHING-COLOUR SHORT-SLEEVE BLOUSE (choli) that covers the bust and upper "
              "back, with the natural midriff bare between the blouse and the drape. Clear layering "
              "between blouse, skin and saree fabric."),
    "lehenga": ("A high-couture Indian lehenga: high-waisted floor-length skirt with an "
                "exaggerated architectural A-line flare and stiff structural drape, rich metallic "
                "threadwork embroidery catching light; skin-tight cropped choli with sweetheart "
                "neckline and fitted short sleeves; sheer net dupatta over one shoulder with "
                "transparent rendering and scalloped embroidered borders."),
    "coat": ("A tailored knee-length overcoat worn OPEN and completely UNBUTTONED over the "
             "existing outfit; the front hangs open so the shirt / top and trousers underneath "
             "stay fully visible. Mid-weight wool, sharp padded shoulders, full-length straight "
             "sleeves, classic notched lapel, soft vertical folds down the open front, side welt "
             "pockets; the coat layers cleanly on top without replacing or warping the clothes "
             "underneath."),
    "coat-w": ("A knee-length belted wool overcoat with a collar, worn over the outfit; clean "
               "layered drape, full-length sleeves, tied waist belt, front falling straight; the "
               "coat sits on top of the existing clothing without replacing it."),
    "jumpsuit": ("A sleek full-length one-piece jumpsuit with a continuous elongated silhouette; "
                 "sharply tailored bodice, deep V-neckline, sleeveless shoulders, flowing into a "
                 "cinched natural waist with a subtle self-fabric belt; wide-leg palazzo trousers "
                 "draping fluidly to the floor; matte crepe with slight stretch, smooth contouring "
                 "around bust and hips before a relaxed voluminous leg drape."),
}


def garment_prompt_full(category: str) -> str:
    return GARMENT_PROMPT_FULL.get(category, f"a person wearing the {category}")


# Rs -> USD for the ledger. Assignment cap: Rs 4 / generation.
USD_PER_INR = 0.0113
INR_COST_CAP = 4.0
SPEED_CAP_SEC = 15.0
BUDGET_CAP_USD = 10.0
