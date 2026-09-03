#!/usr/bin/env bash
# Re-create the Python env on a fresh pod that already has the network volume
# (repos + weights under /workspace/repos and /workspace/ckpts). Weights are NOT
# re-downloaded. ~5 min.
#
#   bash runpod/setup_deps.sh
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive PIP_BREAK_SYSTEM_PACKAGES=1 PIP_ROOT_USER_ACTION=ignore
PY=/usr/local/bin/python

echo "=== apt $(date -u +%T) ==="
apt-get update -y -qq && apt-get install -y -qq git-lfs ffmpeg libgl1 libglib2.0-0 build-essential tmux >/dev/null 2>&1 || echo "apt warnings"

echo "=== core deps $(date -u +%T) ==="
$PY -m pip -q install -U pip setuptools wheel
$PY -m pip -q install \
  "fastapi==0.115.*" "uvicorn[standard]" python-multipart pillow "huggingface_hub[cli]==0.25.2" \
  einops opencv-python-headless==4.10.0.84 scipy av tqdm cloudpickle omegaconf \
  numpy==1.26.4 "onnxruntime-gpu==1.18.1" scikit-image==0.24.0 matplotlib pycocotools fvcore \
  "diffusers==0.25.0" "transformers==4.36.2" "accelerate==0.26.1" 2>&1 | tail -3

echo "=== detectron2 (cu128 prebuilt wheel) $(date -u +%T) ==="
$PY -c "import detectron2" 2>/dev/null || $PY -m pip -q install \
  "https://github.com/MiroPsota/torch_packages_builder/releases/download/detectron2-0.6%2B18f6958/detectron2-0.6%2B18f6958pt2.8.0cu128-cp312-cp312-linux_x86_64.whl" 2>&1 | tail -3

echo "=== verify $(date -u +%T) ==="
$PY - <<'PY'
import torch, diffusers, transformers, onnxruntime, numpy, cv2, detectron2
print("torch", torch.__version__, "cuda", torch.cuda.is_available())
print("diffusers", diffusers.__version__, "transformers", transformers.__version__)
print("onnxruntime", onnxruntime.__version__, "numpy", numpy.__version__, "cv2", cv2.__version__)
print("detectron2", detectron2.__version__)
import os
print("repos:", os.listdir("/workspace/repos"))
print("ckpts:", os.listdir("/workspace/ckpts"))
PY
echo "=== DONE $(date -u +%T) ==="
