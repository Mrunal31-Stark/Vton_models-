#!/usr/bin/env bash
# Bootstrap a RunPod pod (PyTorch 2.4 / CUDA 12.1 template, RTX 4090 24GB) with
# IDM-VTON, Leffa and CatVTON + the eval server.
#
#   bash runpod/setup.sh
#   python runpod/server.py          # serves on :8000, expose via RunPod proxy
set -euo pipefail

WORK=/workspace
mkdir -p "$WORK/repos" "$WORK/ckpts"
cd "$WORK/repos"

apt-get update -y && apt-get install -y git-lfs ffmpeg libgl1 && git lfs install

# ---- repos ---------------------------------------------------------------
[ -d IDM-VTON ] || git clone https://github.com/yisol/IDM-VTON.git
[ -d Leffa ]    || git clone https://github.com/franciszzj/Leffa.git
[ -d CatVTON ]  || git clone https://github.com/Zheng-Chong/CatVTON.git

# ---- python deps -------------------------------------------------------
pip install -U pip
pip install "fastapi==0.115.*" "uvicorn[standard]==0.30.*" python-multipart pillow
pip install diffusers==0.25.0 transformers==4.36.2 accelerate==0.25.0 \
            einops onnxruntime-gpu opencv-python-headless scipy \
            huggingface_hub==0.25.2 config==0.5.1 torchvision

# ---- weights ----------------------------------------------------------
# IDM-VTON (full pipeline incl. densepose / humanparsing helpers)
huggingface-cli download yisol/IDM-VTON --local-dir "$WORK/ckpts/IDM-VTON" --exclude "*.md"
# CatVTON
huggingface-cli download zhengchong/CatVTON --local-dir "$WORK/ckpts/CatVTON"
# Leffa
huggingface-cli download franciszzj/Leffa --local-dir "$WORK/ckpts/Leffa"

echo "setup done. run: python runpod/server.py"
