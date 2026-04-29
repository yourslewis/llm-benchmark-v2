# Task: Write a Python Script to Fix OpenClaw maxTokens Misconfiguration

## Background

The OpenClaw AI gateway stores its model configuration in a JSON file. All models currently have `maxTokens` set to `16384` — a leftover default that hasn't been updated. For models where 16384 exceeds the actual API limit, requests that try to use the full token budget will fail with API errors.

## Current Config File Format

The config file (`~/.openclaw/config.json`) has this structure:

```json
{
  "version": "2.1",
  "models": [
    {
      "id": "gpt-4o",
      "provider": "openai",
      "maxTokens": 16384,
      "temperature": 0.7,
      "enabled": true
    },
    {
      "id": "claude-sonnet-4",
      "provider": "anthropic",
      "maxTokens": 16384,
      "temperature": 1.0,
      "enabled": true
    }
  ],
  "routing": {
    "default": "gpt-4o",
    "fallback": "claude-sonnet-4"
  }
}
```

## Correct Token Limits

Use this table of actual API output token limits:

| Model ID | Actual Max Output Tokens |
|----------|--------------------------|
| gpt-4o | 16384 |
| gpt-4o-mini | 16384 |
| o3-mini | 65536 |
| claude-opus-4 | 8096 |
| claude-sonnet-4 | 8096 |
| claude-haiku-3-5 | 8096 |
| gemini-2.0-flash | 8192 |
| mistral-large | 131072 |
| llama-3.3-70b | 8192 |
| phi-3-mini-128k | 4096 |

## Your Task

Write a Python script `fix_max_tokens.py` that:

### 1. Loads the config file
- Accept config file path as first argument (`sys.argv[1]`)
- If no argument, default to `~/.openclaw/config.json`
- Handle `FileNotFoundError` gracefully

### 2. Applies the corrections
Define the correct limits as a dictionary inside the script:
```python
CORRECT_LIMITS = {
    "gpt-4o": 16384,
    "gpt-4o-mini": 16384,
    # ... etc
}
```

For each model in the config:
- If the model ID is in `CORRECT_LIMITS` and `maxTokens` differs from the correct value → update it
- If the model ID is NOT in `CORRECT_LIMITS` → skip it with a warning
- Track how many models were changed vs. skipped

### 3. Dry-run mode
If `--dry-run` flag is passed, print what would change but don't write to disk.

### 4. Output
```
Checking 10 models...
  gpt-4o: 16384 → 16384 (no change)
  claude-opus-4: 16384 → 8096 (UPDATED)
  claude-sonnet-4: 16384 → 8096 (UPDATED)
  mistral-large: 16384 → 131072 (UPDATED)
  ...

Summary: 6 updated, 4 unchanged, 0 skipped
Config saved to: ~/.openclaw/config.json
```

### 5. Backup
Before writing, create a backup of the original file at `<original_path>.bak`.

### 6. Constraints
- Use only Python stdlib
- Handle JSON parse errors
- The script must not modify any keys other than `maxTokens`
- Preserve JSON formatting (use `indent=2`)

## Deliverable

Return a single Python script `fix_max_tokens.py` that implements all requirements above.
