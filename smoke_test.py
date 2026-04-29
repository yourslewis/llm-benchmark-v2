#!/usr/bin/env python3
"""Quick smoke test: hit every model via LiteLLM proxy with a tiny prompt."""

import json, time, urllib.request, urllib.error, sys

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

MODELS = [
    # Copilot/LiteLLM models
    "claude-opus-4-6-1m",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "claude-opus-4-5",
    "claude-sonnet-4-5",
    "claude-sonnet-4",
    "gpt-5.3-codex",
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "goldeneye",
    "gpt-4.1",
    "gpt-4o",
    "gpt-5-mini",
    "gpt-5.1",
    "gpt-5.1-codex",
    "gpt-5.1-codex-max",
    "gpt-5.1-codex-mini",
    "gpt-5.2",
    "gpt-5.2-codex",
    "gpt-5.4",
    "gpt-5.4-mini",
]

results = []

for model in MODELS:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "max_tokens": 10,
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
            tokens = body.get("usage", {}).get("total_tokens", "?")
            results.append((model, "✅", f"{elapsed:.1f}s", text, tokens))
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        try:
            err_body = e.read().decode()[:200]
        except:
            err_body = str(e)
        results.append((model, "❌", f"{elapsed:.1f}s", err_body, "-"))
    except Exception as e:
        elapsed = time.time() - start
        results.append((model, "❌", f"{elapsed:.1f}s", str(e)[:200], "-"))

# Print results
print(f"\n{'Model':<28} {'Status':<4} {'Time':<7} {'Tokens':<8} {'Response'}")
print("-" * 100)
for model, status, elapsed, text, tokens in results:
    print(f"{model:<28} {status:<4} {elapsed:<7} {str(tokens):<8} {text}")

ok = sum(1 for r in results if r[1] == "✅")
fail = sum(1 for r in results if r[1] == "❌")
print(f"\n{'='*50}")
print(f"Total: {len(results)} models | ✅ {ok} working | ❌ {fail} failed")
