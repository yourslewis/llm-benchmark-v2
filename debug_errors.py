#!/usr/bin/env python3
"""Check what error gpt-5.1, gpt-5.2, gpt-5.2-codex return."""

import json, urllib.request, urllib.error

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

for model in ["gpt-5.1", "gpt-5.2", "gpt-5.2-codex"]:
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
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"{model}: OK")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"{model}: {body}\n")
