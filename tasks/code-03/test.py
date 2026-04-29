#!/usr/bin/env python3
"""Test script for code-03: Multi-API benchmark harness with TTFT measurement."""
import ast, sys, re

def test_code(code_text):
    results = {"passed": 0, "failed": 0, "details": []}

    # T1: Valid Python syntax
    try:
        ast.parse(code_text)
        results["passed"] += 1
        results["details"].append(("syntax", "PASS", "Valid Python"))
    except SyntaxError as e:
        results["failed"] += 1
        results["details"].append(("syntax", "FAIL", str(e)))
        return results

    # T2: Uses stdlib only (no banned imports)
    banned = ["requests", "httpx", "aiohttp", "sseclient", "rich", "click"]
    found_banned = [b for b in banned if re.search(rf'\bimport\s+{b}\b|\bfrom\s+{b}\b', code_text)]
    if not found_banned:
        results["passed"] += 1
        results["details"].append(("stdlib_only", "PASS", "No banned imports"))
    else:
        results["failed"] += 1
        results["details"].append(("stdlib_only", "FAIL", f"Banned imports: {found_banned}"))

    # T3: Uses urllib for HTTP
    if "urllib" in code_text and ("urlopen" in code_text or "Request" in code_text):
        results["passed"] += 1
        results["details"].append(("urllib_http", "PASS", "Uses urllib for HTTP"))
    else:
        results["failed"] += 1
        results["details"].append(("urllib_http", "FAIL", "Missing urllib HTTP calls"))

    # T4: Supports both API types
    has_chat = "chat_completions" in code_text or "chat/completions" in code_text
    has_responses = "responses" in code_text and ("api_type" in code_text or "/responses" in code_text)
    if has_chat and has_responses:
        results["passed"] += 1
        results["details"].append(("dual_api", "PASS", "Supports both chat_completions and responses API"))
    else:
        results["failed"] += 1
        results["details"].append(("dual_api", "FAIL", f"chat_completions={has_chat}, responses={has_responses}"))

    # T5: SSE parsing (data: prefix)
    if re.search(r'data:', code_text) and ("startswith" in code_text or "strip" in code_text):
        results["passed"] += 1
        results["details"].append(("sse_parsing", "PASS", "Parses SSE stream (data: prefix)"))
    else:
        results["failed"] += 1
        results["details"].append(("sse_parsing", "FAIL", "Missing SSE stream parsing"))

    # T6: TTFT measurement using time
    has_time = "time.time" in code_text or "time.perf_counter" in code_text or "time.monotonic" in code_text
    has_ttft = "ttft" in code_text.lower()
    if has_time and has_ttft:
        results["passed"] += 1
        results["details"].append(("ttft_measurement", "PASS", "Measures TTFT using time"))
    else:
        results["failed"] += 1
        results["details"].append(("ttft_measurement", "FAIL", f"time={has_time}, ttft_var={has_ttft}"))

    # T7: Saves JSON results
    if "json.dump" in code_text and ("benchmark_results" in code_text or "output" in code_text):
        results["passed"] += 1
        results["details"].append(("json_output", "PASS", "Saves results as JSON"))
    else:
        results["failed"] += 1
        results["details"].append(("json_output", "FAIL", "Missing JSON output save"))

    # T8: Result structure has required fields
    required_fields = ["ttft_ms", "total_ms", "status", "model_id"]
    found = [f for f in required_fields if f in code_text]
    if len(found) == len(required_fields):
        results["passed"] += 1
        results["details"].append(("result_structure", "PASS", "Result dict has all required fields"))
    else:
        missing = [f for f in required_fields if f not in code_text]
        results["failed"] += 1
        results["details"].append(("result_structure", "FAIL", f"Missing fields: {missing}"))

    # T9: ThreadPoolExecutor for parallelism
    if "ThreadPoolExecutor" in code_text or "concurrent.futures" in code_text:
        results["passed"] += 1
        results["details"].append(("parallelism", "PASS", "Uses ThreadPoolExecutor"))
    else:
        results["failed"] += 1
        results["details"].append(("parallelism", "FAIL", "Missing ThreadPoolExecutor"))

    # T10: CLI argument parsing
    if "argparse" in code_text and "--config" in code_text:
        results["passed"] += 1
        results["details"].append(("cli_args", "PASS", "Has argparse with --config"))
    else:
        results["failed"] += 1
        results["details"].append(("cli_args", "FAIL", "Missing argparse or --config argument"))

    # T11: Error handling per model
    if "except" in code_text and ("error" in code_text.lower() or "timeout" in code_text.lower()):
        results["passed"] += 1
        results["details"].append(("error_handling", "PASS", "Per-model error handling"))
    else:
        results["failed"] += 1
        results["details"].append(("error_handling", "FAIL", "Missing per-model error handling"))

    # T12: Summary block
    if "summary" in code_text and ("avg_ttft" in code_text or "fastest" in code_text or "total" in code_text):
        results["passed"] += 1
        results["details"].append(("summary", "PASS", "Includes summary block in output"))
    else:
        results["failed"] += 1
        results["details"].append(("summary", "FAIL", "Missing summary block"))

    return results

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    r = test_code(code)
    total = r["passed"] + r["failed"]
    for name, status, detail in r["details"]:
        print(f"  {status} {name}: {detail}")
    print(f"\nPass rate: {r['passed']}/{total} ({100*r['passed']/total:.0f}%)")
