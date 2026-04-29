#!/usr/bin/env python3
"""Test Ollama embedding API with OpenAI-compatible endpoint."""

import json, time, urllib.request, urllib.error

OLLAMA_URL = "http://127.0.0.1:11434/api/embed"
OLLAMA_OPENAI_URL = "http://127.0.0.1:11434/v1/embeddings"

# Test 1: Ollama native API
print("=== Test 1: Ollama native API ===")
payload = json.dumps({
    "model": "nomic-embed-text",
    "input": "Hello world, this is a test of local embeddings"
}).encode()

req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
start = time.time()
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        elapsed = time.time() - start
        embeddings = data.get("embeddings", [])
        dim = len(embeddings[0]) if embeddings else 0
        print(f"  ✅ {elapsed*1000:.0f}ms | dim={dim} | model=nomic-embed-text")
except Exception as e:
    print(f"  ❌ {e}")

# Test 2: OpenAI-compatible API (what OpenClaw uses)
print("\n=== Test 2: OpenAI-compatible API ===")
payload = json.dumps({
    "model": "nomic-embed-text",
    "input": "Hello world, this is a test of local embeddings"
}).encode()

req = urllib.request.Request(OLLAMA_OPENAI_URL, data=payload, headers={"Content-Type": "application/json"})
start = time.time()
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        elapsed = time.time() - start
        dim = len(data["data"][0]["embedding"]) if data.get("data") else 0
        print(f"  ✅ {elapsed*1000:.0f}ms | dim={dim} | model=nomic-embed-text")
except Exception as e:
    print(f"  ❌ {e}")

# Test 3: OpenAI-compatible API with model name "text-embedding-3-small"
# This tests if we can alias/trick OpenClaw into thinking it's the OpenAI model
print("\n=== Test 3: Using 'text-embedding-3-small' model name ===")
payload = json.dumps({
    "model": "text-embedding-3-small",
    "input": "Hello world, this is a test of local embeddings"
}).encode()

req = urllib.request.Request(OLLAMA_OPENAI_URL, data=payload, headers={"Content-Type": "application/json"})
start = time.time()
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        elapsed = time.time() - start
        dim = len(data["data"][0]["embedding"]) if data.get("data") else 0
        print(f"  ✅ {elapsed*1000:.0f}ms | dim={dim}")
except urllib.error.HTTPError as e:
    err = e.read().decode()[:200]
    print(f"  ❌ {err}")

# Test 4: Batch embedding (multiple inputs)
print("\n=== Test 4: Batch embedding (5 inputs) ===")
payload = json.dumps({
    "model": "nomic-embed-text",
    "input": [
        "First test sentence",
        "Second test sentence", 
        "Third test sentence about AI models",
        "Fourth test about embeddings",
        "Fifth test about vector databases"
    ]
}).encode()

req = urllib.request.Request(OLLAMA_OPENAI_URL, data=payload, headers={"Content-Type": "application/json"})
start = time.time()
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        elapsed = time.time() - start
        count = len(data.get("data", []))
        dim = len(data["data"][0]["embedding"]) if data.get("data") else 0
        print(f"  ✅ {elapsed*1000:.0f}ms | {count} embeddings | dim={dim}")
except Exception as e:
    print(f"  ❌ {e}")
