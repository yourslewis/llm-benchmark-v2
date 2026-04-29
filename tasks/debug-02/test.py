#!/usr/bin/env python3
"""Test script for debug-02: fix_max_tokens.py script."""
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

    # T2: Uses stdlib only
    banned = ["requests", "httpx", "rich", "click", "yaml"]
    found_banned = [b for b in banned if re.search(rf'\bimport\s+{b}\b|\bfrom\s+{b}\b', code_text)]
    if not found_banned:
        results["passed"] += 1
        results["details"].append(("stdlib_only", "PASS", "No banned imports"))
    else:
        results["failed"] += 1
        results["details"].append(("stdlib_only", "FAIL", f"Banned imports: {found_banned}"))

    # T3: Defines CORRECT_LIMITS dict
    if "CORRECT_LIMITS" in code_text and "{" in code_text:
        results["passed"] += 1
        results["details"].append(("correct_limits", "PASS", "CORRECT_LIMITS dict defined"))
    else:
        results["failed"] += 1
        results["details"].append(("correct_limits", "FAIL", "Missing CORRECT_LIMITS dict"))

    # T4: Accepts config path from sys.argv
    if "sys.argv" in code_text or "argparse" in code_text:
        results["passed"] += 1
        results["details"].append(("file_arg", "PASS", "Accepts config path from arguments"))
    else:
        results["failed"] += 1
        results["details"].append(("file_arg", "FAIL", "Missing sys.argv or argparse for config path"))

    # T5: Reads and writes JSON
    if "json.load" in code_text and "json.dump" in code_text:
        results["passed"] += 1
        results["details"].append(("json_rw", "PASS", "Reads and writes JSON"))
    else:
        results["failed"] += 1
        results["details"].append(("json_rw", "FAIL", "Missing json.load or json.dump"))

    # T6: Creates backup (.bak)
    if ".bak" in code_text:
        results["passed"] += 1
        results["details"].append(("backup", "PASS", "Creates .bak backup"))
    else:
        results["failed"] += 1
        results["details"].append(("backup", "FAIL", "Missing .bak backup creation"))

    # T7: Dry-run mode
    if "dry" in code_text.lower() and ("dry_run" in code_text or "dry-run" in code_text or "dryrun" in code_text.lower()):
        results["passed"] += 1
        results["details"].append(("dry_run", "PASS", "Has dry-run mode"))
    else:
        results["failed"] += 1
        results["details"].append(("dry_run", "FAIL", "Missing --dry-run flag"))

    # T8: Updates maxTokens field
    if "maxTokens" in code_text:
        results["passed"] += 1
        results["details"].append(("max_tokens_key", "PASS", "References maxTokens key"))
    else:
        results["failed"] += 1
        results["details"].append(("max_tokens_key", "FAIL", "Missing maxTokens key reference"))

    # T9: Prints summary of changes
    if ("updated" in code_text.lower() or "changed" in code_text.lower()) and ("unchanged" in code_text.lower() or "no change" in code_text.lower()):
        results["passed"] += 1
        results["details"].append(("summary_output", "PASS", "Prints updated/unchanged summary"))
    else:
        results["failed"] += 1
        results["details"].append(("summary_output", "FAIL", "Missing updated/unchanged summary output"))

    # T10: Error handling
    if "FileNotFoundError" in code_text or "except" in code_text:
        results["passed"] += 1
        results["details"].append(("error_handling", "PASS", "Has error handling"))
    else:
        results["failed"] += 1
        results["details"].append(("error_handling", "FAIL", "Missing error handling"))

    # T11: Uses indent=2 for JSON output
    if "indent=2" in code_text or "indent = 2" in code_text:
        results["passed"] += 1
        results["details"].append(("json_indent", "PASS", "Preserves JSON formatting with indent=2"))
    else:
        results["failed"] += 1
        results["details"].append(("json_indent", "FAIL", "Missing indent=2 in json.dump"))

    return results

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    r = test_code(code)
    total = r["passed"] + r["failed"]
    for name, status, detail in r["details"]:
        print(f"  {status} {name}: {detail}")
    print(f"\nPass rate: {r['passed']}/{total} ({100*r['passed']/total:.0f}%)")
