#!/usr/bin/env python3
"""Test script for code-04: Lock-Free Concurrent LRU Cache."""
import ast, sys, re, threading

def test_code(code_text):
    results = {"passed": 0, "failed": 0, "details": []}
    
    # T1: Valid syntax
    try:
        ast.parse(code_text)
        results["passed"] += 1
        results["details"].append(("syntax", "PASS", "Valid Python"))
    except SyntaxError as e:
        results["failed"] += 1
        results["details"].append(("syntax", "FAIL", str(e)))
        return results

    # T2: LRUCache class exists
    if re.search(r'class\s+LRUCache', code_text):
        results["passed"] += 1
        results["details"].append(("lru_class", "PASS", "LRUCache class found"))
    else:
        results["failed"] += 1
        results["details"].append(("lru_class", "FAIL", "No LRUCache class"))

    # T3: Uses linked list or OrderedDict
    if any(x in code_text for x in ['OrderedDict', 'prev', 'next', 'Node', 'head', 'tail', 'doubly']):
        results["passed"] += 1
        results["details"].append(("doubly_linked_list", "PASS", "LRU ordering structure found"))
    else:
        results["failed"] += 1
        results["details"].append(("doubly_linked_list", "FAIL", "No LRU ordering structure"))

    # T4: Hash map / dict
    if 'dict' in code_text.lower() or '{}' in code_text or 'self.cache' in code_text or 'self.map' in code_text:
        results["passed"] += 1
        results["details"].append(("hash_map", "PASS", "Dict/hashmap found"))
    else:
        results["failed"] += 1
        results["details"].append(("hash_map", "FAIL", "No dict/hashmap"))

    # T5: Capacity eviction
    if 'capacity' in code_text.lower() and ('evict' in code_text.lower() or 'pop' in code_text or 'del ' in code_text or 'remove' in code_text):
        results["passed"] += 1
        results["details"].append(("capacity_eviction", "PASS", "Eviction logic found"))
    else:
        results["failed"] += 1
        results["details"].append(("capacity_eviction", "FAIL", "No eviction logic"))

    # T6: Thread safety
    threading_patterns = ['Lock', 'RLock', 'Condition', 'Semaphore', 'threading', 'concurrent', 'atomic']
    if any(p in code_text for p in threading_patterns):
        results["passed"] += 1
        results["details"].append(("thread_safety", "PASS", "Threading primitives found"))
    else:
        results["failed"] += 1
        results["details"].append(("thread_safety", "FAIL", "No threading primitives"))

    # T7: No single global lock
    # Check if there's more than one lock, or striped locking, or lock-free approach
    lock_count = len(re.findall(r'Lock\(\)|RLock\(\)', code_text))
    has_striped = 'stripe' in code_text.lower() or 'shard' in code_text.lower() or 'bucket' in code_text.lower()
    has_per_node = 'node' in code_text.lower() and 'lock' in code_text.lower()
    if lock_count > 1 or has_striped or has_per_node or 'ReadWriteLock' in code_text or 'rwlock' in code_text.lower():
        results["passed"] += 1
        results["details"].append(("no_global_lock", "PASS", "Fine-grained locking detected"))
    else:
        results["failed"] += 1
        results["details"].append(("no_global_lock", "FAIL", f"Only {lock_count} lock(s) found — likely global lock"))

    # T8: Try to run basic correctness test
    try:
        exec_globals = {}
        exec(code_text, exec_globals)
        LRUCache = exec_globals.get('LRUCache')
        if LRUCache:
            cache = LRUCache(3)
            cache.put("a", "1")
            cache.put("b", "2")
            cache.put("c", "3")
            assert cache.get("a") == "1", f"Expected '1', got {cache.get('a')}"
            cache.put("d", "4")
            assert cache.get("b") is None, f"Expected None, got {cache.get('b')}"
            assert cache.get("c") == "3"
            assert cache.get("d") == "4"
            results["passed"] += 1
            results["details"].append(("correctness", "PASS", "Basic LRU tests passed"))
        else:
            results["failed"] += 1
            results["details"].append(("correctness", "FAIL", "LRUCache not found in exec"))
    except Exception as e:
        results["failed"] += 1
        results["details"].append(("correctness", "FAIL", str(e)[:100]))

    return results

if __name__ == "__main__":
    code = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    r = test_code(code)
    total = r["passed"] + r["failed"]
    for name, status, detail in r["details"]:
        print(f"  {status} {name}: {detail}")
    print(f"\nPass rate: {r['passed']}/{total} ({100*r['passed']/total:.0f}%)")
