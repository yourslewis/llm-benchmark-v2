#!/usr/bin/env python3
"""Test the 4 newly added models after config change."""

import json, time, urllib.request, urllib.error

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

MODELS = ["gpt-4o", "gemini-3-flash-preview", "gemini-3.1-pro-preview", "goldeneye"]

for model in MODELS:
    payload = json.dumps({
        "model": model,
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
            print(f"{model:<30} ✅ {elapsed:.1f}s  {text}")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        try:
            err = e.read().decode()[:300]
        except:
            err = str(e)
        print(f"{model:<30} ❌ {elapsed:.1f}s  {err}")
