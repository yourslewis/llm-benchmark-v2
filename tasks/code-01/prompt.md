Write a Python script that tests all models listed in a JSON config file by sending the prompt "Reply with exactly one word: OK" to each model via an OpenAI-compatible API at http://127.0.0.1:4000/v1/chat/completions.

Requirements:
1. Load model list from a JSON file passed as command-line argument
2. For each model, send the test prompt with max_tokens=20
3. Handle models that don't support the `temperature` parameter (skip it for those)
4. Set a 30-second timeout per request
5. Capture: model name, pass/fail status, response latency (seconds), response text (first 50 chars)
6. Print results as a formatted table with columns: Model, Status, Latency, Response
7. Print a summary line at the end: "Total: N models | ✅ X working | ❌ Y failed"
8. Use only Python standard library (urllib, json, time) — no pip packages
