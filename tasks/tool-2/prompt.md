You are debugging a multi-tool workflow that failed. Here is the transcript of 3 failed tool calls:

**Call 1 — Rate Limited:**
```
Tool: web_search
Input: {"query": "OpenClaw changelog April 2026", "count": 5}
Error: HTTP 429 Too Many Requests
Headers: {"Retry-After": "30", "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1713470400"}
```

**Call 2 — Schema Mismatch:**
```
Tool: file_write
Input: {"path": "/tmp/report.md", "contents": "# Report\n..."}
Error: ValidationError - Unknown field 'contents'. Did you mean 'content'?
Schema: {"path": "string (required)", "content": "string (required)", "mode": "string (optional, default: 'overwrite')"}
```

**Call 3 — Timeout:**
```
Tool: exec
Input: {"command": "python3 analyze.py --input data.csv --output results.json", "timeout": 10}
Error: TimeoutError - Process did not complete within 10 seconds
Partial stdout: "Processing row 15000/250000..."
```

For each failed call:
1. **Root cause**: What specifically went wrong?
2. **Recovery strategy**: How should the agent recover? Consider:
   - Immediate retry vs. delayed retry vs. alternative approach
   - Parameter corrections
   - Timeout adjustments
   - Graceful degradation options
3. **Corrected call**: Provide the exact corrected tool call JSON.
4. **Prevention**: How should the agent prevent this class of error in future calls?

Then provide the **complete corrected sequence** of all 3 calls (plus any additional calls needed for recovery), with proper ordering and error handling wrappers.
