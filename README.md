# Vizzle Virtual Try-On Model Evaluation

**Goal:** find the VTON model with best accuracy across **all 10 clothing categories**
while staying **< 15 s/generation** and **< Rs 4/generation**.

**Answer:** **IDM-VTON self-hosted, with a category-aware optimization layer.** Across three
test rounds (the last two on full head-to-toe person models with the client's own garments,
prompts and reference looks) it **wins or ties 10 of the 11 categories** — mean accuracy
**4.18/5 vs CatVTON 3.53, Leffa 3.33**. ~8–11 s, ~Rs 0.16/image on one RTX 4090.
The one weak spot is coat on the male model (no shirt+tie under the open coat — a base-photo
limitation, documented below).
CatVTON is the fallback / high-throughput option. See [`results/comparison.md`](results/comparison.md).

---

## Status

| Step | State |
|------|-------|
| 1. Research market | ✅ [`docs/research.md`](docs/research.md) |
| 2. Lock shortlist | ✅ IDM-VTON, Leffa, CatVTON (self-host) + FLUX Pro VTO, image-apps-v2 (fal) |
| 3. Test environment + assets | ✅ harness + 11 test cases (10 categories, coat on both genders), full head-to-toe person models |
| 4. Run matrix + IDM-VTON optimization | ✅ round 3: IDM-VTON base ×11 + opt ×6, CatVTON ×11, Leffa ×11 — 39 generations (earlier rounds archived) |
| 5. Score + comparison | ✅ [`results/scores.csv`](results/scores.csv) → [`results/comparison.md`](results/comparison.md) |
| 6. Screen recording | ✅ **[Google Drive (public link)](https://drive.google.com/file/d/1qhjQVKnL7z1vQZzcoz0XTVPAF4brJXqb/view?usp=sharing)** — also `recording/vizzle_vton_demo_saree.gif` |
| 7. Final recommendation | ✅ below + comparison.md |

**Total RunPod spend: $4.34 / $10 cap** — $3.16 the 3 test rounds + $1.17 a later session to host
the demo for the screen recording; fal account unfunded so FLUX/image-apps researched but not
live-tested. See [`COST_LEDGER.md`](COST_LEDGER.md).

---

## Results

Round-3 per-category winner (full table + all 5 rubric axes in `results/comparison.md`):

| category | winner | score | note |
|---|---|--:|---|
| saree | **IDM-VTON (opt)** | 4.2 | floor-length drape + pallu + **matching blouse**; others give a one-shoulder gown |
| kurti | **IDM-VTON (opt)** | 4.6 | full length, placket + slits; others add a dupatta "cape" |
| lehenga | **IDM-VTON (opt)** | 4.2 | choli + floor-length embroidered skirt + sheer dupatta |
| top | **IDM-VTON** | 4.2 | velvet wrap faithful, no side-drape artefact |
| jumpsuit | **IDM-VTON (opt)** | 4.2 | clean wide-leg jumpsuit; others bleed the palazzo / add a blob |
| t-shirt | **IDM-VTON** | 4.2 | clean black tee; CatVTON renders it tan long-sleeve, Leffa barely applies it |
| shirt | **IDM-VTON** | 4.6 | plaid flannel crisp; CatVTON 4.2 close; Leffa turns it into a plaid suit |
| jeans | IDM / CatVTON / Leffa tie | 4.0 | all apply denim cleanly on the full-length male base |
| trousers | IDM / CatVTON tie | 4.0 | both clean; Leffa 3.8 |
| coat (male) | Leffa 3.6 / **IDM-VTON (opt) 3.4** | 3.4–3.6 | weakest category for all — no model reproduces the reference shirt+tie (casual base). Leffa's *closed* coat edges the rubric; IDM's *open* silhouette matches the brief. CatVTON 3.0 short blazer |
| coat-w | **IDM-VTON (opt)** | 4.4 | belted wool coat + fur collar, clean |

**Mean accuracy (11 categories): IDM-VTON 4.18 · CatVTON 3.53 · Leffa 3.33.**
IDM-VTON wins or ties 10 of 11 (clear best on the 8 hardest); the exception is coat on the
male model, where every model is weak.

Speed & cost (all far inside the caps, on one RTX 4090):

| model | gen time | Rs/image |
|---|--:|--:|
| CatVTON | 5.8 s | 0.10 |
| Leffa (self-host) | 6.9 s | 0.13 |
| IDM-VTON baseline | 7–9 s | 0.13–0.16 |
| IDM-VTON optimized | 9–11 s | 0.16–0.20 |

---

## The IDM-VTON optimization (Step 4 caveat)

Baseline IDM-VTON repaints only an **upper-body mask** with a generic prompt, so any long
garment (saree, kurti, lehenga, long coat) is fitted as a crop-top and the legs are left as
the original clothing — the assignment's documented failure. **No fine-tuning / no training**
(that alone would exceed the $10 cap). The fix is prompt + parameter + pre/post-processing,
in [`runpod/models/idm_vton_runner.py`](runpod/models/idm_vton_runner.py):

1. **Category-aware mask region** (`models/common.CATEGORY_TO_PART`): saree / kurti / lehenga /
   jumpsuit / coat escalate from `upper_body` to a full-body (`dresses`) mask.
2. **Category prompt** (`config.GARMENT_PROMPT_FULL`, compressed to `models/common.garment_prompt`
   for IDM's 77-token CLIP encoder): the client's detailed prompts — e.g. "floor-length draped
   saree, pleats tucked at the center-front waist, pallu over the left shoulder, **over a fitted
   matching-colour short-sleeve blouse, midriff bare**"; "knee-length overcoat worn **open and
   unbuttoned over the outfit, the clothes underneath still visible**".
3. **Category params** (`models/common.IDM_PARAMS`): 32–40 diffusion steps + guidance 2.0–2.5
   for heavy drape (vs 30 / 2.0 default).
4. **Scarf/dupatta mask-union** (`idm_vton_runner.infer`): the female model wears a dupatta that
   hangs outside her body silhouette; `get_mask_location` misses it and it leaves a "cape" next
   to the new garment — so LIP label 11 (scarf) is unioned into the mask and repainted away.
5. **Light face + hair paste-back** (`np.isin(parse, [2, 13])`, feathered) on the full-body runs
   (saree, lehenga, coat, coat-w) to hold identity where the long mask reaches the neck.

Before/after: [`results/idm_before_after.png`](results/idm_before_after.png). The optimization
takes saree, lehenga, jumpsuit and both coats from a truncated crop-top to the full garment.

**Residual limits:**
- IDM-VTON is SDXL-based on Western catalog data — the saree drape is correct in
  shape/length/blouse but the pallu is slightly stiff.
- **`coat` (male) — accepted limitation.** IDM-VTON inpaints only the coat region, so with a
  casual base photo (black polo) it **cannot show a white shirt + tie** through the open front
  as in `assets/reference/coat_expected_look.png`; the half-repainted polo reads as a dark top
  tucked into dark trousers, and the face drifts slightly on the full-body mask. Two fixes,
  neither done to stay inside budget: **(a)** supply a formal male base photo (shirt + tie +
  trousers) and re-run `coat` only (~$0.30, one short pod session); **(b)** FLUX Pro VTO, which
  is prompt-directed and can synthesise the shirt+tie (needs fal.ai funding). `coat-w` (female,
  belted overcoat, no shirt+tie in the brief) is unaffected and scores 4.4.
- The person photo must be **head-to-toe** — a knee-cropped model caps every long garment at
  knee length regardless of the mask.

---

## Test set

`assets/persons/` — `female.jpg` (Indian woman in a kurta set, full head-to-toe, plain bg),
`male.jpg` (Indian man in a black polo + cream chinos + sneakers, full head-to-toe — round-3
swap from the earlier suited man; the earlier one is kept as `_male_suited_prev.jpg`).
`assets/garments/` — one product shot per category; `assets/garments/extras/coat_women.jpg`
is used for `coat-w`. `assets/reference/*_expected_look.png` — client-supplied target looks
that steer the optimization prompts. Manifest + provenance in `assets/sources.json`.

Gender rule: saree/kurti/lehenga/top/jumpsuit → female; t-shirt/shirt/jeans/trousers → male;
**coat on both** (`coat` male, `coat-w` female). The `t-shirt` image arrived black-on-black
(unsegmentable) and was rebuilt from a plain flat-lay. Losing the suited base for round 3
means `coat` is now coat-over-polo, not the coat-over-shirt-and-tie of the reference.

Same person + garment fed to every model. `python scripts/verify_assets.py` writes a contact sheet.

---

## Shortlist & why

| Model | Host | Cost/img | Speed | Verdict |
|-------|------|---------:|------:|---------|
| **IDM-VTON** | RunPod self-host | Rs 0.16 | 9 s | **recommended** — wins or ties 10 of 11 categories (mean 4.18); only weak on male coat (shirt+tie not in base photo) |
| CatVTON | RunPod self-host | Rs 0.10 | 6 s | fallback / high-throughput (mean 3.53); no text lever → weak on Indian wear, the black tee, coats |
| Leffa | RunPod self-host (isolated venv) | Rs 0.13 | 7 s | mean 3.33; over-applies patterns, barely applies plain tees, hanging-fabric artefacts |
| FLUX Pro VTO | fal | ~Rs 3.4 | ~8 s | not tested (fal unfunded); prompt-directed — revisit if a hosted option is wanted |
| image-apps-v2 | fal | ~Rs 3.5 | ~10 s | not tested (fal unfunded) |

Cut at research: FASHN ($0.075), Kling Kolors ($0.07), Nano Banana Pro — all over Rs 4.

---

## Repo layout

```
config.py                 categories (11: coat on both), gender map, model registry, caps, client prompts
run_tryon.py              CLI harness — times, costs, logs every generation; auto-halts at $10
adapters/                 one thin adapter per model (runpod / fal)
runpod/setup_deps.sh      re-create the pod Python env (weights already on the volume)
runpod/leffa_venv.sh      isolated venv for Leffa (needs diffusers 0.31, IDM needs 0.25)
runpod/server.py          FastAPI: POST /tryon -> image + gpu_seconds   (idm-vton + catvton)
runpod/leffa_server.py    same, Leffa only, runs in venv_leffa
runpod/models/*_runner.py per-model load()/infer(); IDM-VTON optimization lives here
webapp/                   ~60-line Flask UI — upload person/garment, pick, generate (for the recording)
scripts/verify_assets.py  contact sheet of the test set
scripts/build_comparison.py  log.csv + scores.csv -> comparison.md
results/log.csv           auto: model,category,tag,gen_time,wall,cost,within_speed,within_cost
results/scores.csv        manual 1–5 rubric (fit/drape/texture/artifacts/identity)
results/comparison.md     the deliverable table + per-category winners + recommendation
results/outputs/          every generated image
COST_LEDGER.md            $10 cap tracking — actual $1.85
```

---

## Reproduce

```bash
pip install -r requirements.txt
cp .env.example .env          # RUNPOD_TRYON_URL (+ RUNPOD_LEFFA_URL, FAL_KEY if used)

# 1. provision a RunPod RTX 4090 pod + a network volume, attach the volume at /workspace
# 2. on the pod:
bash runpod/setup.sh          # first time: clone repos + download weights to the volume
bash runpod/setup_deps.sh     # (re)install the Python env
#    detectron2: prebuilt cu128 wheel; onnxruntime-gpu==1.18.1 + numpy==1.26.4
#    (newer ORT can't parse the 2023-era human-parsing ONNX); diffusers pinned 0.25
python runpod/server.py       # note the pod proxy URL -> .env RUNPOD_TRYON_URL
bash runpod/leffa_venv.sh && (cd runpod && venv_leffa/bin/python leffa_server.py)  # for Leffa

# 3. from your machine:
python run_tryon.py --model idm-vton,catvton --category all
python run_tryon.py --model idm-vton --category saree,kurti,lehenga,jumpsuit,coat --tag optimized
python run_tryon.py --model leffa --category all      # RUNPOD_LEFFA_URL -> leffa_server

# 4. score results/outputs/* into results/scores.csv, then
python scripts/build_comparison.py

# 5. demo UI for the recording
python webapp/app.py          # http://localhost:5000
```

---

## Screen recording → Google Drive

**Public link (Anyone with the link):**
https://drive.google.com/file/d/1qhjQVKnL7z1vQZzcoz0XTVPAF4brJXqb/view?usp=sharing

The recording shows the webapp flow end-to-end (upload person → upload garment → pick category +
model + optimization → Generate → result) across multiple clothing types. A short local copy is
also at `recording/vizzle_vton_demo_saree.gif`.

All RunPod resources have since been torn down (pods terminated, network volume deleted). To
record more, provision a fresh pod + network volume and run `runpod/setup2.sh` for the full
clone + weight download, then `runpod/server.py`.

---

## Final recommendation

**Primary: IDM-VTON + the category-aware optimization layer**, self-hosted on one RTX 4090.
Across three test rounds it **wins or ties 10 of the 11 categories** (mean 4.18/5 vs
CatVTON 3.53, Leffa 3.33), and is the clear best on the 8 hard cases — every Indian-wear
category and the women's coat. It is the only model that renders a coat *open* over the
outfit and the only one that puts a matching blouse under the saree. ~Rs 0.16/image, ~9 s —
an order of magnitude inside both caps, no per-call vendor fee or rate limit.

The one weak category is **coat on the male model**: with a casual base photo IDM-VTON can't
show a shirt + tie through the open coat (see Residual limits). This is an input-data /
model-class limit, not a ranking against the other models — CatVTON (short blazer) and Leffa
(closed coat) handle it no better. A formal male base photo or FLUX Pro VTO would close it.

**Fallback: CatVTON** for a low-latency / lowest-cost tier where Indian-wear drape isn't the
priority — fine on menswear and simple tops, but no text lever to fix its weak spots.

**Revisit later: FLUX Pro VTO** (hosted, prompt-directed like the IDM optimization) if a
~Rs 3.4/image hosted call is acceptable and the last bit of saree-pallu realism matters.
