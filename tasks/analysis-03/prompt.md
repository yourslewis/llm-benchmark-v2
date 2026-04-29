# Task: Review Model Token Limits and Recommend Config Corrections

## Background

Your AI gateway configuration has `maxTokens` set to **16,384** for all models. This was the default value when the config was first created, and nobody has updated it since. Some models support more tokens than this; others support less — meaning some are artificially limited and others are incorrectly configured.

## Current Configuration

| Model ID | Provider | Current maxTokens | 
|----------|----------|-------------------|
| gpt-4o | openai | 16384 |
| gpt-4o-mini | openai | 16384 |
| o3-mini | openai | 16384 |
| claude-opus-4 | anthropic | 16384 |
| claude-sonnet-4 | anthropic | 16384 |
| claude-haiku-3-5 | anthropic | 16384 |
| gemini-2.0-flash | google | 16384 |
| mistral-large | mistral | 16384 |
| llama-3.3-70b | groq | 16384 |
| phi-3-mini-128k | azure | 16384 |

## Your Task

### 1. Research & Correct

For each model, look up (or recall from knowledge) the **actual maximum output token limit** supported by the API, then fill in the table:

| Model ID | Actual Max Output Tokens | Current Setting | Recommended Setting | Action Needed |
|----------|--------------------------|-----------------|---------------------|---------------|
| gpt-4o | ? | 16384 | ? | Increase / Decrease / OK |
| ... | | | | |

**Notes on "Recommended Setting":**
- Set to the actual API maximum if it's higher than 16384 (you want to allow full output)
- Set to a practical limit if the actual max is very large (e.g., 1M tokens is rarely needed — cap at 32K or 64K)
- Set to the actual max if it's lower than 16384 (to avoid API errors)

### 2. Flag Dangerous Misconfiguration

Are any of these models set to a value **higher than their actual API limit**? If so, what would happen when a request tries to use the full 16384 tokens on those models?

### 3. Priority Order

Which corrections should be made first? Rank them by:
1. **Critical** — current setting will cause API errors
2. **Important** — current setting limits capability significantly
3. **Low priority** — close enough, minor adjustment

### 4. Config Snippet

Show what the corrected config block would look like for the **3 highest-priority models**, in this format:

```json
{
  "model": "model-id",
  "maxTokens": <corrected_value>,
  "reason": "Changed from 16384: actual API limit is X"
}
```
