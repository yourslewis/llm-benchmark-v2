#!/usr/bin/env python3
"""Test script for code-01: Model smoke test script."""
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
        return results  # Can't test further if syntax fails

    # T2: Uses stdlib only (no pip imports)
    banned = ["requests", "httpx", "aiohttp", "rich", "tabulate", "click"]
    found_banned = [b for b in banned if re.search(rf'\bimport\s+{b}\b|\bfrom\s+{b}\b', code_text)]
    if not found_banned:
        results["passed"] += 1
        results["details"].append(("stdlib_only", "PASS", "No banned imports"))
    else:
        results["failed"] += 1
        results["details"].append(("stdlib_only", "FAIL", f"Banned imports: {found_banned}"))

    # T3: Loads JSON from file/argument
    if "json" in code_text and ("argv" in code_text or "argparse" in code_text or "sys.argv" in code_text):
        results["passed"] += 1
        results["details"].append(("json_loading", "PASS", "Loads JSON from argument"))
    else:
        results["failed"] += 1
        results["details"].append(("json_loading", "FAIL", "Missing JSON file loading from argument"))

    # T4: Makes HTTP request to correct endpoint
    if "chat/completions" in code_text and ("urlopen" in code_text or "urllib" in code_text or "Request" in code_text):
        results["passed"] += 1
        results["details"].append(("api_call", "PASS", "HTTP POST to chat/completions"))
    else:
        results["failed"] += 1
        results["details"].append(("api_call", "FAIL", "Missing HTTP call to chat/completions"))

    # T5: Error handling
    if "except" in code_text and ("timeout" in code_text.lower() or "error" in code_text.lower()):
        results["passed"] += 1
        results["details"].append(("error_handling", "PASS", "Has error handling"))
    else:
        results["failed"] += 1
        results["details"].append(("error_handling", "FAIL", "Missing error handling"))

    # T6: Table-like output
    if "print" in code_text and ("{" in code_text or "format" in code_text or "f\"" in code_text or ":<" in code_text):
        results["passed"] += 1
        results["details"].append(("table_output", "PASS", "Has formatted output"))
    else:
        results["failed"] += 1
        results["details"].append(("table_output", "FAIL", "Missing formatted table output"))

    # T7: Summary line
    if ("total" in code_text.lower() or "summary" in code_text.lower()) and ("working" in code_text.lower() or "passed" in code_text.lower() or "failed" in code_text.lower()):
        results["passed"] += 1
        results["details"].append(("summary_line", "PASS", "Has summary"))
    else:
        results["failed"] += 1
        results["details"].append(("summary_line", "FAIL", "Missing summary line"))

    return results

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    r = test_code(code)
    total = r["passed"] + r["failed"]
    for name, status, detail in r["details"]:
        print(f"  {status} {name}: {detail}")
    print(f"\nPass rate: {r['passed']}/{total} ({100*r['passed']/total:.0f}%)")
