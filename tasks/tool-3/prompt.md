Design a tool-dispatch layer for an AI agent that needs to call multiple external tools (APIs). Requirements:

1. **Parallel dispatch**: Identify independent tool calls that can execute simultaneously. Given a dependency graph of tool calls, batch independent ones together.

2. **Per-provider rate limits**: Different providers have different rate limits:
   - `web_search`: 10 req/min, burst of 3
   - `exec`: 5 concurrent, no rate limit
   - `file_write`: unlimited
   - `llm_call`: 20 req/min, burst of 5
   - `browser`: 2 concurrent, 30 req/min

3. **Error degradation**: When a batched call fails:
   - Retry with exponential backoff (max 3 retries)
   - If a batch member fails, don't fail the whole batch
   - After max retries, degrade to sequential execution for that provider
   - Log failures with enough context for debugging

4. **Priority queue**: Some calls are higher priority. High-priority calls should preempt queued low-priority calls.

Deliverables:
- Architecture diagram (ASCII art or description)
- Pseudocode for the dispatcher (not just an outline — detailed enough to implement)
- Rate limiter implementation (token bucket or sliding window)
- Batch scheduler that resolves the dependency graph
- Error handling and degradation logic
- Rationale for each design decision

Consider edge cases: What happens if all providers are rate-limited? What about circular dependencies in the call graph? How do you prevent starvation of low-priority tasks?
