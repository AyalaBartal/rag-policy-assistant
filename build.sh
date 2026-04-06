#!/usr/bin/env bash
set -e

pip install -r requirements.txt

# Pre-download the ONNX embedding model during build so it's cached
# before the app starts. Without this, the first worker startup blocks
# for 3-5 minutes downloading 79MB while health checks time out.
echo "Pre-downloading ONNX embedding model..."
python3 -c "
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
ef = ONNXMiniLM_L6_V2(preferred_providers=['CPUExecutionProvider'])
ef(['warmup'])
print('ONNX model ready.')
"
