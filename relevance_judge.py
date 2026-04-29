#!/usr/bin/env python3
"""
Relevance Judge — 3-model consensus panel.
Judges: Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro Preview
Scores each model output for relevance to the task/question asked.
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

RELEVANCE_PROMPT = """You are a relevance judge. Score this AI response for RELEVANCE (how well it addresses the specific task/question asked) on a scale of 1-10.

Criteria:
- 10: Directly and completely addresses every aspect of the question. No off-topic content. Follows all specified constraints and format requirements.
- 7-9: Addresses the core question well with minor gaps or slight tangential content.
- 4-6: Partially addresses the question but misses key aspects, includes significant filler, or goes off-topic.
- 1-3: Mostly off-topic, ignores the question's constraints, or answers a different question entirely.

Focus on:
- Does it answer the SPECIFIC question asked (not a related but different topic)?
- Does it follow format/constraint requirements?
- Does it avoid unnecessary padding or filler?
- Does it address ALL parts of a multi-part question?

Task: {task_id}
Model: {model_id}

Original task/question:
{task_prompt}

Response to evaluate:
{response_text}

Reply with ONLY a JSON object: {{"relevance_score": <1-10>, "missed_aspects": ["list of specific parts of the question not addressed"], "justification": "one paragraph"}}"""


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
            if "relevance_score" in data: return data
        except: pass
    match = re.search(r'"relevance_score"\s*:\s*(\d+)', text)
    if match: return {"relevance_score": int(match.group(1)), "justification": text[:300]}
    return None


def load_task_prompts(results_dir):
    task_prompts = {}
    tasks_file = BENCHMARK_DIR / "tasks.json"
    if tasks_file.exists():
        tasks = json.loads(tasks_file.read_text())
        if isinstance(tasks, list):
            for t in tasks: task_prompts[t["id"]] = t.get("prompt", "")
    # Check task dirs for prompt files
    raw_dir = results_dir / "raw"
    for task_dir in raw_dir.iterdir():
        if task_dir.is_dir():
            prompt_file = task_dir / "prompt.txt"
            if prompt_file.exists(): task_prompts[task_dir.name] = prompt_file.read_text()[:4000]
    return task_prompts


def main():
    if len(sys.argv) < 2:
        print("Usage: relevance_judge.py <results_dir>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    raw_dir = results_dir / "raw"
    output_file = results_dir / "relevance_scores.json"

    task_prompts = load_task_prompts(results_dir)
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
            task_prompt = task_prompts.get(task_id, f"[Task: {task_id}]")[:4000]
            tasks.append((task_id, model_id, task_prompt, result.get("response_text", "")[:8000]))

    total = len(tasks)
    print(f"Relevance consensus judge: {total} task-model pairs to score")

    for task_id, model_id, task_prompt, response_text in tasks:
        print(f"Judging {task_id} × {model_id}...", end=" ", flush=True)
        if task_id not in existing: existing[task_id] = {}
        if model_id not in existing[task_id]: existing[task_id][model_id] = {"judges": []}
        
        for judge_model in JUDGE_MODELS:
            if any(j["judge"] == judge_model for j in existing[task_id][model_id]["judges"]):
                continue
            
            prompt = RELEVANCE_PROMPT.format(task_id=task_id, model_id=model_id, task_prompt=task_prompt, response_text=response_text)
            raw = send_with_retry(judge_model, prompt)
            parsed = parse_response(raw)
            if parsed:
                existing[task_id][model_id]["judges"].append({
                    "judge": judge_model,
                    "score": parsed["relevance_score"],
                    "justification": parsed.get("justification", ""),
                    "missed": parsed.get("missed_aspects", [])
                })
        
        all_scores = [j["score"] for j in existing[task_id][model_id]["judges"] if j.get("score") is not None]
        if all_scores:
            existing[task_id][model_id]["score"] = round(statistics.median(all_scores), 1)
            print(f"median_score={existing[task_id][model_id]['score']}")
        
        with open(output_file, "w") as f: json.dump(existing, f, indent=2)

    print(f"\nRelevance consensus complete: {output_file}")

if __name__ == "__main__":
    main()
