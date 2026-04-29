# Task: Categorize Smoke Test Failures and Recommend Model Removals

## Background

You run a nightly smoke test against all configured LLM models. Each test sends a simple prompt and checks for a valid response. Below are the results from last night's run across 23 models.

## Smoke Test Results

| # | Model ID | Provider | Status | Error / Notes |
|---|----------|----------|--------|---------------|
| 1 | gpt-4o | openai | ✅ PASS | ttft=412ms |
| 2 | gpt-4o-mini | openai | ✅ PASS | ttft=287ms |
| 3 | gpt-4-turbo | openai | ✅ PASS | ttft=534ms |
| 4 | o1 | openai | ✅ PASS | ttft=8341ms |
| 5 | o3-mini | openai | ✅ PASS | ttft=1203ms |
| 6 | claude-opus-4 | anthropic | ✅ PASS | ttft=891ms |
| 7 | claude-sonnet-4 | anthropic | ✅ PASS | ttft=623ms |
| 8 | claude-haiku-3-5 | anthropic | ✅ PASS | ttft=198ms |
| 9 | gemini-2.0-flash | google | ✅ PASS | ttft=341ms |
| 10 | gemini-1.5-pro | google | ❌ FAIL | 404 Not Found — model deprecated |
| 11 | gemini-1.5-flash | google | ❌ FAIL | 404 Not Found — model deprecated |
| 12 | gpt-3.5-turbo | openai | ❌ FAIL | 404 Not Found — model deprecated |
| 13 | claude-2.1 | anthropic | ❌ FAIL | 404 Not Found — model deprecated |
| 14 | mistral-large | mistral | ✅ PASS | ttft=512ms |
| 15 | mistral-medium | mistral | ❌ FAIL | 401 Unauthorized — API key invalid or expired |
| 16 | codestral | mistral | ❌ FAIL | 401 Unauthorized — API key invalid or expired |
| 17 | llama-3.3-70b | groq | ✅ PASS | ttft=89ms |
| 18 | llama-3.1-8b | groq | ✅ PASS | ttft=67ms |
| 19 | deepseek-chat | deepseek | ❌ FAIL | 503 Service Unavailable — upstream down |
| 20 | deepseek-reasoner | deepseek | ❌ FAIL | 503 Service Unavailable — upstream down |
| 21 | qwen-turbo | alibaba | ❌ FAIL | Connection timeout after 30s |
| 22 | qwen-plus | alibaba | ❌ FAIL | Connection timeout after 30s |
| 23 | phi-3-mini | azure | ❌ FAIL | 400 Bad Request — invalid model name for this endpoint |

## Your Task

### 1. Categorize Failures

Group the 14 failing models by failure type. For each category:
- Name the category
- List which models fall into it
- Explain what the error means and what likely caused it

### 2. Prioritized Fix Plan

For each failure category, provide:
- **Immediate action:** What to do right now
- **Time estimate:** How long the fix should take
- **Owner:** Who should fix it (infra team, API team, etc.)

### 3. Removal Recommendations

Recommend which models to **permanently remove** from the configuration vs. which ones to **keep but fix**.

Use this table format:
| Model | Action | Reason |
|-------|--------|--------|
| gemini-1.5-pro | Remove | ... |
| deepseek-chat | Keep (fix) | ... |

### 4. Passing Model Notes

Among the 9 passing models, flag any concerns:
- Are any passing models unusually slow or worth reviewing?
- Any redundancy (multiple models from same provider doing the same thing)?

### 5. Summary

After your analysis, write a 3-sentence executive summary suitable for sharing with your team lead.
