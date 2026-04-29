#!/usr/bin/env python3
"""Test goldeneye after Responses API switch."""

import json, time, urllib.request, urllib.error

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

payload = json.dumps({
    "model": "goldeneye",
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
        text = body["choices"][0]["message"]["content"].strip()[:80]
        print(f"goldeneye  ✅ {elapsed:.1f}s  {text}")
except urllib.error.HTTPError as e:
    elapsed = time.time() - start
    err = e.read().decode()[:400]
    print(f"goldeneye  ❌ {elapsed:.1f}s  {err}")
