#!/usr/bin/env python3
"""Test Azure models (direct, not via LiteLLM) and OpenAI Codex models."""

import json, time, urllib.request, urllib.error, subprocess, os

def get_secret(secret_id):
    """Get secret from clawguard vault."""
    result = subprocess.run(
        ["/opt/homebrew/Cellar/node/25.8.0/bin/node",
         "/Users/yourslewis/.openclaw/extensions/clawguard/bin/clawguard-vault-get.mjs",
         secret_id],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout.strip()

# Azure East US 2 (gpt-5.4-pro, gpt-5.3-codex, gpt-image-1)
azure_key = get_secret("models.apiKey.azure")
azure_base = "https://yours-mlk2lgx7-eastus2.cognitiveservices.azure.com/openai/v1"

# Azure UK South (gpt-5.1-codex-mini)  
azure_mini_key = get_secret("models.apiKey.azure-mini")
azure_mini_base = "https://yours-mlw8x303-uksouth.cognitiveservices.azure.com/openai/v1"

TESTS = [
    # (name, base_url, api_key, model_id, use_responses_api)
    ("azure/gpt-5.4-pro", azure_base, azure_key, "gpt-5.4-pro", True),
    ("azure/gpt-5.3-codex", azure_base, azure_key, "gpt-5.3-codex", True),
    ("azure/gpt-image-1", azure_base, azure_key, "gpt-image-1", True),
    ("azure-mini/gpt-5.1-codex-mini", azure_mini_base, azure_mini_key, "gpt-5.1-codex-mini", True),
]

for name, base_url, api_key, model, use_responses in TESTS:
    if use_responses:
        # OpenAI Responses API format
        url = f"{base_url}/responses"
        payload = json.dumps({
            "model": model,
            "input": "Reply with exactly: OK",
            "max_output_tokens": 20,
        }).encode()
    else:
        # Chat completions format
        url = f"{base_url}/chat/completions"
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
            "max_tokens": 20,
        }).encode()

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    req = urllib.request.Request(url, data=payload, headers=headers)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
            elapsed = time.time() - start
            # Responses API returns different structure
            if use_responses:
                output = body.get("output_text", str(body.get("output", ""))[:80])
            else:
                output = body["choices"][0]["message"]["content"].strip()[:80]
            print(f"{name:<35} ✅ {elapsed:.1f}s  {output[:50]}")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        try:
            err = e.read().decode()[:300]
        except:
            err = str(e)
        print(f"{name:<35} ❌ {elapsed:.1f}s  {err}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"{name:<35} ❌ {elapsed:.1f}s  {str(e)[:300]}")
