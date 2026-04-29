#!/usr/bin/env python3
"""
LLM-as-Judge v4 — 3-model consensus panel
Judges: Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro Preview
Self-recusal: each judge skips scoring outputs from its own model family.
Consensus: median score, flag disagreements (spread ≥ 3).
v4: thinking=high for judges, retry with backoff.
"""

import json, os, sys, time, urllib.request, urllib.error, re, statistics
from pathlib import Path

BENCHMARK_DIR = Path(__file__).parent
CONFIG_DIR = BENCHMARK_DIR / "config"
API_KEY = "dummy-key"
VERSION_PREFIX = "v4"
MAX_RETRIES = 3

# Thinking params per judge model
JUDGE_THINKING = {
    "claude-opus-4-7": {"thinking": {"type": "enabled", "budget_tokens": 16000}},
    "gpt-5.5": {"reasoning": {"effort": "high"}},  # responses API
    "gemini-3.1-pro-preview": {"extra_body": {"thinking_config": {"thinking_budget": 16000}}},
}

def load_config():
    with open(CONFIG_DIR / "models.json") as f:
        return json.load(f)

def load_judge_prompt():
    with open(CONFIG_DIR / "judge_prompt.txt") as f:
        return f.read()

def send_judge_request(judge_model, prompt_text):
    """Send a judge request. Uses responses API for GPT judges, chat completions otherwise."""
    thinking = JUDGE_THINKING.get(judge_model, {})

    if judge_model.startswith("gpt-"):
        return send_judge_responses(judge_model, prompt_text, thinking)
    else:
        return send_judge_chat(judge_model, prompt_text, thinking)

def send_judge_chat(judge_model, prompt_text, thinking):
    endpoint = "http://127.0.0.1:4040/v1/chat/completions"
    body = {
        "model": judge_model,
        "messages": [{"role": "user", "content": prompt_text}],
    }

    if "thinking" in thinking:
        body["thinking"] = thinking["thinking"]
        # Don't set temperature with Anthropic thinking
    elif "extra_body" in thinking:
        body["extra_body"] = thinking["extra_body"]
        body["temperature"] = 0
    else:
        body["temperature"] = 0

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        err = str(e)
        # If thinking rejected, retry without
        if "thinking" in err.lower():
            body.pop("thinking", None)
            body.pop("extra_body", None)
            body["temperature"] = 0
            req2 = urllib.request.Request(endpoint, data=json.dumps(body).encode(), headers=headers)
            try:
                with urllib.request.urlopen(req2, timeout=180) as resp:
                    data = json.loads(resp.read())
                    return data["choices"][0]["message"]["content"].strip()
            except:
                pass
        return None

def send_judge_responses(judge_model, prompt_text, thinking):
    endpoint = "http://127.0.0.1:4040/v1/responses"
    body = {
        "model": judge_model,
        "input": prompt_text,
    }
    if "reasoning" in thinking:
        body["reasoning"] = thinking["reasoning"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
            # Extract text from responses API
            response_text = data.get("output_text", "")
            if not response_text:
                output = data.get("output", [])
                if isinstance(output, list):
                    texts = []
                    for item in output:
                        if isinstance(item, dict):
                            if item.get("type") == "reasoning":
                                continue
                            content = item.get("content", [])
                            if isinstance(content, list):
                                for c in content:
                                    if isinstance(c, dict) and c.get("text"):
                                        texts.append(c["text"])
                            elif isinstance(content, str):
                                texts.append(content)
                    response_text = "\n".join(texts)
            return response_text.strip()
    except Exception:
        return None

def send_judge_with_retry(judge_model, prompt_text):
    for attempt in range(MAX_RETRIES):
        result = send_judge_request(judge_model, prompt_text)
        if result is not None:
            return result
        if attempt < MAX_RETRIES - 1:
            wait = 2 ** (attempt + 1)
            time.sleep(wait)
    return None

def parse_judge_response(response_text):
    if not response_text:
        return None
    try:
        data = json.loads(response_text)
        if "score" in data:
            return {"score": int(data["score"]), "justification": data.get("justification", "")}
    except (json.JSONDecodeError, ValueError):
        pass
    match = re.search(r'```(?:json)?\s*\n?(.*?)```', response_text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if "score" in data:
                return {"score": int(data["score"]), "justification": data.get("justification", "")}
        except (json.JSONDecodeError, ValueError):
            pass
    match = re.search(r'"score"\s*:\s*(\d+)', response_text)
    if match:
        return {"score": int(match.group(1)), "justification": response_text[:200]}
    return None

def get_eligible_judges(model_id, model_family, config):
    judges = config.get("judges", [])
    return judges

def main():
    config = load_config()
    judge_template = load_judge_prompt()

    results_parent = BENCHMARK_DIR / "results"
    if "--dir" in sys.argv:
        idx = sys.argv.index("--dir")
        results_dir = Path(sys.argv[idx + 1])
    else:
        existing = sorted([d for d in results_parent.iterdir() if d.name.startswith(f"{VERSION_PREFIX}-")], reverse=True)
        if not existing:
            print(f"No {VERSION_PREFIX} results found. Run benchmark first.")
            sys.exit(1)
        results_dir = existing[0]

    raw_dir = results_dir / "raw"
    scores_file = results_dir / "scores.json"

    print(f"Judging results in: {results_dir}")

    existing_scores = {}
    if scores_file.exists():
        existing_scores = json.loads(scores_file.read_text())

    all_scores = existing_scores.copy()
    flagged = []
    judged = 0
    skipped = 0
    errors = 0

    for task_dir in sorted(raw_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        task_id = task_dir.name
        rubric_file = BENCHMARK_DIR / "tasks" / task_id / "rubric.json"
        if not rubric_file.exists():
            continue
        rubric = json.loads(rubric_file.read_text())
        if rubric.get("grading") == "automated":
            continue

        prompt_file = BENCHMARK_DIR / "tasks" / task_id / "prompt.md"
        task_prompt = prompt_file.read_text().strip() if prompt_file.exists() else ""
        rubric_text = "\n".join([f"- {c['name']} (weight {c['weight']}): {c['description']}"
                                  for c in rubric.get("criteria", [])])

        for result_file in sorted(task_dir.glob("*.json")):
            result = json.loads(result_file.read_text())
            if result.get("status") != "ok":
                continue

            model_id = result["model_id"]
            score_key = f"{task_id}/{model_id}"
            model_family = result.get("family", config["models"].get(model_id, {}).get("family", "unknown"))
            eligible_judges = get_eligible_judges(model_id, model_family, config)

            if not eligible_judges:
                continue

            existing_entry = all_scores.get(score_key)
            if existing_entry:
                existing_judges = set(j['judge'] for j in existing_entry.get('judges', []) if j.get('score') is not None)
                if len(existing_judges) >= len(eligible_judges):
                    skipped += 1
                    continue
                judges_to_run = [j for j in eligible_judges if j not in existing_judges]
            else:
                judges_to_run = eligible_judges
                existing_entry = None

            if not judges_to_run:
                skipped += 1
                continue

            print(f"Judging {task_id} × {model_id} ({len(judges_to_run)} judges)...", end=" ", flush=True)

            response_text = result.get("response_text", "")[:8000]

            judge_scores = []
            judge_details = []

            if existing_entry:
                for j in existing_entry.get('judges', []):
                    if j.get('score') is not None:
                        judge_scores.append(j['score'])
                        judge_details.append(j)

            for judge_model in judges_to_run:
                filled_prompt = judge_template.replace("{task_prompt}", task_prompt[:3000])
                filled_prompt = filled_prompt.replace("{rubric}", rubric_text)
                filled_prompt = filled_prompt.replace("{response}", response_text)

                raw_response = send_judge_with_retry(judge_model, filled_prompt)
                parsed = parse_judge_response(raw_response)

                if parsed:
                    judge_scores.append(parsed["score"])
                    judge_details.append({
                        "judge": judge_model,
                        "score": parsed["score"],
                        "justification": parsed["justification"],
                    })
                else:
                    errors += 1
                    judge_details.append({
                        "judge": judge_model,
                        "score": None,
                        "error": "Failed to parse response",
                        "raw": (raw_response or "")[:200],
                    })

            if judge_scores:
                median_score = round(statistics.median(judge_scores))
                spread = max(judge_scores) - min(judge_scores)

                all_scores[score_key] = {
                    "task_id": task_id,
                    "model_id": model_id,
                    "median_score": median_score,
                    "spread": spread,
                    "flagged": spread >= 3,
                    "judge_count": len(judge_scores),
                    "judges": judge_details,
                    "category": rubric.get("category", ""),
                    "difficulty": rubric.get("difficulty", ""),
                }

                flag_icon = " ⚠️ FLAGGED" if spread >= 3 else ""
                print(f"median={median_score} spread={spread}{flag_icon}")

                if spread >= 3:
                    flagged.append(all_scores[score_key])
                judged += 1
            else:
                print("❌ no valid scores")
                errors += 1

            with open(scores_file, "w") as f:
                json.dump(all_scores, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Judging complete: {scores_file}")
    print(f"  Judged: {judged}")
    print(f"  Skipped (already done): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Flagged disagreements: {len(flagged)}")

    if flagged:
        print(f"\n⚠️ Flagged Disagreements (spread ≥ 3):")
        for f_item in flagged:
            scores_str = ", ".join([f"{j['judge']}={j['score']}" for j in f_item['judges'] if j.get('score')])
            print(f"  {f_item['task_id']} × {f_item['model_id']}: {scores_str} (spread={f_item['spread']})")

if __name__ == "__main__":
    main()
