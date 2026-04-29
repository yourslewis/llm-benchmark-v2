#!/usr/bin/env python3
"""Update maxTokens for all models in openclaw.json to their real limits.
Also remove dead models (gpt-5.1-codex, gpt-5.1-codex-max, gpt-5.1-codex-mini)."""

import json

CONFIG_PATH = "/Users/yourslewis/.openclaw/openclaw.json"

# Correct maxTokens per model ID
MAX_TOKENS_MAP = {
    # Claude models
    "claude-opus-4-6-1m": 128000,
    "claude-opus-4-6": 128000,
    "claude-sonnet-4-6": 64000,
    "claude-haiku-4-5": 64000,
    "claude-opus-4-5": 64000,
    "claude-sonnet-4-5": 64000,
    "claude-sonnet-4": 64000,
    # GPT-5 family
    "gpt-5.3-codex": 128000,
    "gpt-5.4": 128000,
    "gpt-5.4-mini": 128000,
    "gpt-5.4-pro": 128000,
    "gpt-5.1": 128000,
    "gpt-5.2": 128000,
    "gpt-5.2-codex": 128000,
    "gpt-5-mini": 128000,
    # GPT-4 family
    "gpt-4.1": 32768,
    "gpt-4o": 16384,
    # Gemini
    "gemini-2.5-pro": 65535,
    "gemini-3-flash-preview": 65535,
    "gemini-3.1-pro-preview": 65535,
    # Other
    "goldeneye": 128000,
    # Azure models (same IDs)
    "gpt-5.1-codex-mini": 128000,
}

# Dead models to remove from copilot provider
DEAD_MODELS = {"gpt-5.1-codex", "gpt-5.1-codex-max", "gpt-5.1-codex-mini"}

with open(CONFIG_PATH) as f:
    config = json.load(f)

changes = []

for provider_name, provider in config.get("models", {}).get("providers", {}).items():
    if "models" not in provider:
        continue
    
    # Remove dead models (only from copilot provider)
    if provider_name == "copilot":
        original_count = len(provider["models"])
        provider["models"] = [m for m in provider["models"] if m["id"] not in DEAD_MODELS]
        removed = original_count - len(provider["models"])
        if removed:
            changes.append(f"Removed {removed} dead model(s) from {provider_name}")
    
    # Update maxTokens
    for model in provider["models"]:
        model_id = model["id"]
        if model_id in MAX_TOKENS_MAP:
            old = model.get("maxTokens")
            new = MAX_TOKENS_MAP[model_id]
            if old != new:
                model["maxTokens"] = new
                changes.append(f"{provider_name}/{model_id}: {old} -> {new}")

# Also remove dead models from agents.defaults.models
defaults_models = config.get("agents", {}).get("defaults", {}).get("models", {})
for dead in DEAD_MODELS:
    key = f"copilot/{dead}"
    if key in defaults_models:
        del defaults_models[key]
        changes.append(f"Removed {key} from agents.defaults.models")

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)

print(f"\n{len(changes)} changes applied:")
for c in changes:
    print(f"  ✅ {c}")
