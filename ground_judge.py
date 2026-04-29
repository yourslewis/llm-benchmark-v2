#!/usr/bin/env python3
"""
Grounding/Fact-checking Judge — 3-model consensus panel.
Judges: Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro Preview
Scores each model output for factual accuracy and hallucination.
"""

import json, sys, time, urllib.request, urllib.error, re, statistics
from pathlib import Path
from collections import defaultdict

BENCHMARK_DIR = Path(__file__).parent
API_KEY = "dummy-key"
ENDPOINT_CHAT = "http://127.0.0.1:4040/v1/chat/completions"
ENDPOINT_RESPONSES = "http://127.0.0.1:4040/v1/responses"
JUDGE_MODELS = ["claude-opus-4-7", "gpt-5.5", "gemini-3.1-pro-preview"]
MAX_RETRIES = 3

GROUNDING_PROMPT = """You are a fact-checking judge. Score this AI response for GROUNDING (factual accuracy and absence of hallucination) on a scale of 1-10.

Criteria:
- 10: Every claim is verifiable and accurate. No fabricated facts, papers, numbers, or technical details.
- 7-9: Mostly accurate with minor imprecisions that don't mislead.
- 4-6: Contains some unverifiable or questionable claims.
- 1-3: Multiple fabricated facts, hallucinated references, or incorrect technical details.

Focus on:
- Are cited papers real and correctly described?
- Are technical claims accurate (math, complexity, numbers)?
- Are model names, architectures, and comparisons factual?
- Are any statistics or benchmarks fabricated?

Task: {task_id}
Model: {model_id}

Response to evaluate:
{response_text}

Reply with ONLY a JSON object: {{"grounding_score": <1-10>, "hallucinations_found": ["list of specific fabricated/incorrect claims"], "justification": "one paragraph"}}"""


def send_request(judge_model, prompt_text):
    if judge_model == "gpt-5.5":
        body = {"model": judge_model, "input": prompt_text, "reasoning": {"effort": "high"}}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
        req = urllib.request.Request(ENDPOINT_RESPONSES, data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
                return data.get("output_text", "").strip()
        except: return None
    else:
        body = {
            "model": judge_model,
            "messages": [{"role": "user", "content": prompt_text}],
        }
        if "claude" in judge_model:
            body["thinking"] = {"type": "enabled", "budget_tokens": 16000}
        elif "gemini" in judge_model:
            body["extra_body"] = {"thinking_config": {"thinking_budget": 16000}}

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
        req = urllib.request.Request(ENDPOINT_CHAT, data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if "thinking" in str(e).lower():
                body.pop("thinking", None)
                body.pop("extra_body", None)
                body["temperature"] = 0
                req2 = urllib.request.Request(ENDPOINT_CHAT, data=json.dumps(body).encode(), headers=headers)
                try:
                    with urllib.request.urlopen(req2, timeout=300) as resp:
                        data = json.loads(resp.read())
                        return data["choices"][0]["message"]["content"].strip()
                except: pass
            return None


def send_with_retry(judge_model, prompt_text):
    for attempt in range(MAX_RETRIES):
        result = send_request(judge_model, prompt_text)
        if result is not None: return result
        if attempt < MAX_RETRIES - 1: time.sleep(2 ** (attempt + 1))
    return None


def parse_response(text):
    if not text: return None
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if "grounding_score" in data: return data
        except: pass
    match = re.search(r'"grounding_score"\s*:\s*(\d+)', text)
    if match: return {"grounding_score": int(match.group(1)), "justification": text[:300]}
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: ground_judge.py <results_dir>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    raw_dir = results_dir / "raw"
    output_file = results_dir / "grounding_scores.json"

    existing = {}
    if output_file.exists(): existing = json.loads(output_file.read_text())

    tasks = []
    for task_dir in sorted(raw_dir.iterdir()):
        if not task_dir.is_dir(): continue
        task_id = task_dir.name
        for result_file in sorted(task_dir.glob("*.json")):
            result = json.loads(result_file.read_text())
            if result.get("status") != "ok": continue
            model_id = result["model_id"]
            if task_id in existing and model_id in existing[task_id] and len(existing[task_id][model_id].get("judges", [])) >= len(JUDGE_MODELS):
                continue
            tasks.append((task_id, model_id, result.get("response_text", "")[:8000]))

    total = len(tasks)
    print(f"Grounding consensus judge: {total} task-model pairs to score")

    for task_id, model_id, response_text in tasks:
        print(f"Judging {task_id} × {model_id}...", end=" ", flush=True)
        if task_id not in existing: existing[task_id] = {}
        if model_id not in existing[task_id]: existing[task_id][model_id] = {"judges": []}
        
        scores = []
        for judge_model in JUDGE_MODELS:
            # Skip if already judged by this model
            if any(j["judge"] == judge_model for j in existing[task_id][model_id]["judges"]):
                continue
            
            prompt = GROUNDING_PROMPT.format(task_id=task_id, model_id=model_id, response_text=response_text)
            raw = send_with_retry(judge_model, prompt)
            parsed = parse_response(raw)
            if parsed:
                existing[task_id][model_id]["judges"].append({
                    "judge": judge_model,
                    "score": parsed["grounding_score"],
                    "justification": parsed.get("justification", ""),
                    "hallucinations": parsed.get("hallucinations_found", [])
                })
        
        all_scores = [j["score"] for j in existing[task_id][model_id]["judges"] if j.get("score") is not None]
        if all_scores:
            existing[task_id][model_id]["score"] = round(statistics.median(all_scores), 1)
            print(f"median_score={existing[task_id][model_id]['score']}")
        
        with open(output_file, "w") as f: json.dump(existing, f, indent=2)

    print(f"\nGrounding consensus complete: {output_file}")

if __name__ == "__main__":
    main()
