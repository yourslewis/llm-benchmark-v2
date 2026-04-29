#!/usr/bin/env python3
"""Test script for code-02: Telegram notification in security plugin."""
import ast, sys, re

def test_code(code_text):
    results = {"passed": 0, "failed": 0, "details": []}

    # T1: Valid JavaScript syntax check (basic — look for obvious errors)
    # Since it's JS not Python, we do a text-level check
    if "module.exports" in code_text and "onToolCall" in code_text:
        results["passed"] += 1
        results["details"].append(("structure", "PASS", "Plugin structure intact"))
    else:
        results["failed"] += 1
        results["details"].append(("structure", "FAIL", "Missing module.exports or onToolCall"))

    # T2: Uses api.message()
    if "api.message(" in code_text:
        results["passed"] += 1
        results["details"].append(("api_message", "PASS", "Uses api.message()"))
    else:
        results["failed"] += 1
        results["details"].append(("api_message", "FAIL", "Missing api.message() call"))

    # T3: Uses await with api.message
    if re.search(r'await\s+api\.message\s*\(', code_text):
        results["passed"] += 1
        results["details"].append(("await_message", "PASS", "Uses await api.message()"))
    else:
        results["failed"] += 1
        results["details"].append(("await_message", "FAIL", "Missing await before api.message()"))

    # T4: Uses config.notifyChannel as target
    if "config.notifyChannel" in code_text and "target" in code_text:
        results["passed"] += 1
        results["details"].append(("notify_channel", "PASS", "Uses config.notifyChannel as target"))
    else:
        results["failed"] += 1
        results["details"].append(("notify_channel", "FAIL", "Missing config.notifyChannel target"))

    # T5: Checks notifyChannel is set before sending
    if re.search(r'if\s*\(.*notifyChannel', code_text) or re.search(r'notifyChannel\s*&&', code_text) or re.search(r'notifyChannel\s*\?', code_text):
        results["passed"] += 1
        results["details"].append(("guard_check", "PASS", "Guards on notifyChannel being set"))
    else:
        results["failed"] += 1
        results["details"].append(("guard_check", "FAIL", "Missing guard: notifyChannel may be null"))

    # T6: Notification includes toolName
    if re.search(r'toolName', code_text[code_text.find("api.message"):]) if "api.message" in code_text else False:
        results["passed"] += 1
        results["details"].append(("includes_toolname", "PASS", "Notification includes toolName"))
    else:
        # Check broadly
        api_msg_idx = code_text.find("api.message")
        if api_msg_idx != -1 and "toolName" in code_text[api_msg_idx:api_msg_idx+500]:
            results["passed"] += 1
            results["details"].append(("includes_toolname", "PASS", "Notification includes toolName"))
        else:
            results["failed"] += 1
            results["details"].append(("includes_toolname", "FAIL", "Notification message missing toolName"))

    # T7: Error handling around api.message
    if re.search(r'try\s*\{[^}]*api\.message', code_text, re.DOTALL) or re.search(r'\.catch\s*\(', code_text):
        results["passed"] += 1
        results["details"].append(("error_handling", "PASS", "Error handling around api.message"))
    else:
        results["failed"] += 1
        results["details"].append(("error_handling", "FAIL", "Missing try/catch around api.message"))

    # T8: All three TODO blocks are replaced
    todo_count = code_text.count("// TODO: Add Telegram notification here")
    if todo_count == 0:
        results["passed"] += 1
        results["details"].append(("todos_replaced", "PASS", "All TODO comments replaced"))
    else:
        results["failed"] += 1
        results["details"].append(("todos_replaced", "FAIL", f"{todo_count} TODO comment(s) still present"))

    # T9: Includes timestamp in message
    if "timestamp" in code_text.lower() or "toISOString" in code_text or "new Date" in code_text:
        results["passed"] += 1
        results["details"].append(("timestamp", "PASS", "Includes timestamp in notification"))
    else:
        results["failed"] += 1
        results["details"].append(("timestamp", "FAIL", "Missing timestamp in notification"))

    return results

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    r = test_code(code)
    total = r["passed"] + r["failed"]
    for name, status, detail in r["details"]:
        print(f"  {status} {name}: {detail}")
    print(f"\nPass rate: {r['passed']}/{total} ({100*r['passed']/total:.0f}%)")
