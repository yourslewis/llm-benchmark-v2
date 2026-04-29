#!/usr/bin/env python3
"""Test OpenAI Codex provider models (openai-codex/gpt-5.4, openai-codex/gpt-5.3-codex).
These use OAuth auth, so we check if there's a cached token."""

import json, os, glob

# Check if there are any OpenAI Codex OAuth tokens cached
home = os.path.expanduser("~")
openclaw_dir = os.path.join(home, ".openclaw")

# Look for OAuth token files
print("Looking for OpenAI Codex OAuth tokens...")
for pattern in ["*codex*", "*openai*", "*oauth*", "*token*"]:
    matches = glob.glob(os.path.join(openclaw_dir, "**", pattern), recursive=True)
    for m in matches:
        if not "/node_modules/" in m and not "/extensions/" in m:
            print(f"  Found: {m}")

# The openai-codex provider uses OAuth flow - we can't easily test it 
# from a script without the OAuth token. Let's check if the config 
# references specific endpoints.
print("\nNote: openai-codex models use OAuth authentication managed by OpenClaw.")
print("These models (openai-codex/gpt-5.4, openai-codex/gpt-5.3-codex) can only")
print("be tested through the OpenClaw gateway itself, not directly from a script.")
print("\nThese models are listed in agents.defaults.models but NOT in models.providers,")
print("meaning they use the built-in openai-codex provider with OAuth.")
