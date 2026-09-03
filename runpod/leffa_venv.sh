#!/usr/bin/env bash
# Isolated venv for Leffa on the pod. Leffa vendors a ~diffusers-0.27 UNet that
# conflicts with the diffusers 0.25 IDM-VTON needs, so it gets its own env.
# Inherits torch / torchvision / detectron2 from the system site-packages.
#
#   bash runpod/leffa_venv.sh
#   (cd runpod && /workspace/venv_leffa/bin/python leffa_server.py)   # serves :8000
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
V=/workspace/venv_leffa
[ -d "$V" ] || python -m venv "$V" --system-site-packages
source "$V/bin/activate"
pip -q install -U pip
pip -q install "diffusers==0.31.0" "transformers==4.44.2" "accelerate==0.34.2" \
  "huggingface_hub==0.25.2" "fastapi==0.115.*" "uvicorn[standard]" python-multipart \
  pillow einops onnxruntime-gpu==1.18.1 numpy==1.26.4 opencv-python-headless==4.10.0.84 \
  scipy scikit-image==0.24.0 2>&1 | tail -3
python - <<'PY'
import torch, diffusers, transformers, detectron2
print("venv_leffa: torch", torch.__version__, "cuda", torch.cuda.is_available(),
      "diffusers", diffusers.__version__, "transformers", transformers.__version__,
      "detectron2", detectron2.__version__)
PY
echo "=== LEFFA VENV DONE ==="
