# Task: Add Telegram Notification to Security Plugin

## Background

You are working on an OpenClaw security plugin called **ClawGuard**. The plugin intercepts tool calls and blocks ones that match security policies. Currently, when a tool call is blocked, it is silently dropped with only a local log entry.

Your task is to **add Telegram notification logic** so that whenever a tool call is blocked, the plugin sends a Telegram message using `api.message()`.

## Existing Plugin Code

Below is the full plugin source (`clawguard.plugin.js`). Add your notification code to this file.

```javascript
// clawguard.plugin.js
// ClawGuard Security Plugin v2.1.0
// Multi-layer tool call scanning with behavioral chain detection

"use strict";

const PLUGIN_NAME = "clawguard";
const PLUGIN_VERSION = "2.1.0";

// ─── Configuration ───────────────────────────────────────────────────────────

const DEFAULT_CONFIG = {
  enabled: true,
  logLevel: "warn",
  notifyChannel: null,   // Telegram chat ID for notifications — fill this in
  silentBlock: false,
  layers: {
    L1: { enabled: true, patterns: true },
    L2: { enabled: true, heuristics: true },
    L3: { enabled: false, llmScan: false },
    L4: { enabled: false, behavioral: false },
  },
  piiTypes: ["email", "phone", "ssn", "creditCard", "apiKey"],
  credentialPatterns: [
    /sk-[a-zA-Z0-9]{32,}/g,
    /ghp_[a-zA-Z0-9]{36}/g,
    /AKIA[0-9A-Z]{16}/g,
    /-----BEGIN (RSA |EC )?PRIVATE KEY-----/,
    /xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+/g,
  ],
};

// ─── Layer 1: Pattern Matching ────────────────────────────────────────────────

const BLOCKED_TOOLS = new Set([
  "exec_shell",
  "write_file",
  "delete_file",
  "send_email",
  "make_http_request",
]);

const BLOCKED_PATTERNS = [
  /rm\s+-rf\s+\//i,
  /curl\s+.*\|\s*sh/i,
  /wget\s+.*\|\s*bash/i,
  /base64\s+-d\s*\|/i,
  /eval\s*\(/i,
  /exec\s*\(/i,
  /;\s*cat\s+\/etc\/passwd/i,
  /\|\s*nc\s+/i,
];

function scanL1(toolName, toolArgs) {
  const argsStr = JSON.stringify(toolArgs);

  if (BLOCKED_TOOLS.has(toolName)) {
    return { blocked: true, reason: `L1: tool '${toolName}' is in blocklist` };
  }

  for (const pattern of BLOCKED_PATTERNS) {
    if (pattern.test(argsStr)) {
      return { blocked: true, reason: `L1: matched pattern ${pattern}` };
    }
  }

  return { blocked: false };
}

// ─── Layer 2: Heuristic Analysis ──────────────────────────────────────────────

const SUSPICIOUS_KEYWORDS = [
  "ignore previous instructions",
  "disregard your system prompt",
  "you are now",
  "pretend you are",
  "act as if",
  "bypass",
  "jailbreak",
  "prompt injection",
  "override",
  "forget everything",
];

function scoreHeuristic(text) {
  let score = 0;
  const lower = text.toLowerCase();

  for (const kw of SUSPICIOUS_KEYWORDS) {
    if (lower.includes(kw)) score += 20;
  }

  // Long base64-like strings
  const b64matches = text.match(/[A-Za-z0-9+/]{80,}={0,2}/g);
  if (b64matches) score += b64matches.length * 10;

  // Excessive special characters
  const specialCount = (text.match(/[<>{}|\\^~\[\]`]/g) || []).length;
  if (specialCount > 20) score += 15;

  return score;
}

function scanL2(toolName, toolArgs) {
  const argsStr = JSON.stringify(toolArgs);
  const score = scoreHeuristic(argsStr);

  if (score >= 40) {
    return { blocked: true, reason: `L2: heuristic score ${score} >= threshold 40` };
  }

  return { blocked: false, score };
}

// ─── PII Detection ────────────────────────────────────────────────────────────

function detectPII(text, piiTypes) {
  const found = [];

  if (piiTypes.includes("email")) {
    const emails = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g);
    if (emails) found.push({ type: "email", count: emails.length });
  }

  if (piiTypes.includes("phone")) {
    const phones = text.match(/(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}/g);
    if (phones) found.push({ type: "phone", count: phones.length });
  }

  if (piiTypes.includes("ssn")) {
    const ssns = text.match(/\b\d{3}-\d{2}-\d{4}\b/g);
    if (ssns) found.push({ type: "ssn", count: ssns.length });
  }

  if (piiTypes.includes("creditCard")) {
    const cards = text.match(/\b(?:\d{4}[-\s]?){3}\d{4}\b/g);
    if (cards) found.push({ type: "creditCard", count: cards.length });
  }

  if (piiTypes.includes("apiKey")) {
    for (const pattern of DEFAULT_CONFIG.credentialPatterns) {
      const matches = text.match(pattern);
      if (matches) found.push({ type: "apiKey", count: matches.length });
    }
  }

  return found;
}

// ─── Behavioral Chain Tracker ─────────────────────────────────────────────────

class BehavioralChainTracker {
  constructor() {
    this.chains = new Map(); // sessionId → [events]
    this.WINDOW_MS = 60_000;
    this.MAX_EVENTS = 10;
  }

  record(sessionId, event) {
    const now = Date.now();
    const events = (this.chains.get(sessionId) || []).filter(
      (e) => now - e.ts < this.WINDOW_MS
    );
    events.push({ ...event, ts: now });
    this.chains.set(sessionId, events.slice(-this.MAX_EVENTS));
    return events;
  }

  isChainSuspicious(sessionId) {
    const events = this.chains.get(sessionId) || [];
    if (events.length < 3) return false;

    const blockCount = events.filter((e) => e.blocked).length;
    if (blockCount >= 3) return true;

    const uniqueTools = new Set(events.map((e) => e.tool));
    if (uniqueTools.size >= 5 && events.length >= 5) return true;

    return false;
  }
}

const chainTracker = new BehavioralChainTracker();

// ─── Main Plugin Export ───────────────────────────────────────────────────────

module.exports = {
  name: PLUGIN_NAME,
  version: PLUGIN_VERSION,

  async onToolCall(context, api) {
    const { toolName, toolArgs, sessionId } = context;
    const config = { ...DEFAULT_CONFIG, ...(api.getConfig?.() || {}) };

    if (!config.enabled) return { allow: true };

    // Layer 1
    const l1 = scanL1(toolName, toolArgs);
    if (l1.blocked) {
      api.log("warn", `[ClawGuard] BLOCKED (${l1.reason}) tool=${toolName} session=${sessionId}`);

      // TODO: Add Telegram notification here using api.message()
      // The notification should include: toolName, reason, sessionId, timestamp
      // Use config.notifyChannel as the target

      chainTracker.record(sessionId, { tool: toolName, blocked: true, reason: l1.reason });
      return { allow: false, reason: l1.reason };
    }

    // Layer 2
    const l2 = scanL2(toolName, toolArgs);
    if (l2.blocked) {
      api.log("warn", `[ClawGuard] BLOCKED (${l2.reason}) tool=${toolName} session=${sessionId}`);

      // TODO: Add Telegram notification here using api.message()
      // Same as above — notify on L2 blocks too

      chainTracker.record(sessionId, { tool: toolName, blocked: true, reason: l2.reason });
      return { allow: false, reason: l2.reason };
    }

    // PII check
    const argsStr = JSON.stringify(toolArgs);
    const pii = detectPII(argsStr, config.piiTypes);
    if (pii.length > 0) {
      api.log("info", `[ClawGuard] PII detected in tool=${toolName}: ${JSON.stringify(pii)}`);
    }

    // Behavioral chain check
    chainTracker.record(sessionId, { tool: toolName, blocked: false });
    if (chainTracker.isChainSuspicious(sessionId)) {
      api.log("warn", `[ClawGuard] Suspicious behavioral chain detected session=${sessionId}`);

      // TODO: Add Telegram notification here using api.message()
      // Notify on suspicious behavioral chain too

      return { allow: false, reason: "L4: suspicious behavioral chain" };
    }

    return { allow: true };
  },

  async onLoad(api) {
    const config = api.getConfig?.() || {};
    api.log("info", `[ClawGuard] v${PLUGIN_VERSION} loaded. notifyChannel=${config.notifyChannel || "not set"}`);
  },
};
```

## Your Task

Modify the plugin above to add Telegram notification logic. Specifically:

1. **Replace all three `// TODO: Add Telegram notification here` comments** with working code that calls `api.message()`.

2. **The notification message should include:**
   - Emoji indicator: 🚨 for blocks, ⚠️ for behavioral chains
   - The tool name that was blocked
   - The reason for blocking
   - The session ID
   - A timestamp (ISO format)

3. **Only send the notification if** `config.notifyChannel` is set (not null/undefined).

4. **Handle errors gracefully** — if `api.message()` throws, log the error but don't let it block the security decision.

5. **The notification call must use** `await api.message({ target: config.notifyChannel, message: "..." })`.

## Output Format

Return the complete modified plugin file with all three TODO sections replaced. Do not truncate or omit any existing code.
