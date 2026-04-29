#!/usr/bin/env python3
"""Probe GitHub Copilot API for correct model slugs for missing models."""

import json, time, urllib.request, urllib.error

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

# Try various slug formats for the 4 missing models
CANDIDATES = [
    # GPT-4o variants
    "gpt-4o",
    # Gemini 3 Flash variants
    "gemini-3-flash-preview",
    "gemini-3.0-flash-preview",
    "gemini-3-flash",
    # Gemini 3.1 Pro variants
    "gemini-3.1-pro-preview",
    "gemini-3.1-pro",
    "gemini-3-pro-preview",
    # Goldeneye
    "goldeneye",
    "o3",
    "o4-mini",
]

for model in CANDIDATES:
    # Route through LiteLLM as github_copilot/ directly
    payload = json.dumps({
        "model": f"github_copilot/{model}",
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "max_tokens": 20,
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    req = urllib.request.Request(PROXY, data=payload, headers=headers)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            elapsed = time.time() - start
            text = body["choices"][0]["message"]["content"].strip()[:50]
            print(f"github_copilot/{model:<30} ✅ {elapsed:.1f}s  {text}")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        try:
            err_body = json.loads(e.read().decode())
            msg = err_body.get("error", {}).get("message", "")[:150]
        except:
            msg = str(e)[:150]
        print(f"github_copilot/{model:<30} ❌ {elapsed:.1f}s  {msg}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"github_copilot/{model:<30} ❌ {elapsed:.1f}s  {str(e)[:150]}")
