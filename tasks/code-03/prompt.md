# Task: Build a Multi-API Benchmark Harness with Streaming TTFT Measurement

## Overview

Build a Python command-line benchmark harness that tests LLM models across two API formats and measures **Time-To-First-Token (TTFT)** via SSE streaming.

## Requirements

### API Support
The harness must support **two API formats**:

1. **Chat Completions API** (`/v1/chat/completions`)
   - Request body: `{ "model": "...", "messages": [...], "stream": true, ... }`
   - SSE stream format: `data: {"choices": [{"delta": {"content": "..."}}]}`

2. **Responses API** (`/v1/responses`)
   - Request body: `{ "model": "...", "input": "...", "stream": true, ... }`
   - SSE stream format: `data: {"type": "content_block_delta", "delta": {"text": "..."}}`

### Per-Model Configuration
Load model config from a JSON file. Each model entry supports:
```json
{
  "models": [
    {
      "id": "gpt-4o",
      "api_type": "chat_completions",
      "base_url": "https://api.openai.com",
      "api_key_env": "OPENAI_API_KEY",
      "temperature": 0.7,
      "max_tokens": 100
    },
    {
      "id": "claude-sonnet-4",
      "api_type": "responses",
      "base_url": "https://api.anthropic.com",
      "api_key_env": "ANTHROPIC_API_KEY",
      "temperature": 1.0,
      "max_tokens": 200
    }
  ]
}
```

### TTFT Measurement
- Send request with `stream: true`
- Record `t_start` immediately before the HTTP request
- Parse the SSE stream; record `t_first_token` when the **first non-empty content delta** arrives
- `TTFT = t_first_token - t_start` (in milliseconds)
- Also record total response time (until stream ends)

### Benchmark Prompt
Use a fixed prompt for all models:
> "Reply with exactly one sentence about the color blue."

### Output
Save results to `benchmark_results.json` with this structure:
```json
{
  "run_id": "<uuid>",
  "timestamp": "<ISO datetime>",
  "prompt": "Reply with exactly one sentence about the color blue.",
  "results": [
    {
      "model_id": "gpt-4o",
      "api_type": "chat_completions",
      "status": "ok",
      "ttft_ms": 312.4,
      "total_ms": 1847.2,
      "first_token": "Blue",
      "full_response": "Blue is the color of a clear sky on a sunny day.",
      "error": null
    },
    {
      "model_id": "bad-model",
      "api_type": "chat_completions",
      "status": "error",
      "ttft_ms": null,
      "total_ms": 5001.0,
      "first_token": null,
      "full_response": null,
      "error": "Connection timeout after 5000ms"
    }
  ],
  "summary": {
    "total": 2,
    "ok": 1,
    "errors": 1,
    "avg_ttft_ms": 312.4,
    "fastest_model": "gpt-4o",
    "slowest_model": "gpt-4o"
  }
}
```

### CLI Interface
```
python benchmark.py --config models.json [--output results.json] [--timeout 10] [--workers 4]
```

- `--config`: Path to model config JSON (required)
- `--output`: Output file path (default: `benchmark_results.json`)
- `--timeout`: Per-model timeout in seconds (default: 30)
- `--workers`: Parallel workers using `concurrent.futures.ThreadPoolExecutor` (default: 1)

### Error Handling
- Catch timeouts, connection errors, HTTP errors, and JSON parse errors
- Record error in result but continue to next model
- Never crash the whole harness due to one model failing

### Constraints
- **Use only Python stdlib** — no `requests`, `httpx`, `aiohttp`, `sseclient`, etc.
- Use `urllib.request` for HTTP
- Parse SSE stream manually (lines starting with `data: `)
- Use `concurrent.futures.ThreadPoolExecutor` for parallelism
- Target Python 3.9+

## Deliverable

Return a single Python file `benchmark.py` that implements all requirements above.
