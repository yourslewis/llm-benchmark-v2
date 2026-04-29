# Task: Diagnose Gateway Timeout Errors

## Background

You are operating an AI gateway that routes requests to multiple LLM providers. The gateway uses an **embedded run failover** system — when a model call times out, it records a decision and optionally retries with a fallback model.

## Error Logs

The following 20 log lines were captured over a 4-minute window this morning. Review them carefully:

```
2026-04-06T08:14:02.341Z [gateway] INFO  session=a1b2c3 model=gpt-4o routing decision: primary
2026-04-06T08:14:07.412Z [gateway] WARN  session=a1b2c3 model=gpt-4o embedded run failover decision: reason=timeout elapsed=5071ms threshold=5000ms
2026-04-06T08:14:07.415Z [gateway] INFO  session=a1b2c3 model=claude-sonnet-4 routing decision: failover
2026-04-06T08:14:09.203Z [gateway] INFO  session=a1b2c3 model=claude-sonnet-4 response received tokens=412 ttft=847ms
2026-04-06T08:15:11.882Z [gateway] INFO  session=d4e5f6 model=gpt-4o routing decision: primary
2026-04-06T08:15:16.994Z [gateway] WARN  session=d4e5f6 model=gpt-4o embedded run failover decision: reason=timeout elapsed=5112ms threshold=5000ms
2026-04-06T08:15:17.001Z [gateway] INFO  session=d4e5f6 model=gemini-2.0-flash routing decision: failover
2026-04-06T08:15:18.774Z [gateway] INFO  session=d4e5f6 model=gemini-2.0-flash response received tokens=388 ttft=612ms
2026-04-06T08:16:03.554Z [gateway] INFO  session=g7h8i9 model=gpt-4o routing decision: primary
2026-04-06T08:16:08.671Z [gateway] WARN  session=g7h8i9 model=gpt-4o embedded run failover decision: reason=timeout elapsed=5117ms threshold=5000ms
2026-04-06T08:16:08.680Z [gateway] WARN  session=g7h8i9 model=claude-sonnet-4 routing decision: failover (no more fallbacks after this)
2026-04-06T08:16:09.903Z [gateway] INFO  session=g7h8i9 model=claude-sonnet-4 response received tokens=501 ttft=901ms
2026-04-06T08:17:44.120Z [gateway] INFO  session=j1k2l3 model=o3-mini routing decision: primary
2026-04-06T08:17:49.234Z [gateway] WARN  session=j1k2l3 model=o3-mini embedded run failover decision: reason=timeout elapsed=5114ms threshold=5000ms
2026-04-06T08:17:49.241Z [gateway] INFO  session=j1k2l3 model=gpt-4o routing decision: failover
2026-04-06T08:17:54.399Z [gateway] WARN  session=j1k2l3 model=gpt-4o embedded run failover decision: reason=timeout elapsed=5158ms threshold=5000ms
2026-04-06T08:17:54.407Z [gateway] ERROR session=j1k2l3 all fallbacks exhausted — request failed
2026-04-06T08:18:22.901Z [gateway] INFO  session=m4n5o6 model=gpt-4o routing decision: primary
2026-04-06T08:18:27.988Z [gateway] WARN  session=m4n5o6 model=gpt-4o embedded run failover decision: reason=timeout elapsed=5087ms threshold=5000ms
2026-04-06T08:18:28.001Z [gateway] INFO  session=m4n5o6 model=claude-sonnet-4 routing decision: failover
```

## Questions

### 1. Root Cause Analysis
Based on the log pattern, what is the most likely root cause of the timeout failures?

Consider:
- Which model is timing out most frequently?
- What does the consistent ~5000ms elapsed time suggest?
- Is this likely a model-side issue or a gateway configuration issue?
- What does session `j1k2l3` tell us that the others don't?

### 2. Pattern Summary
Fill in this table:

| Metric | Value |
|--------|-------|
| Total timeout events | |
| Primary model causing most timeouts | |
| % of sessions where failover succeeded | |
| Sessions where all fallbacks exhausted | |
| Typical elapsed time at timeout | |

### 3. Configuration Fix
The gateway uses a YAML config. Propose specific config changes to fix the issue:

```yaml
# Current config (partial):
gateway:
  timeout_ms: 5000
  models:
    - id: gpt-4o
      provider: openai
      fallback: claude-sonnet-4
    - id: o3-mini
      provider: openai
      fallback: gpt-4o
    - id: claude-sonnet-4
      provider: anthropic
      fallback: null
```

What changes would you make and why?

### 4. Monitoring Recommendation
What metric or alert would you add to catch this problem earlier in the future? Provide a specific alert definition (metric, threshold, window, action).
