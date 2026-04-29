#!/usr/bin/env python3
"""
Model Benchmark Harness — Task Extractor
Extracts representative user prompts from OpenClaw session transcripts.
"""

import json, os, sys, glob, re, ast
from datetime import datetime
from pathlib import Path

AGENTS_DIR = os.path.expanduser("~/.openclaw/agents")
BENCHMARK_DIR = os.path.expanduser("~/.openclaw/workspace-chloe/benchmark")
TASKS_FILE = os.path.join(BENCHMARK_DIR, "tasks.json")

CATEGORIES = {
    "monitoring": ["check", "status", "monitor", "tail", "log", "nvidia-smi", "ssh", "training"],
    "code": ["fix", "debug", "error", "traceback", "implement", "refactor", "build", "script"],
    "research": ["paper", "search", "find", "literature", "survey", "explore", "leaked", "claude code"],
    "security": ["audit", "vulnerability", "CVE", "scan", "malware", "injection", "security", "vet"],
    "planning": ["plan", "trip", "schedule", "draft", "email", "brainstorm", "rental", "hotel", "flight"],
    "data": ["data", "csv", "spreadsheet", "kaggle", "analysis", "metric", "score", "todoist", "tasks"],
    "sysadmin": ["cron", "config", "gateway", "restart", "install", "setup", "agent", "model", "BOOT"],
}


def categorize_task(text):
    text_lower = text.lower()
    scores = {cat: sum(1 for kw in kws if kw.lower() in text_lower) for cat, kws in CATEGORIES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def clean_prompt(text):
    """Strip security wrappers and metadata from user message."""
    t = text
    t = re.sub(r'<openguardrails>.*?</openguardrails>', '', t, flags=re.DOTALL)
    t = re.sub(r'<clawguard>.*?</clawguard>', '', t, flags=re.DOTALL)
    t = re.sub(r'<openguardrails-quota-exceeded>.*?</openguardrails-quota-exceeded>', '', t, flags=re.DOTALL)
    t = re.sub(r'Conversation info \(untrusted.*?```\s*\n', '', t, flags=re.DOTALL)
    t = re.sub(r'Sender \(untrusted.*?```\s*\n', '', t, flags=re.DOTALL)
    t = re.sub(r'Replied message \(untrusted.*?```\s*\n', '', t, flags=re.DOTALL)
    t = re.sub(r'\[media attached:.*?\]', '', t)
    t = re.sub(r'To send an image back.*?Keep caption in the text body\.', '', t, flags=re.DOTALL)
    t = re.sub(r'System:.*?\n', '', t)
    t = re.sub(r'Current time:.*?\n', '', t)
    t = re.sub(r'Heartbeat:.*?\n', '', t)
    return t.strip()


def parse_message(entry):
    """Parse a JSONL entry's message field."""
    if entry.get("type") != "message":
        return None, None
    msg = entry.get("message", {})
    if isinstance(msg, str):
        try:
            msg = ast.literal_eval(msg)
        except:
            try:
                msg = json.loads(msg)
            except:
                return None, None
    role = msg.get("role", "")
    content = msg.get("content", "")
    if isinstance(content, list):
        texts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
        content = "\n".join(texts)
    return role, content


def extract_tasks():
    os.makedirs(BENCHMARK_DIR, exist_ok=True)
    tasks = []
    seen = set()

    # Get recent non-boot transcripts > 10KB
    transcripts = []
    for agent in ["chloe", "rex", "don", "selin"]:
        sess_dir = os.path.join(AGENTS_DIR, agent, "sessions")
        if not os.path.exists(sess_dir):
            continue
        for f in glob.glob(os.path.join(sess_dir, "*.jsonl")):
            if "boot-" in os.path.basename(f):
                continue
            size = os.path.getsize(f)
            if size < 10000:
                continue
            transcripts.append((f, agent, size, os.path.getmtime(f)))

    transcripts.sort(key=lambda x: -x[3])
    transcripts = transcripts[:30]
    print(f"Scanning {len(transcripts)} transcripts...")

    for filepath, agent, size, mtime in transcripts:
        try:
            with open(filepath) as f:
                lines = f.readlines()
        except:
            continue

        entries = []
        for line in lines:
            try:
                entries.append(json.loads(line.strip()))
            except:
                continue

        for i, entry in enumerate(entries):
            role, content = parse_message(entry)
            if role != "user" or not content:
                continue

            cleaned = clean_prompt(content)
            if len(cleaned) < 15:
                continue
            if cleaned.startswith("(session bootstrap)"):
                continue

            # Deduplicate
            key = cleaned[:80]
            if key in seen:
                continue
            seen.add(key)

            # Get response length
            resp_words = 0
            for j in range(i + 1, min(i + 15, len(entries))):
                r, c = parse_message(entries[j])
                if r == "assistant" and c and len(c) > 10:
                    resp_words = len(c.split())
                    break

            category = categorize_task(cleaned)
            tasks.append({
                "id": f"{agent}_{len(tasks):03d}",
                "agent": agent,
                "category": category,
                "prompt": cleaned[:2000],
                "prompt_length": len(cleaned),
                "response_words": resp_words,
                "source": os.path.basename(filepath),
            })

    # Sample: up to 3 per category, diverse agents
    sampled = []
    by_cat = {}
    for t in tasks:
        by_cat.setdefault(t["category"], []).append(t)

    for cat in sorted(by_cat):
        agents_used = set()
        for t in by_cat[cat]:
            if len([s for s in sampled if s["category"] == cat]) >= 3:
                break
            if t["agent"] not in agents_used or len([s for s in sampled if s["category"] == cat]) < 2:
                sampled.append(t)
                agents_used.add(t["agent"])

    with open(TASKS_FILE, "w") as f:
        json.dump({
            "extracted_at": datetime.now().isoformat(),
            "total_found": len(tasks),
            "sampled": len(sampled),
            "tasks": sampled,
        }, f, indent=2)

    print(f"\nExtracted {len(tasks)} tasks, sampled {len(sampled)}")
    for cat in sorted(by_cat):
        n = len(by_cat[cat])
        s = len([x for x in sampled if x["category"] == cat])
        print(f"  {cat}: {n} found, {s} sampled")
    print(f"\nSaved to {TASKS_FILE}")


def show_tasks():
    with open(TASKS_FILE) as f:
        data = json.load(f)
    print(f"Tasks: {data['sampled']} sampled from {data['total_found']} found\n")
    for t in data["tasks"]:
        print(f"[{t['id']}] {t['category'].upper()} ({t['agent']})")
        print(f"  {t['prompt'][:120].replace(chr(10), ' ')}...")
        print(f"  Response: ~{t['response_words']} words\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if cmd == "extract":
        extract_tasks()
    elif cmd == "show":
        show_tasks()
    else:
        print(f"Usage: benchmark.py [extract|show]")
