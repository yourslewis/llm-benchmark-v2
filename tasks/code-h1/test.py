#!/usr/bin/env python3
"""Test for code-h1: concurrency bug fix. Runs 1000 iterations to verify no race."""
import sys, subprocess, asyncio, tempfile, os

def main():
    if len(sys.argv) < 2:
        print("Usage: test.py <solution.py>")
        sys.exit(1)

    solution_path = sys.argv[1]
    with open(solution_path) as f:
        solution_code = f.read()

    # Write test harness
    test_code = solution_code + """

import asyncio, random

async def test_race_condition(iteration):
    results_seen = set()
    N = 20

    async def flaky_handler(payload):
        await asyncio.sleep(random.uniform(0, 0.001))
        return payload * 2

    pool = AsyncWorkerPool(max_workers=5, max_retries=1)
    pool.register_handler("test", flaky_handler)

    for i in range(N):
        await pool.submit(i, handler="test")

    results = await pool.run_all("test")

    # All N items should be in results
    assert len(results) == N, f"Iter {iteration}: Expected {N} results, got {len(results)}"

    # Stats should be consistent
    stats = await pool.get_stats()
    assert stats["completed"] == N, f"Iter {iteration}: Expected {N} completed, got {stats['completed']}"
    assert stats["active_workers"] == 0, f"Iter {iteration}: Active workers should be 0, got {stats['active_workers']}"

    # Results should be correct
    for i in range(N):
        item_id = i + 1
        assert item_id in results, f"Iter {iteration}: Missing result for item {item_id}"
        assert results[item_id] == i * 2, f"Iter {iteration}: Wrong result for item {item_id}"

async def run_all_tests():
    passed = 0
    failed = 0
    for i in range(1000):
        try:
            await test_race_condition(i)
            passed += 1
        except (AssertionError, Exception) as e:
            failed += 1
            if failed <= 3:
                print(f"  FAIL iter {i}: {e}")
    print(f"Pass rate: {passed}/1000")

asyncio.run(run_all_tests())
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        test_file = f.name

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True, text=True, timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr[:500], file=sys.stderr)
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    main()
