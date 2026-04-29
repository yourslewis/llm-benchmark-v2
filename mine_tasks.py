#!/usr/bin/env python3
"""Mine non-trivial tasks from session transcripts."""
import json, ast, glob, os, re

AGENTS_DIR = os.path.expanduser("~/.openclaw/agents")

tasks = []
seen = set()

for agent in ["chloe", "rex", "don", "selin"]:
    sess_dir = os.path.join(AGENTS_DIR, agent, "sessions")
    if not os.path.exists(sess_dir):
        continue
    files = sorted(glob.glob(os.path.join(sess_dir, "*.jsonl")), key=os.path.getmtime, reverse=True)[:15]
    for f in files:
        if "boot-" in os.path.basename(f):
            continue
        if os.path.getsize(f) < 10000:
            continue
        try:
            with open(f) as fh:
                lines = fh.readlines()
        except:
            continue

        entries = []
        for line in lines:
            try:
                entries.append(json.loads(line.strip()))
            except:
                continue

        for i, entry in enumerate(entries):
            if entry.get("type") != "message":
                continue
            msg = entry.get("message", {})
            if isinstance(msg, str):
                try:
                    msg = ast.literal_eval(msg)
                except:
                    continue
            if msg.get("role") != "user":
                continue
            content = msg.get("content", "")
            if isinstance(content, list):
                texts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                content = "\n".join(texts)

            t = content
            t = re.sub(r"<openguardrails>.*?</openguardrails>", "", t, flags=re.DOTALL)
            t = re.sub(r"<clawguard>.*?</clawguard>", "", t, flags=re.DOTALL)
            t = re.sub(r"<openguardrails-quota-exceeded>.*?</openguardrails-quota-exceeded>", "", t, flags=re.DOTALL)
            t = re.sub(r"Conversation info \(untrusted.*?```\s*\n", "", t, flags=re.DOTALL)
            t = re.sub(r"Sender \(untrusted.*?```\s*\n", "", t, flags=re.DOTALL)
            t = re.sub(r"Replied message \(untrusted.*?```\s*\n", "", t, flags=re.DOTALL)
            t = re.sub(r"\[media attached:.*?\]", "", t)
            t = re.sub(r"To send an image back.*?Keep caption in the text body\.", "", t, flags=re.DOTALL)
            t = re.sub(r"System:.*?\n", "", t)
            t = re.sub(r"Current time:.*?\n", "", t)
            t = re.sub(r"Heartbeat:.*?\n", "", t)
            t = t.strip()

            if len(t) < 50 or t.startswith("(session bootstrap)"):
                continue

            key = t[:80]
            if key in seen:
                continue
            seen.add(key)

            resp_words = 0
            for j in range(i + 1, min(i + 15, len(entries))):
                if entries[j].get("type") != "message":
                    continue
                m2 = entries[j].get("message", {})
                if isinstance(m2, str):
                    try:
                        m2 = ast.literal_eval(m2)
                    except:
                        continue
                if m2.get("role") == "assistant":
                    c2 = m2.get("content", "")
                    if isinstance(c2, list):
                        c2 = " ".join(p.get("text", "") for p in c2 if isinstance(p, dict))
                    if len(str(c2)) > 20:
                        resp_words = len(str(c2).split())
                        break

            tasks.append({
                "agent": agent,
                "prompt": t[:2000],
                "prompt_len": len(t),
                "resp_words": resp_words,
                "file": os.path.basename(f),
            })

nontrivial = [t for t in tasks if t["prompt_len"] > 80 and t["resp_words"] > 30]
nontrivial.sort(key=lambda x: -x["resp_words"])

print(f"Total extracted: {len(tasks)}")
print(f"Non-trivial (>80 char prompt, >30 word response): {len(nontrivial)}")
print()

for i, t in enumerate(nontrivial[:40]):
    preview = t["prompt"][:130].replace("\n", " ")
    print(f"{i+1:2d}. [{t['agent']}] resp={t['resp_words']:4d}w len={t['prompt_len']:4d} | {preview}")
