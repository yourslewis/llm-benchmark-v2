#!/usr/bin/env python3
"""Re-test gpt-5.1, gpt-5.2, gpt-5.2-codex without temperature."""

import json, urllib.request, urllib.error, time

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

for model in ["gpt-5.1", "gpt-5.2", "gpt-5.2-codex"]:
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
            print(f"{model:<28} ✅ {elapsed:.1f}s  {text}")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        err = e.read().decode()[:300]
        print(f"{model:<28} ❌ {elapsed:.1f}s  {err}")
