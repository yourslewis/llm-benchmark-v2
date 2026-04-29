#!/usr/bin/env python3
"""Final smoke test: all working models via LiteLLM + Azure direct."""

import json, time, urllib.request, urllib.error, subprocess

PROXY = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "dummy-key"

def get_secret(secret_id):
    result = subprocess.run(
        ["/opt/homebrew/Cellar/node/25.8.0/bin/node",
         "/Users/yourslewis/.openclaw/extensions/clawguard/bin/clawguard-vault-get.mjs",
         secret_id],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout.strip()

# LiteLLM models: (name, needs_no_temperature)
LITELLM_MODELS = [
    ("claude-opus-4-6-1m", False),
    ("claude-opus-4-6", False),
    ("claude-sonnet-4-6", False),
    ("claude-haiku-4-5", False),
    ("claude-opus-4-5", False),
    ("claude-sonnet-4-5", False),
    ("claude-sonnet-4", False),
    ("gpt-5.3-codex", True),
    ("gpt-5.4", True),
    ("gpt-5.4-mini", True),
    ("gpt-5.1", True),
    ("gpt-5.2", True),
    ("gpt-5.2-codex", True),
    ("gemini-2.5-pro", False),
    ("gemini-3-flash-preview", False),
    ("gemini-3.1-pro-preview", False),
    ("goldeneye", True),
    ("gpt-4.1", False),
    ("gpt-4o", False),
    ("gpt-5-mini", False),
]

results = []

print("Testing LiteLLM models...")
for model, no_temp in LITELLM_MODELS:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "max_tokens": 20,
    }
    if not no_temp:
        body["temperature"] = 0

    payload = json.dumps(body).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    req = urllib.request.Request(PROXY, data=payload, headers=headers)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            elapsed = time.time() - start
            text = data["choices"][0]["message"]["content"].strip()[:30]
            results.append(("copilot", model, "✅", f"{elapsed:.1f}s", text))
    except Exception as e:
        elapsed = time.time() - start
        results.append(("copilot", model, "❌", f"{elapsed:.1f}s", str(e)[:80]))

# Azure direct models
print("Testing Azure models...")
azure_key = get_secret("models.apiKey.azure")
azure_mini_key = get_secret("models.apiKey.azure-mini")

AZURE_MODELS = [
    ("azure", "gpt-5.4-pro", "https://yours-mlk2lgx7-eastus2.cognitiveservices.azure.com/openai/v1/responses", azure_key),
    ("azure", "gpt-5.3-codex", "https://yours-mlk2lgx7-eastus2.cognitiveservices.azure.com/openai/v1/responses", azure_key),
    ("azure-mini", "gpt-5.1-codex-mini", "https://yours-mlw8x303-uksouth.cognitiveservices.azure.com/openai/v1/responses", azure_mini_key),
]

for provider, model, url, key in AZURE_MODELS:
    payload = json.dumps({
        "model": model,
        "input": "Reply with exactly: OK",
        "max_output_tokens": 20,
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "api-key": key,
    }

    req = urllib.request.Request(url, data=payload, headers=headers)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            elapsed = time.time() - start
            output = data.get("output_text", str(data.get("output", ""))[:30])[:30]
            results.append((provider, model, "✅", f"{elapsed:.1f}s", output))
    except Exception as e:
        elapsed = time.time() - start
        results.append((provider, model, "❌", f"{elapsed:.1f}s", str(e)[:80]))

# Print results
print(f"\n{'Provider':<12} {'Model':<28} {'Status':<4} {'Time':<7} {'Response'}")
print("-" * 90)
for provider, model, status, elapsed, text in results:
    print(f"{provider:<12} {model:<28} {status:<4} {elapsed:<7} {text}")

ok = sum(1 for r in results if r[2] == "✅")
fail = sum(1 for r in results if r[2] == "❌")
print(f"\n{'='*50}")
print(f"Total: {len(results)} models | ✅ {ok} working | ❌ {fail} failed")
