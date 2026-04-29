#!/usr/bin/env python3
"""Re-test models that failed due to max_tokens=10 being too low."""

import json, time, urllib.request, urllib.error

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

MODELS = [
    "gpt-5.3-codex",
    "gpt-5.1",
    "gpt-5.2",
    "gpt-5.2-codex",
    "gpt-5.4",
    "gpt-5.4-mini",
]

for model in MODELS:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "max_tokens": 20,
        "temperature": 0,
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
            print(f"{model:<28} ✅ {elapsed:.1f}s  {text}")
    except Exception as e:
        elapsed = time.time() - start
        err = str(e)[:150]
        print(f"{model:<28} ❌ {elapsed:.1f}s  {err}")
