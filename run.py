#!/usr/bin/env python3
"""
Model Benchmark Runner v4
Replays benchmark tasks against all configured models.
Captures: response text, tokens, TTFT, latency, tokens/sec, code pass rate.
Supports: Chat Completions API (LiteLLM), Responses API (LiteLLM + Azure direct).
Resumable: skips completed (task, model) pairs.
v4: thinking=high for all models, retry with backoff, bumped timeouts.
"""

import json, os, sys, time, urllib.request, urllib.error, subprocess, re
from pathlib import Path
from datetime import datetime

BENCHMARK_DIR = Path(__file__).parent
CONFIG_DIR = BENCHMARK_DIR / "config"
TASKS_DIR = BENCHMARK_DIR / "tasks"
API_KEY = "dummy-key"  # LiteLLM proxy key
VERSION_PREFIX = "v4"
MAX_RETRIES = 3

# Models that should skip thinking (log thinking_skipped)
THINKING_SKIP_CHAT = {"claude-haiku-4-5"}
THINKING_SKIP_GEMINI = {"gemini-2.5-pro"}

def get_vault_secret(secret_id):
    """Get secret from ClawGuard vault."""
    try:
        result = subprocess.run(
            ["/opt/homebrew/Cellar/node/25.8.0/bin/node",
             os.path.expanduser("~/.openclaw/extensions/clawguard/bin/clawguard-vault-get.mjs"),
             secret_id],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"  ⚠ Vault error for {secret_id}: {e}")
        return None

def load_config():
    with open(CONFIG_DIR / "models.json") as f:
        return json.load(f)

def load_tasks():
    tasks = []
    for task_dir in sorted(TASKS_DIR.iterdir()):
        if not task_dir.is_dir():
            continue
        prompt_file = task_dir / "prompt.md"
        rubric_file = task_dir / "rubric.json"
        if not prompt_file.exists():
            continue
        task = {
            "id": task_dir.name,
            "prompt": prompt_file.read_text().strip(),
            "rubric": json.loads(rubric_file.read_text()) if rubric_file.exists() else {},
            "has_test": (task_dir / "test.py").exists(),
            "test_path": str(task_dir / "test.py"),
            "category": task_dir.name.rsplit("-", 1)[0] if "-" in task_dir.name else "unknown",
        }
        tasks.append(task)
    return tasks

def get_thinking_params(model_id, model_cfg):
    """Return thinking/reasoning params for a model, or None to skip."""
    family = model_cfg.get("family", "")
    api = model_cfg.get("api", "")

    # Anthropic models via chat completions
    if family == "claude":
        if model_id in THINKING_SKIP_CHAT:
            return None, True  # skip, log thinking_skipped
        # opus-4-7, opus-4-6, opus-4-6-1m, sonnet-4-6, sonnet-4-5
        return {"thinking": {"type": "enabled", "budget_tokens": 16000}}, False

    # Google models
    if family == "google":
        if model_id in THINKING_SKIP_GEMINI:
            return None, True
        return {"extra_body": {"thinking_config": {"thinking_budget": 16000}}}, False

    # OpenAI models
    if family == "openai":
        if api == "chat":
            # gpt-5-mini uses chat completions
            return {"reasoning_effort": "high"}, False
        else:
            # responses API (gpt-5.x, azure/*)
            return {"reasoning": {"effort": "high"}}, False

    return {}, False

def send_chat_completion(model_id, model_cfg, prompt, max_tokens=16000):
    endpoint = model_cfg["endpoint"]
    thinking_params, thinking_skipped = get_thinking_params(model_id, model_cfg)

    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }
    if model_cfg.get("supports_max_tokens", True):
        body["max_tokens"] = max_tokens

    # Apply thinking params
    if thinking_params and not thinking_skipped:
        if "thinking" in thinking_params:
            body["thinking"] = thinking_params["thinking"]
            # Anthropic thinking requires temperature unset or 1
            body.pop("temperature", None)
        elif "reasoning_effort" in thinking_params:
            body["reasoning_effort"] = thinking_params["reasoning_effort"]
            if model_cfg.get("supports_temperature", True):
                body["temperature"] = 0
        elif "extra_body" in thinking_params:
            body["extra_body"] = thinking_params["extra_body"]
            if model_cfg.get("supports_temperature", True):
                body["temperature"] = 0
        else:
            if model_cfg.get("supports_temperature", True):
                body["temperature"] = 0
    else:
        if model_cfg.get("supports_temperature", True):
            body["temperature"] = 0

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(), headers=headers)

    start_time = time.time()
    ttft = None
    chunks = []
    output_tokens = 0
    input_tokens = 0

    try:
        with urllib.request.urlopen(req, timeout=450) as resp:  # +50% from 300
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                if ttft is None:
                    delta = choices[0].get("delta", {})
                    if delta.get("content"):
                        ttft = (time.time() - start_time) * 1000
                delta = choices[0].get("delta", {})
                if delta.get("content"):
                    chunks.append(delta["content"])
                usage = chunk.get("usage", {})
                if usage.get("completion_tokens"):
                    output_tokens = usage["completion_tokens"]
                if usage.get("prompt_tokens"):
                    input_tokens = usage["prompt_tokens"]

    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, Exception) as e:
        total_time = (time.time() - start_time) * 1000
        error_msg = str(e)
        if hasattr(e, 'read'):
            try:
                error_msg = e.read().decode()[:500]
            except:
                pass
        return None, {
            "error": error_msg,
            "total_latency_ms": total_time,
            "thinking_skipped": thinking_skipped,
        }

    total_time = (time.time() - start_time) * 1000
    response_text = "".join(chunks)

    if output_tokens == 0:
        output_tokens = len(response_text) // 4
    if input_tokens == 0:
        input_tokens = len(prompt) // 4

    generation_time = total_time - (ttft or 0)
    tokens_per_sec = (output_tokens / (generation_time / 1000)) if generation_time > 0 else 0

    return response_text, {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "ttft_ms": round(ttft, 1) if ttft else None,
        "total_latency_ms": round(total_time, 1),
        "tokens_per_sec": round(tokens_per_sec, 1),
        "thinking_skipped": thinking_skipped,
    }

def send_responses_api(model_id, model_cfg, prompt, max_tokens=16000):
    endpoint = model_cfg["endpoint"]
    api_model = model_id.split("/")[-1] if "/" in model_id else model_id
    thinking_params, thinking_skipped = get_thinking_params(model_id, model_cfg)

    body = {
        "model": api_model,
        "input": prompt,
        "max_output_tokens": max_tokens,
    }

    # Apply reasoning params for responses API
    if thinking_params and not thinking_skipped:
        if "reasoning" in thinking_params:
            body["reasoning"] = thinking_params["reasoning"]

    headers = {"Content-Type": "application/json"}

    if model_cfg.get("auth_header") == "api-key":
        secret = get_vault_secret(model_cfg["auth_secret"])
        if not secret:
            return None, {"error": "Failed to get vault secret"}
        headers["api-key"] = secret
    else:
        headers["Authorization"] = f"Bearer {API_KEY}"

    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(), headers=headers)

    timeout_sec = 900 if model_cfg.get("provider") == "azure" else 450  # +50%
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read())
            total_time = (time.time() - start_time) * 1000

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
                                    if isinstance(c, dict):
                                        if c.get("type") == "output_text" and c.get("text"):
                                            texts.append(c["text"])
                                        elif c.get("text"):
                                            texts.append(c["text"])
                            elif isinstance(content, str):
                                texts.append(content)
                    response_text = "\n".join(texts)

            usage = data.get("usage", {})
            input_tokens = usage.get("input_tokens", len(prompt) // 4)
            output_tokens = usage.get("output_tokens", len(response_text) // 4)
            tokens_per_sec = (output_tokens / (total_time / 1000)) if total_time > 0 else 0

            return response_text, {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "ttft_ms": None,
                "total_latency_ms": round(total_time, 1),
                "tokens_per_sec": round(tokens_per_sec, 1),
                "thinking_skipped": thinking_skipped,
            }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, Exception) as e:
        total_time = (time.time() - start_time) * 1000
        error_msg = str(e)
        if hasattr(e, 'read'):
            try:
                error_msg = e.read().decode()[:500]
            except:
                pass
        return None, {"error": error_msg, "total_latency_ms": total_time, "thinking_skipped": thinking_skipped}

def send_request(model_id, model_cfg, prompt):
    if model_cfg["api"] == "responses":
        return send_responses_api(model_id, model_cfg, prompt)
    else:
        return send_chat_completion(model_id, model_cfg, prompt)

def send_request_with_retry(model_id, model_cfg, prompt):
    """Send request with exponential backoff retries."""
    for attempt in range(MAX_RETRIES):
        response_text, metrics = send_request(model_id, model_cfg, prompt)
        if response_text is not None:
            return response_text, metrics
        # Check if thinking param rejection — fallback without thinking
        err = metrics.get("error", "")
        if "thinking" in err.lower() or "reasoning" in err.lower():
            print(f"  ⚠ Thinking rejected, falling back without thinking params")
            # Temporarily mark as skip
            orig_family = model_cfg.get("family", "")
            THINKING_SKIP_CHAT.add(model_id)
            THINKING_SKIP_GEMINI.add(model_id)
            response_text, metrics = send_request(model_id, model_cfg, prompt)
            THINKING_SKIP_CHAT.discard(model_id)
            THINKING_SKIP_GEMINI.discard(model_id)
            metrics["thinking_fallback"] = True
            return response_text, metrics
        if attempt < MAX_RETRIES - 1:
            wait = 2 ** (attempt + 1)
            print(f"  ⚠ Retry {attempt+1}/{MAX_RETRIES} in {wait}s...")
            time.sleep(wait)
    return None, metrics

def extract_code(response_text):
    match = re.search(r'```(?:python)?\s*\n(.*?)```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    if "import " in response_text or "def " in response_text:
        return response_text.strip()
    return response_text.strip()

def run_code_test(task, response_text):
    if not task["has_test"]:
        return None
    code = extract_code(response_text)
    tmp_file = f"/tmp/benchmark_code_{task['id']}.py"
    with open(tmp_file, "w") as f:
        f.write(code)
    try:
        result = subprocess.run(
            ["python3", task["test_path"], tmp_file],
            capture_output=True, text=True, timeout=60  # +50% from 30 for harder tasks
        )
        output = result.stdout
        match = re.search(r'Pass rate: (\d+)/(\d+)', output)
        if match:
            passed, total = int(match.group(1)), int(match.group(2))
            return round(100 * passed / total) if total > 0 else 0
        return 0
    except Exception:
        return 0
    finally:
        try:
            os.unlink(tmp_file)
        except:
            pass

def compute_cost(model_cfg, input_tokens, output_tokens):
    pricing = model_cfg.get("pricing", {})
    input_cost = (input_tokens / 1_000_000) * pricing.get("input_per_mtok", 0)
    output_cost = (output_tokens / 1_000_000) * pricing.get("output_per_mtok", 0)
    return round(input_cost + output_cost, 6)

def main():
    config = load_config()
    models = config["models"]
    tasks = load_tasks()

    if not tasks:
        print("No tasks found in tasks/ directory")
        sys.exit(1)

    print(f"Loaded {len(tasks)} tasks, {len(models)} models")
    print(f"Total runs: {len(tasks) * len(models)}")

    # Create results directory
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    results_dir = BENCHMARK_DIR / "results" / f"{VERSION_PREFIX}-{timestamp}"
    raw_dir = results_dir / "raw"

    if "--resume" in sys.argv:
        results_parent = BENCHMARK_DIR / "results"
        existing = sorted([d for d in results_parent.iterdir() if d.name.startswith(f"{VERSION_PREFIX}-")], reverse=True)
        if existing:
            results_dir = existing[0]
            raw_dir = results_dir / "raw"
            print(f"Resuming from {results_dir}")

    raw_dir.mkdir(parents=True, exist_ok=True)

    completed = 0
    skipped = 0
    failed = 0
    total = len(tasks) * len(models)

    for task in tasks:
        task_dir = raw_dir / task["id"]
        task_dir.mkdir(exist_ok=True)

        for model_id, model_cfg in models.items():
            safe_model_id = model_id.replace("/", "_")
            result_file = task_dir / f"{safe_model_id}.json"

            if result_file.exists():
                skipped += 1
                continue

            completed += 1
            progress = f"[{completed + skipped}/{total}]"
            print(f"{progress} {task['id']} × {model_id}...", end=" ", flush=True)

            response_text, metrics = send_request_with_retry(model_id, model_cfg, task["prompt"])

            if response_text is None:
                failed += 1
                print(f"❌ {metrics.get('error', 'unknown')[:80]}")
                result = {
                    "task_id": task["id"],
                    "model_id": model_id,
                    "status": "error",
                    "error": metrics.get("error", "unknown"),
                    "metrics": metrics,
                }
            else:
                code_pass_rate = None
                if task["rubric"].get("grading") == "automated" and task["has_test"]:
                    code_pass_rate = run_code_test(task, response_text)

                cost = compute_cost(model_cfg, metrics.get("input_tokens", 0), metrics.get("output_tokens", 0))

                status_icon = "✅" if not metrics.get("error") else "⚠️"
                speed_info = f"{metrics.get('tokens_per_sec', 0):.0f} tok/s"
                ttft_info = f"TTFT {metrics.get('ttft_ms', 0):.0f}ms" if metrics.get('ttft_ms') else "no TTFT"
                code_info = f" code={code_pass_rate}%" if code_pass_rate is not None else ""
                thinking_info = " [no-think]" if metrics.get("thinking_skipped") else ""
                print(f"{status_icon} {speed_info} | {ttft_info} | {metrics['total_latency_ms']:.0f}ms{code_info}{thinking_info}")

                result = {
                    "task_id": task["id"],
                    "model_id": model_id,
                    "status": "ok",
                    "response_text": response_text,
                    "metrics": {
                        **metrics,
                        "cost_usd": cost,
                        "code_pass_rate": code_pass_rate,
                    },
                    "category": task["rubric"].get("category", task["category"]),
                    "difficulty": task["rubric"].get("difficulty", "unknown"),
                    "family": model_cfg.get("family", "unknown"),
                }

            with open(result_file, "w") as f:
                json.dump(result, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Benchmark complete: {results_dir}")
    print(f"  Completed: {completed}")
    print(f"  Skipped (resumed): {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Results: {raw_dir}")

if __name__ == "__main__":
    main()
