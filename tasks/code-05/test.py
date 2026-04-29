#!/usr/bin/env python3
"""Test script for code-05: Median of Two Sorted Arrays + Streaming."""
import ast, sys, re

def test_code(code_text):
    results = {"passed": 0, "failed": 0, "details": []}
    
    try:
        ast.parse(code_text)
        results["passed"] += 1
        results["details"].append(("syntax", "PASS", "Valid Python"))
    except SyntaxError as e:
        results["failed"] += 1
        results["details"].append(("syntax", "FAIL", str(e)))
        return results

    # T2: Binary search (not merge)
    if any(x in code_text for x in ['binary', 'lo', 'hi', 'left', 'right', 'mid', 'partition', 'bisect']):
        if 'merge' not in code_text.lower().split('def ')[0] if 'def ' in code_text else True:
            results["passed"] += 1
            results["details"].append(("binary_search", "PASS", "Binary search approach detected"))
        else:
            results["failed"] += 1
            results["details"].append(("binary_search", "FAIL", "Appears to use merge approach"))
    else:
        results["failed"] += 1
        results["details"].append(("binary_search", "FAIL", "No binary search patterns found"))

    # T3: Part 1 correctness
    try:
        exec_globals = {}
        exec(code_text, exec_globals)
        fn = exec_globals.get('findMedianSortedArrays') or exec_globals.get('find_median_sorted_arrays')
        if fn:
            tests = [
                ([1, 3], [2], 2.0),
                ([1, 2], [3, 4], 2.5),
                ([], [1], 1.0),
                ([1, 3, 5, 7, 9, 11], [2, 4, 6, 8, 10, 12], 6.5),
                ([1], [1], 1.0),
                ([1, 2, 3], [], 2.0),
            ]
            all_pass = True
            for n1, n2, expected in tests:
                result = fn(n1, n2)
                if abs(result - expected) > 0.001:
                    all_pass = False
                    results["details"].append(("part1_correctness", "FAIL", f"fn({n1},{n2})={result}, expected {expected}"))
                    break
            if all_pass:
                results["passed"] += 1
                results["details"].append(("part1_correctness", "PASS", f"All {len(tests)} test cases passed"))
            else:
                results["failed"] += 1
        else:
            results["failed"] += 1
            results["details"].append(("part1_correctness", "FAIL", "findMedianSortedArrays not found"))
    except Exception as e:
        results["failed"] += 1
        results["details"].append(("part1_correctness", "FAIL", str(e)[:100]))

    # T4: StreamingMedian class
    if re.search(r'class\s+StreamingMedian', code_text):
        results["passed"] += 1
        results["details"].append(("streaming_class", "PASS", "StreamingMedian class found"))
    else:
        results["failed"] += 1
        results["details"].append(("streaming_class", "FAIL", "No StreamingMedian class"))

    # T5: Heap approach
    if 'heapq' in code_text or 'heappush' in code_text or 'heap' in code_text.lower():
        results["passed"] += 1
        results["details"].append(("heap_approach", "PASS", "Heap-based approach"))
    else:
        results["failed"] += 1
        results["details"].append(("heap_approach", "FAIL", "No heap usage"))

    # T6: Part 2 correctness
    try:
        exec_globals2 = {}
        exec(code_text, exec_globals2)
        SM = exec_globals2.get('StreamingMedian')
        if SM:
            sm = SM()
            sm.add(1)
            assert sm.median() == 1.0, f"After [1]: expected 1.0, got {sm.median()}"
            sm.add(2)
            assert sm.median() == 1.5, f"After [1,2]: expected 1.5, got {sm.median()}"
            sm.add(3)
            assert sm.median() == 2.0, f"After [1,2,3]: expected 2.0, got {sm.median()}"
            sm.add(4)
            assert sm.median() == 2.5, f"After [1,2,3,4]: expected 2.5, got {sm.median()}"
            sm.add(0)
            assert sm.median() == 2.0, f"After [0,1,2,3,4]: expected 2.0, got {sm.median()}"
            results["passed"] += 1
            results["details"].append(("part2_correctness", "PASS", "Streaming median tests passed"))
        else:
            results["failed"] += 1
            results["details"].append(("part2_correctness", "FAIL", "StreamingMedian not found"))
    except Exception as e:
        results["failed"] += 1
        results["details"].append(("part2_correctness", "FAIL", str(e)[:100]))

    # T7: Type hints
    if '->' in code_text and ':' in code_text and ('int' in code_text or 'float' in code_text or 'List' in code_text):
        results["passed"] += 1
        results["details"].append(("type_hints", "PASS", "Type hints present"))
    else:
        results["failed"] += 1
        results["details"].append(("type_hints", "FAIL", "No type hints"))

    # T8: Edge cases handled
    if 'len' in code_text and ('0' in code_text or 'empty' in code_text.lower() or 'not ' in code_text):
        results["passed"] += 1
        results["details"].append(("edge_cases", "PASS", "Edge case handling detected"))
    else:
        results["failed"] += 1
        results["details"].append(("edge_cases", "FAIL", "No edge case handling"))

    return results

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    r = test_code(code)
    total = r["passed"] + r["failed"]
    for name, status, detail in r["details"]:
        print(f"  {status} {name}: {detail}")
    print(f"\nPass rate: {r['passed']}/{total} ({100*r['passed']/total:.0f}%)")
