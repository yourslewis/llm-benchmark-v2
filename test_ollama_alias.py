#!/usr/bin/env python3
"""Test Ollama with aliased OpenAI model names."""

import json, time, urllib.request

OLLAMA_OPENAI_URL = "http://127.0.0.1:11434/v1/embeddings"

for model in ["text-embedding-3-small", "text-embedding-3-large", "nomic-embed-text"]:
    payload = json.dumps({
        "model": model,
        "input": "Test embedding for OpenClaw memory search"
    }).encode()

    req = urllib.request.Request(OLLAMA_OPENAI_URL, data=payload, headers={"Content-Type": "application/json"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            elapsed = time.time() - start
            dim = len(data["data"][0]["embedding"]) if data.get("data") else 0
            print(f"{model:<30} ✅ {elapsed*1000:.0f}ms | dim={dim}")
    except Exception as e:
        print(f"{model:<30} ❌ {e}")
