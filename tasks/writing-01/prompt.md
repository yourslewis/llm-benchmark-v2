# Task: Write a Technical Specification for a Model Benchmark System

## Background

You are building an LLM model benchmark system to evaluate 23 LLMs across a range of task types. The system uses **LLM-as-judge** consensus scoring with 3 judges and includes speed metrics and routing table output.

## Specification Requirements

Write a complete technical specification document for this system. The spec should be detailed enough that a senior engineer could implement it from scratch.

## System Overview

The benchmark system must:
- Test **23 LLM models** across 6 task categories (code, plan, analysis, debug, writing, design)
- Use **3-judge LLM consensus scoring** with self-recusal (a model cannot judge its own output)
- Measure **speed metrics** (TTFT, total latency, tokens/sec)
- Produce a **routing table** recommending which models to use for which task types

## What to Cover in the Spec

### 1. Architecture Overview
- High-level system diagram (described in text)
- Core components and their responsibilities
- Data flow from prompt → response → scoring → output

### 2. Benchmark Task Corpus
- How tasks are organized (categories, difficulties)
- Task schema (what fields each task has)
- How prompts are templated and parameterized
- Minimum corpus size requirements

### 3. Model Execution Layer
- How models are invoked (API clients, config structure)
- Parallelism model (workers, rate limiting)
- Timeout and retry strategy
- How per-model configuration is stored (temperature, maxTokens, etc.)
- Error handling and result recording for failures

### 4. LLM-as-Judge Scoring System

This is the core innovation. Specify:

#### 4.1 Judge Pool
- The system maintains a pool of judge models
- For each response, exactly 3 judges are selected
- **Self-recusal rule:** The model that generated the response cannot serve as its own judge
- How judges are selected (round-robin, random, or deterministic per task?)

#### 4.2 Scoring Protocol
- Judge prompt template (include the exact template structure)
- What judges evaluate (correctness, completeness, clarity, etc.)
- Scoring scale (e.g., 0–10 per criterion)
- How per-criterion weights are applied

#### 4.3 Consensus Calculation
- How 3 judge scores are combined (average, weighted, majority?)
- How to handle outlier judges (one judge gives 2/10, others give 8/10)
- Confidence score: how certain is the consensus?
- When to flag a result for human review

#### 4.4 Judge Reliability Tracking
- Track each judge's scoring patterns over time
- Detect bias (does judge X always score its own provider's models higher?)
- Judge calibration: normalize scores across judges

### 5. Speed Metrics
Specify exactly how to measure:
- **TTFT (Time-to-First-Token):** definition, measurement method, precision
- **Total latency:** from request send to stream end
- **Tokens per second:** calculation method
- **P50/P95/P99 latencies:** how to compute across a run

### 6. Results Schema
Define the complete JSON schema for:
- Individual task result
- Model aggregate result
- Full benchmark run result

Use JSON Schema or pseudo-schema notation.

### 7. Routing Table Output
Specify the format and generation logic for the routing table:
- What columns it has (model, category, avg_score, avg_ttft_ms, cost_per_1k, recommendation)
- How the "recommendation" field is determined
- How to handle ties

### 8. Non-Functional Requirements
- Scalability: how many concurrent model calls?
- Reproducibility: how are results reproducible?
- Storage: where and how are results stored?
- Cost controls: how to avoid runaway API costs during a benchmark run?

### 9. Open Questions
List 3–5 genuine open questions or design decisions that need team input before implementation.
