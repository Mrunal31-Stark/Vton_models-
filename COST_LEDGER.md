# Cost Ledger — hard cap $10.00

Keep every RunPod invoice + fal usage export for reimbursement (payable only if selected).

| Date | Item | Detail | USD |
|------|------|--------|-----|
| 2026-09-02 | RunPod credit | pre-loaded (not a spend) | +15.00 |
| 2026-09-02 | RunPod RTX 4090 (secure, EU-RO-1) + 70 GB network volume | 4 pods on 1 network volume across **3 test rounds**: env setup ×4, smoke tests, IDM-VTON baseline + optimized (+ prompt/mask iteration), CatVTON, Leffa (isolated venv). R1 = 10 categories; R2 = 11 (full-body models, coat on both); R3 = menswear re-run on a casual full-length male + coat/prompt tuning. ~4.3 pod-hr total. | **~3.16** |
| — | fal.ai (FLUX Pro VTO, image-apps-v2) | account unfunded ($0, locked) → **not tested, $0** | 0.00 |
| | | **TOTAL TESTING SPEND** | **~3.16** |

Verified against RunPod balance: **$15.00 → $11.84 = $3.16 actual** (3 rounds). ~32% of the $10 cap.

## Per-generation unit cost (the number the assignment asks for)

GPU-seconds only, on one RTX 4090 @ $0.74/hr (Rs 65/hr):

| model | gen time | cost/img |
|-------|---------:|---------:|
| CatVTON | 5.6 s | Rs 0.10 |
| Leffa (self-host) | 6.6 s | Rs 0.12 |
| IDM-VTON baseline | 6.8 s | Rs 0.12 |
| IDM-VTON optimized | 7.7–8.6 s | Rs 0.14–0.16 |

All **far** inside the Rs 4 / 15 s caps. Even at a hosted 4090 rate ($1.10/hr serverless) the
worst case is ~Rs 0.25/img. `results/log.csv` has the per-run `cost_usd` / `cost_inr` columns;
`run_tryon.py` auto-halts if cumulative spend ever hits $10.

## Not tested (hosted-only, fal account unfunded)

| model | researched price | vs Rs 4 cap |
|-------|------------------|-------------|
| FLUX Pro VTO (`fal-ai/flux-pro/v1/vto`) | $0.0375/MP ≈ Rs 3.4 | just under |
| image-apps-v2 (`fal-ai/image-apps-v2/virtual-try-on`) | $0.04 ≈ Rs 3.5 | just under |
| Leffa on fal (`fal-ai/leffa/virtual-tryon`) | $0.10 ≈ Rs 8.8 | **over** (self-hosted instead) |
