#!/usr/bin/env python3
"""Check raw Responses API output format for Azure models."""
import json, urllib.request, subprocess, sys

def get_secret(sid):
    r = subprocess.run(
        ["/opt/homebrew/Cellar/node/25.8.0/bin/node",
         "/Users/yourslewis/.openclaw/extensions/clawguard/bin/clawguard-vault-get.mjs", sid],
        capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

MODELS = [
    ("gpt-5.4-pro", "https://yours-mlk2lgx7-eastus2.cognitiveservices.azure.com/openai/v1/responses", "models.apiKey.azure"),
    ("gpt-5.3-codex", "https://yours-mlk2lgx7-eastus2.cognitiveservices.azure.com/openai/v1/responses", "models.apiKey.azure"),
    ("gpt-5.1-codex-mini", "https://yours-mlw8x303-uksouth.cognitiveservices.azure.com/openai/v1/responses", "models.apiKey.azure-mini"),
]

for model, endpoint, secret_id in MODELS:
    print(f"\n{'='*60}")
    print(f"Model: {model}")
    print(f"{'='*60}")
    
    key = get_secret(secret_id)
    body = json.dumps({"model": model, "input": "What is 2+2? Reply in one sentence.", "max_output_tokens": 100}).encode()
    headers = {"Content-Type": "application/json", "api-key": key}
    req = urllib.request.Request(endpoint, data=body, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            
            print(f"Top-level output_text: {repr(data.get('output_text', ''))}")
            print(f"Top-level text: {repr(data.get('text', ''))}")
            print(f"Output type: {type(data.get('output'))}")
            print()
            
            output = data.get("output", [])
            for i, item in enumerate(output):
                if isinstance(item, dict):
                    print(f"  output[{i}]:")
                    print(f"    type: {item.get('type')}")
                    print(f"    role: {item.get('role', 'N/A')}")
                    content = item.get("content")
                    if content is None:
                        print(f"    content: None")
                    elif isinstance(content, list):
                        for j, c in enumerate(content):
                            if isinstance(c, dict):
                                print(f"    content[{j}]: type={c.get('type')}, text={repr(c.get('text','')[:100])}")
                            else:
                                print(f"    content[{j}]: {repr(str(c)[:100])}")
                    elif isinstance(content, str):
                        print(f"    content: {repr(content[:100])}")
                    # Check for other keys
                    other_keys = [k for k in item.keys() if k not in ('type', 'role', 'content', 'id', 'status', 'phase', 'summary')]
                    if other_keys:
                        print(f"    other keys: {other_keys}")
    except Exception as e:
        print(f"  ERROR: {e}")
