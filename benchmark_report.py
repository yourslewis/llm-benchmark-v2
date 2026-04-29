#!/usr/bin/env python3
"""
Model Benchmark — Runner
Replays extracted tasks against multiple models using OpenClaw's API.
Run this via Chloe/subagents, not standalone.

Output: results.json with per-task per-model scores.
"""

import json, os, sys, time
from datetime import datetime

BENCHMARK_DIR = os.path.expanduser("~/.openclaw/workspace-chloe/benchmark")
TASKS_FILE = os.path.join(BENCHMARK_DIR, "tasks.json")
RESULTS_FILE = os.path.join(BENCHMARK_DIR, "results.json")

MODELS = [
    "copilot/claude-opus-4-6",
    "copilot/claude-sonnet-4-6",
    "copilot/claude-haiku-4-5",
    "copilot/gpt-5.3-codex",
    "copilot/gemini-2.5-pro",
    "copilot/gpt-5.4-mini",
]

# Simplified model names for display
MODEL_NAMES = {
    "copilot/claude-opus-4-6": "Opus 4.6",
    "copilot/claude-sonnet-4-6": "Sonnet 4.6",
    "copilot/claude-haiku-4-5": "Haiku 4.5",
    "copilot/gpt-5.3-codex": "GPT-5.3-Codex",
    "copilot/gemini-2.5-pro": "Gemini 2.5 Pro",
    "copilot/gpt-5.4-mini": "GPT-5.4-mini",
}


def generate_report():
    """Generate a comparison report from results."""
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    
    results = data["results"]
    
    print("=" * 80)
    print("MODEL BENCHMARK REPORT")
    print(f"Generated: {datetime.now().isoformat()}")
    print(f"Tasks: {len(set(r['task_id'] for r in results))}")
    print(f"Models: {len(set(r['model'] for r in results))}")
    print("=" * 80)
    
    # Aggregate by model
    by_model = {}
    for r in results:
        model = r["model"]
        by_model.setdefault(model, []).append(r)
    
    print("\n## Overall Model Comparison\n")
    print(f"{'Model':<20} {'Avg Score':>10} {'Avg Tokens':>12} {'Avg Time':>10} {'Tasks':>6}")
    print("-" * 60)
    
    for model in MODELS:
        runs = by_model.get(model, [])
        if not runs:
            continue
        scored = [r for r in runs if r.get("score") is not None]
        avg_score = sum(r["score"] for r in scored) / len(scored) if scored else 0
        avg_tokens = sum(r.get("output_tokens", 0) for r in runs) / len(runs)
        avg_time = sum(r.get("duration_ms", 0) for r in runs) / len(runs) / 1000
        name = MODEL_NAMES.get(model, model)
        print(f"{name:<20} {avg_score:>10.1f} {avg_tokens:>12.0f} {avg_time:>9.1f}s {len(runs):>6}")
    
    # By category
    categories = sorted(set(r["category"] for r in results))
    print("\n## By Category\n")
    
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        print(f"\n### {cat.upper()}")
        print(f"{'Model':<20} {'Avg Score':>10} {'Avg Tokens':>12}")
        print("-" * 45)
        for model in MODELS:
            runs = [r for r in cat_results if r["model"] == model and r.get("score") is not None]
            if not runs:
                continue
            avg_score = sum(r["score"] for r in runs) / len(runs)
            avg_tokens = sum(r.get("output_tokens", 0) for r in runs) / len(runs)
            name = MODEL_NAMES.get(model, model)
            print(f"{name:<20} {avg_score:>10.1f} {avg_tokens:>12.0f}")
    
    # Recommendation
    print("\n## Recommendations\n")
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        best_model = None
        best_efficiency = -1
        for model in MODELS:
            runs = [r for r in cat_results if r["model"] == model and r.get("score") is not None]
            if not runs:
                continue
            avg_score = sum(r["score"] for r in runs) / len(runs)
            avg_tokens = sum(r.get("output_tokens", 0) for r in runs) / len(runs)
            # Efficiency = score / log(tokens+1) — reward high score, penalize verbosity
            import math
            efficiency = avg_score / max(math.log(avg_tokens + 1), 1) if avg_tokens > 0 else avg_score
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_model = model
        
        if best_model:
            name = MODEL_NAMES.get(best_model, best_model)
            print(f"  {cat}: {name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        generate_report()
    else:
        print("Usage: benchmark_report.py [report]")
