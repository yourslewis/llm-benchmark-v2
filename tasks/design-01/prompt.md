# Task: Design an LLM-Based User Profile System from Browser Behavioral Signals

## Background

You are designing a user profile system for an AI assistant embedded in Microsoft Edge. The system infers user interests, preferences, and context from browser behavioral signals and uses LLM summarization to build rich, structured profiles. These profiles are then used to personalize AI assistant responses in real time.

## Design Requirements

### Input Signals

The system receives these behavioral signals from the Edge browser:
- **Page visits:** URL, title, domain, visit duration, scroll depth, time of day
- **Search queries:** Query text, result click-through
- **Content interactions:** Highlights, annotations, copy events
- **App usage patterns:** Which tabs are open, task-switching behavior
- **Explicit signals:** Bookmarks, saves, likes, follows (when available)

### 5-Layer Profile Schema

Design a profile schema with these 5 layers, each with different update cadence:

| Layer | Name | Update Cadence | Contents |
|-------|------|----------------|----------|
| L1 | Identity | Monthly | Stable attributes: occupation, expertise domains, communication style |
| L2 | Preferences | Weekly | Behavioral preferences: preferred content length, formality, topics to avoid |
| L3 | Interests | Daily | Active interest clusters with confidence scores |
| L4 | World Context | Daily | What the user is currently focused on: active projects, recent searches, news topics |
| L5 | Interest Cards | Event-triggered | Triggered by specific signal patterns; transient, expire after 48h |

### What to Design

#### 1. Full Profile Schema
Define the complete data schema for each layer. For each layer, specify:
- The exact fields and their types
- Example values
- How the layer relates to the others

Use JSON or pseudo-JSON format.

#### 2. Generation Pipeline
Describe how each layer is generated from raw signals:

For each layer, specify:
- **Input:** What signals feed into this layer?
- **LLM summarization prompt:** What prompt template is used to generate/update this layer?
- **Trigger:** When is this layer regenerated? (time-based or event-based)
- **Merge strategy:** How does a new generation merge with the existing layer value? (overwrite, append, weighted merge?)

For the **Interest Cards (L5)** layer specifically:
- Define 3 concrete trigger patterns that create a card
- Specify the card schema (what fields a card has)
- Specify the expiry and eviction logic

#### 3. Storage and Serving Architecture
Design the storage layer with these constraints:
- **Read P99 latency < 5ms** (profile must be available for real-time AI responses)
- Profiles are per-user; estimated 10M users at scale
- Profile size: ~2KB per user (average, all layers combined)
- Writes are async and eventual; reads are synchronous

Specify:
- Storage technology and data model
- Caching strategy (what level, TTL, invalidation)
- How the AI assistant reads the profile at request time (sync path)
- How profile updates are written (async path)

#### 4. LLM Summarization Pipeline

The core of the system is an LLM pipeline that periodically processes raw behavioral events and updates the profile. Specify:

- **Event batching:** How are raw events batched for processing?
- **Summarization model:** What model is used (balance cost vs. quality)?
- **Prompt structure:** Show an example full prompt for generating the L3 (Interests) layer
- **Output parsing:** How is the LLM output parsed and validated before writing to the profile?
- **Failure handling:** What happens if the LLM call fails or returns garbage?

#### 5. Evaluation Framework

How do you know if the profiles are good? Design an evaluation framework:

- **Offline eval:** How do you measure profile quality without user feedback?
- **Online eval:** What metrics do you track in production?
- **A/B testing:** What experiment would you run to measure profile impact on AI assistant quality?
- **Privacy compliance check:** How do you ensure profiles don't contain PII that wasn't consented to?

### Constraints
- Zero raw behavioral data stored on server — only derived profile layers
- All LLM inference happens server-side
- User can view and delete their profile via a simple API
- GDPR/CCPA compliant (right to deletion, data minimization)

## Output Format

Write a structured design document with:
- A section for each of the 5 design areas above
- Concrete examples and schemas, not abstract descriptions
- Call out open questions or tradeoffs where they exist
