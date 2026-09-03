# Step 1 — Market research (Sept 2026)

Budget: Rs 4/gen ≈ **$0.045/image**. Speed: **< 15 s**.

## Commercial / hosted APIs

| Model / API | $/image | Speed | Res | Notes | In budget? |
|---|---|---|---|---|---|
| FASHN v1.6 | 0.075 (→<0.04 at volume) | 5–10 s | 864×1296 | best text/print fidelity; lower-body mixed | ✗ at low volume |
| Kling Kolors v1.5 | 0.07 | seconds | var | holds pose/skin/body; flattens fabric detail sometimes | ✗ |
| Google Nano Banana Pro (Gemini Flash Image) | ~0.06–0.14 | seconds | high | prompt-driven, natural composites, non-deterministic | ✗ |
| FLUX Virtual Try-On Pro (fal) | 0.0375/MP | 5–10 s | var | styling prompts; held dress colour well | ✓ borderline |
| image-apps-v2 (fal) | 0.04 | ~10 s | ≤4K | simple 2-image, full-length placement | ✓ |
| Flux 2 LoRA try-on (fal) | 0.021/MP | ~10 s | var | lora_scale transfer strength | ✓ |
| Leffa (fal) | 0.10 | ~8 s | var | commercial-cleared; explicit garment type | ✗ (but free self-hosted) |

## Open-source (self-host on RunPod — the way to hit Rs 4)

| Model | Repo | Self-host $/img* | Speed | Notes |
|---|---|---|---|---|
| IDM-VTON | yisol/IDM-VTON (ECCV'24, 4.6k★) | ~0.002 | 10–15 s | strong upper body/dresses; **weak saree/kurti OOTB** |
| CatVTON | Zheng-Chong/CatVTON | ~0.001 | 5–8 s | lightweight, fast, fewer params |
| Leffa | franciszzj/Leffa (Meta) | ~0.003 | 8–12 s | upper/lower/dress mode, best pose preservation |
| OOTDiffusion | levihsu/OOTDiffusion | ~0.002 | ~10 s | half/full-body modes; backup |
| Kolors-VTON weights | Kwai-Kolors | ~0.003 | ~8 s | open weights of Kling model; backup |

*RTX 4090 ≈ $0.40–0.70/hr on RunPod community → fractions of a cent at ~10 s/image.

## Sources
- fal.ai — 10 Best Virtual Try-On APIs 2026: https://fal.ai/learn/tools/best-virtual-try-on-apis-2026
- FASHN — Top 4 Open Source VITON Models: https://fashn.ai/blog/comparing-the-top-4-open-source-virtual-try-on-viton-models
- ionio.ai — VTON models compared: https://www.ionio.ai/blog/vton
- pixazo — Best Try-On APIs 2026: https://www.pixazo.ai/blog/best-virtual-try-on-api
- fal model pages: fal-ai/leffa/virtual-tryon, fal-ai/kling/v1-5/kolors-virtual-try-on, fal-ai/fashn/tryon/v1.5
