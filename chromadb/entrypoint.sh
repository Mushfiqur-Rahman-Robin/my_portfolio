#!/bin/bash

echo "Rebuilding hnsw to ensure architecture compatibility (version pinned)"
pip install --force-reinstall --no-cache-dir chroma-hnswlib==0.7.3 "numpy<2"
export IS_PERSISTENT=1
uvicorn chromadb.app:app --workers 1 --host 0.0.0.0 --port 8000 --proxy-headers --log-config chromadb/log_config.yml
