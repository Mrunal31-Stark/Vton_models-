# VTON model comparison

Gates: generation < 15 s  &  cost < Rs 4 per image.  All tested models clear both by a wide margin — so the decision is **accuracy**.

| model | category | variant | gen s | Rs/img | fit | drape | texture | artifact-free | identity | mean | pass |
|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|:--:|
| catvton | coat | baseline | 5.7 | 0.10 | 3 | 2 | 3 | 3 | 4 | 3 | OK |
| catvton | coat-w | baseline | 5.6 | 0.10 | 3 | 3 | 3 | 2 | 4 | 3 | OK |
| catvton | jeans | baseline | 5.7 | 0.10 | 4 | 4 | 4 | 4 | 4 | 4 | OK |
| catvton | jumpsuit | baseline | 5.6 | 0.10 | 3 | 3 | 4 | 3 | 4 | 3.4 | OK |
| catvton | kurti | baseline | 5.6 | 0.10 | 4 | 3 | 4 | 3 | 4 | 3.6 | OK |
| catvton | lehenga | baseline | 5.8 | 0.10 | 4 | 3 | 3 | 4 | 4 | 3.6 | OK |
| catvton | saree | baseline | 5.8 | 0.11 | 3 | 2 | 3 | 4 | 4 | 3.2 | OK |
| catvton | shirt | baseline | 5.6 | 0.10 | 4 | 4 | 4 | 4 | 5 | 4.2 | OK |
| catvton | t-shirt | baseline | 5.7 | 0.10 | 2 | 3 | 3 | 3 | 4 | 3 | OK |
| catvton | top | baseline | 5.6 | 0.10 | 4 | 4 | 4 | 3 | 4 | 3.8 | OK |
| catvton | trousers | baseline | 5.7 | 0.10 | 4 | 4 | 4 | 4 | 4 | 4 | OK |
| idm-vton | coat | baseline | 8.7 | 0.16 | - | - | - | - | - | - | OK |
| idm-vton | coat-w | baseline | 7.1 | 0.13 | - | - | - | - | - | - | OK |
| idm-vton | jeans | baseline | 8.6 | 0.16 | 4 | 4 | 4 | 4 | 4 | 4 | OK |
| idm-vton | jumpsuit | baseline | 7.1 | 0.13 | - | - | - | - | - | - | OK |
| idm-vton | kurti | baseline | 7.0 | 0.13 | - | - | - | - | - | - | OK |
| idm-vton | lehenga | baseline | 7.1 | 0.13 | - | - | - | - | - | - | OK |
| idm-vton | saree | baseline | 8.0 | 0.14 | - | - | - | - | - | - | OK |
| idm-vton | shirt | baseline | 8.6 | 0.16 | 5 | 4 | 4 | 5 | 5 | 4.6 | OK |
| idm-vton | t-shirt | baseline | 8.9 | 0.16 | 4 | 4 | 4 | 4 | 5 | 4.2 | OK |
| idm-vton | top | baseline | 7.2 | 0.13 | 4 | 4 | 4 | 4 | 5 | 4.2 | OK |
| idm-vton | trousers | baseline | 8.6 | 0.16 | 4 | 4 | 4 | 4 | 4 | 4 | OK |
| idm-vton | coat | optimized | 8.8 | 0.16 | 3 | 3 | 4 | 4 | 3 | 3.4 | OK |
| idm-vton | coat-w | optimized | 9.4 | 0.17 | 4 | 4 | 4 | 5 | 5 | 4.4 | OK |
| idm-vton | jumpsuit | optimized | 9.4 | 0.17 | 4 | 4 | 4 | 4 | 5 | 4.2 | OK |
| idm-vton | kurti | optimized | 7.9 | 0.14 | 5 | 4 | 4 | 5 | 5 | 4.6 | OK |
| idm-vton | lehenga | optimized | 10.1 | 0.18 | 4 | 4 | 4 | 4 | 5 | 4.2 | OK |
| idm-vton | saree | optimized | 11.2 | 0.20 | 4 | 4 | 4 | 4 | 5 | 4.2 | OK |
| leffa | coat | baseline | 7.1 | 0.13 | 3 | 3 | 4 | 4 | 4 | 3.6 | OK |
| leffa | coat-w | baseline | 6.9 | 0.12 | 3 | 3 | 3 | 2 | 3 | 2.8 | OK |
| leffa | jeans | baseline | 7.0 | 0.13 | 4 | 4 | 4 | 4 | 4 | 4 | OK |
| leffa | jumpsuit | baseline | 6.9 | 0.13 | 3 | 3 | 4 | 2 | 4 | 3.2 | OK |
| leffa | kurti | baseline | 6.8 | 0.12 | 3 | 3 | 3 | 2 | 4 | 3 | OK |
| leffa | lehenga | baseline | 6.8 | 0.12 | 4 | 4 | 3 | 4 | 4 | 3.8 | OK |
| leffa | saree | baseline | 7.2 | 0.13 | 2 | 2 | 3 | 3 | 4 | 2.8 | OK |
| leffa | shirt | baseline | 7.1 | 0.13 | 2 | 3 | 3 | 3 | 3 | 2.8 | OK |
| leffa | t-shirt | baseline | 8.0 | 0.14 | 3 | 3 | 3 | 3 | 4 | 3.2 | OK |
| leffa | top | baseline | 6.8 | 0.12 | 3 | 4 | 4 | 3 | 4 | 3.6 | OK |
| leffa | trousers | baseline | 7.0 | 0.13 | 4 | 4 | 3 | 4 | 4 | 3.8 | OK |

## Rollup (mean accuracy)

| model / variant | categories | mean accuracy | worst category |
|---|--:|--:|---|
| catvton (baseline) | 11 | 3.53 | t-shirt (3) |
| idm-vton (baseline) | 5 | 4.20 | jeans (4) |
| idm-vton (optimized) | 6 | 4.17 | coat (3.4) |
| leffa (baseline) | 11 | 3.33 | saree (2.8) |

<!-- MANUAL BELOW -->

## Round 3 dataset

Both person photos are full head-to-toe. **Female:** Indian woman in a beige kurta set.
**Male (round 3):** Indian man in a black polo + cream chinos + white sneakers, plain
background — swapped in from the round-2 suited man so grey jeans / charcoal trousers read
with proper contrast and the full leg + feet are in frame. Menswear (t-shirt, shirt, jeans,
trousers, coat) was re-run on this base; womenswear is unchanged from round 2.

**coat** is tested on both models (`coat` = male, `coat-w` = female + `extras/coat_women.jpg`).
Losing the suited base means `coat` is now coat-over-polo rather than coat-over-shirt-and-tie.
**Known limitation (accepted):** IDM-VTON only inpaints the coat region, so it cannot synthesise
a white shirt + tie that is not present in the base photo — the opening of the coat shows the
half-repainted polo, which reads as a dark top tucked into dark trousers rather than the
reference's shirt + tie + navy trousers. Fixing this needs either a formal male base photo
(shirt + tie + trousers) or a prompt-directed model (FLUX Pro VTO). Scored down accordingly
(`coat` male = 3.4). `coat-w` (female) is unaffected and scores 4.4.

Effective IDM-VTON = optimized output for saree/kurti/lehenga/jumpsuit/coat/coat-w, baseline
for top/t-shirt/shirt/jeans/trousers.

| model | mean accuracy (11 cats) | min category |
|---|--:|---|
| **IDM-VTON (effective)** | **4.18** | coat (male) 3.4 — no shirt+tie under the open coat |
| CatVTON | 3.53 | t-shirt 3.0 (colour + sleeve wrong, no text lever) |
| Leffa | 3.33 | saree 2.8 |

## Best model per category (round 3)

| category | winner | score | why |
|---|---|--:|---|
| saree | **IDM-VTON (opt)** | 4.2 | only one with a real floor-length drape + pallu + matching blouse |
| kurti | **IDM-VTON (opt)** | 4.6 | full length + placket; others add a dupatta "cape" |
| lehenga | **IDM-VTON (opt)** | 4.2 | choli + floor-length embroidered skirt + sheer dupatta, cleanest |
| top | **IDM-VTON** | 4.2 | velvet wrap faithful, no side-drape artefact |
| jumpsuit | **IDM-VTON (opt)** | 4.2 | clean wide-leg jumpsuit; CatVTON bleeds the palazzo, Leffa adds a blob |
| t-shirt | **IDM-VTON** | 4.2 | clean black tee; CatVTON turns it tan long-sleeve, Leffa barely applies it |
| shirt | **IDM-VTON** | 4.6 | plaid flannel crisp; CatVTON 4.2 close; Leffa turns it into a plaid suit |
| jeans | IDM / CatVTON / Leffa tie | 4.0 | all three apply denim cleanly on the full-length base |
| trousers | IDM / CatVTON tie | 4.0 | both clean; Leffa 3.8 |
| coat (male) | Leffa 3.6 / **IDM-VTON (opt) 3.4** | 3.4–3.6 | weakest category for every model — none reproduce the reference's shirt+tie (base is a casual polo). Leffa's *closed* coat scores marginally higher on the rubric; IDM's *open knee-length* silhouette matches the client brief better. CatVTON 3.0 (short blazer). |
| coat-w | **IDM-VTON (opt)** | 4.4 | belted wool coat + fur collar, clean; others add a dupatta artefact |

**IDM-VTON wins or ties 10 of the 11 categories** (clear best on the 8 hardest). The one
exception is coat on the male model, where no model does well — Leffa edges it 3.6 vs 3.4 by
the rubric, but produces a *closed* coat against the client's "worn open" brief.

## Recommendation

**Primary: IDM-VTON + the category-aware optimization layer** (`runpod/models/idm_vton_runner.py`)
— category-aware full-body mask, the client's prompts (compressed to CLIP's 77 tokens), tuned
steps/guidance, a scarf/dupatta mask-union to kill hanging-fabric artefacts, and a light
face+hair paste-back on the full-body runs. **No fine-tuning / no training.**

- Best or tied on 10 of 11 categories across three test rounds; clear best on the 8 hardest.
- Only model that adds a matching blouse under the saree and renders the coat open.
- Self-hosted on one RTX 4090: **~8-11 s/image, ~Rs 0.16-0.20/image** — an order of magnitude
  inside both caps, no per-call vendor fee, no rate limit.
- **Known residual (accepted): coat on a male model.** IDM-VTON inpaints only the coat region,
  so with a casual base photo (polo) it cannot show the reference's white shirt + tie through
  the open front — the half-repainted polo reads as a dark top, and the face drifts slightly on
  the full-body mask. Fixes: (a) use a formal male base photo (shirt + tie + trousers) and
  re-run `coat` only (~$0.30), or (b) FLUX Pro VTO (prompt-directed, needs fal funding).
  `coat-w` (female) is unaffected.

**Fallback / high-throughput: CatVTON.** Fastest (5.8 s), cheapest (Rs 0.10), solid on menswear
+ simple tops, but no text lever -> weak on Indian wear, the black tee, and coats.

**Not recommended: Leffa.** Improved on jeans/trousers with the full-length base, but still
over-applies patterns (plaid -> full suit), barely applies plain tees, renders the coat closed,
and adds hanging-fabric artefacts. fal price ($0.10) is also over the Rs 4 cap.

**Not tested: FLUX Pro VTO, image-apps-v2** (hosted-only, fal account unfunded, $0 + locked).
Researched cost Rs 3.4 / Rs 3.5 -- just inside the cap. FLUX Pro is prompt-directed like the
IDM optimization and is the single biggest remaining quality lever (coat "open over shirt+tie",
saree pallu realism, the face-lock on full-body runs) -- fund fal with ~$5-10 to run it.
