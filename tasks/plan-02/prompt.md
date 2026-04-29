# Task: Design a 4-Agent AI Assistant Team

## Background

You are designing a team of 4 specialized AI agents that work together as a personal AI assistant platform. Each agent has a specific role, personality, and capability set.

## The Agents

Design full profiles for each of the following agents:

### Agent 1: Chloe — General Purpose Assistant
- **Role:** Primary personal assistant; first point of contact for most requests
- **Focus:** Task management, communication, scheduling, everyday help

### Agent 2: Rex — Research & Code Agent
- **Role:** Deep research, programming, technical problem-solving
- **Focus:** Web search, code generation, debugging, data analysis

### Agent 3: Don — Data & Monitoring Agent
- **Role:** Observability, metrics, system monitoring, alerting
- **Focus:** Log analysis, dashboard generation, anomaly detection, scheduled reports

### Agent 4: Selin — Security Agent
- **Role:** Security review, threat detection, credential management
- **Focus:** Code security audits, prompt injection detection, PII handling, access control

## What to Define for Each Agent

For each agent, provide:

### 1. Personality Profile
- **Tone/voice:** How do they communicate? (e.g., warm, direct, terse, analytical)
- **Strengths:** What are they exceptionally good at?
- **Weaknesses:** What should they avoid or escalate?
- **Quirks:** One distinctive personality trait that makes them feel like a real team member

### 2. Skill Set
List 6–8 specific capabilities this agent has, in the format:
- `skill_name`: Brief description

### 3. Model Assignment
Recommend a specific LLM for this agent and justify why:
- **Primary model:** (e.g., `gpt-4o`, `claude-opus-4`, `gemini-2.0-flash`, `o3`, etc.)
- **Fallback model:** For when primary is unavailable or over budget
- **Reasoning:** Why this model fits this agent's needs (latency, reasoning, cost, context window, etc.)

### 4. Routing Rules
Define when requests should be routed TO this agent vs. FROM this agent:
- **Route TO this agent when:** (3–5 trigger conditions)
- **Hand off FROM this agent when:** (2–3 escalation conditions)

### 5. Inter-Agent Collaboration
Describe how this agent collaborates with the other 3:
- Which agents does it frequently work with?
- What does it request from others?
- What does it provide to others?

## Team Coordination

After defining all 4 agents, provide:

### Orchestration Strategy
- Which agent acts as the **primary orchestrator** for multi-agent tasks?
- How are tasks routed when a request could fit multiple agents?
- What happens when agents disagree?

### Sample Workflow
Describe a complete multi-agent workflow for this scenario:
> *"The user asks: 'Analyze our API server logs from the last 24 hours and alert me if there are any security anomalies, then summarize the findings and add a task to my Todoist.'"*

Show which agent handles each step and how they hand off to each other.

## Output Format

Structure your response as a clear document with a section for each agent, followed by the team coordination section. Use headers, bullet points, and tables where appropriate.
