# Task: Design a Self-Hosted Security Extension for an AI Agent Platform

## Background

You are replacing a cloud-based security service (**Protector**) with a fully self-hosted security extension for an AI agent platform. The cloud service has been handling security scanning, credential protection, and PII detection remotely — but your team needs zero cloud dependencies for compliance and latency reasons.

The new extension must replicate and improve on the cloud service's functionality entirely locally.

## Requirements

### Core Requirement: Zero Cloud Dependencies
All processing must happen locally. No data may leave the machine for security scanning purposes. The extension must work fully offline.

---

### Requirement 1: Credential Vault

Design a credential vault that:
- Encrypts secrets using **AES-256-GCM** with authenticated encryption
- Integrates with the **OS keychain** (macOS Keychain, Windows Credential Manager, or Linux Secret Service) to store the vault master key
- Supports secret types: API keys, OAuth tokens, passwords, TLS certificates
- Provides a secrets injection API: given a tool call context, automatically substitute `__VAULT_REF_<name>__` placeholders with the actual secret

Specify:
- The vault file format (how secrets are stored at rest)
- The key derivation process (how the AES key is derived from the OS keychain entry)
- The injection mechanism (how secrets enter tool call arguments without appearing in logs)
- Secret rotation: how do you rotate a secret without downtime?

---

### Requirement 2: Multi-Layer Scanning (L1–L4)

Design a 4-layer scanning pipeline for tool calls:

| Layer | Name | Method | Latency Target |
|-------|------|--------|----------------|
| L1 | Pattern Matching | Regex/blocklist | < 1ms |
| L2 | Heuristic Analysis | Statistical scoring | < 5ms |
| L3 | Semantic Analysis | Local LLM | < 200ms |
| L4 | Behavioral Chain | Session state machine | < 2ms |

For each layer, specify:
- What it scans (input)
- How it makes a block/allow decision
- What data structure stores its state (for L4)
- What happens on a positive detection

For **L3 specifically** (local LLM scan):
- Which model would you use? (must run locally, < 4GB RAM)
- How is the model served? (llama.cpp, ollama, etc.)
- What is the exact prompt structure for scanning a tool call?
- How do you handle the 200ms latency requirement?

---

### Requirement 3: Behavioral Chain Detection

Design the L4 behavioral chain detector as a **session state machine**:

- Define the states a session can be in (e.g., Normal, Elevated, Suspicious, Blocked)
- Define the transitions: what events cause state changes?
- Define the detection patterns (at least 4 specific patterns to detect)
- Define the response at each severity level

Also specify:
- How sessions are identified (session ID, user ID, or combination?)
- How long session state is retained
- How to avoid false positives for legitimate power users

---

### Requirement 4: PII Approval Workflow via Telegram

When the scanner detects PII in a tool call argument, the user must explicitly approve before the tool call proceeds.

Design the approval workflow:
- What happens to the tool call while waiting for approval? (async hold)
- What message is sent to the user via Telegram? (include the exact message template)
- What are the user's options? (approve / deny / approve-always for this type)
- What is the timeout? What happens if the user doesn't respond?
- How is the approval decision stored to avoid re-prompting for the same PII type?

---

### Requirement 5: Credential Redaction

Before any text is passed to an LLM, credentials must be redacted and replaced with safe placeholders.

Design the redaction pipeline:
- What patterns are detected? (list at least 8 credential patterns with regex examples)
- How are placeholders generated? (format: `__REDACTED_<TYPE>_<SERIAL>__`)
- How is the redaction mapping stored for the duration of a request? (so it can be reversed if needed)
- At what point in the tool call lifecycle does redaction happen? (before L1 scan? after?)
- How do you prevent double-redaction if a secret appears multiple times?

---

## Deliverable

Write a complete design document with a section for each requirement. For each section:
- Provide concrete data structures (JSON or pseudocode)
- Include specific technology choices with justification
- Call out security tradeoffs explicitly
- Note any implementation risks

The document should be detailed enough for a security engineer to begin implementation from your design alone.
