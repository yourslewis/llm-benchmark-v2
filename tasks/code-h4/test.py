#!/usr/bin/env python3
"""Tests for code-h4: SQL builder NULL bug fix."""
import sys, subprocess, tempfile, os

def main():
    if len(sys.argv) < 2:
        print("Usage: test.py <solution.py>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        code = f.read()

    test_code = code + '''

passed = 0
total = 0

def check(name, condition):
    global passed, total
    total += 1
    if condition:
        passed += 1
    else:
        print(f"  FAIL: {name}")

# Test 1: IN with NULL should produce (col IN (1,2) OR col IS NULL)
q = QueryBuilder("t").where(in_("status", [1, 2, None]))
sql, params = q.build()
check("in_null_has_is_null", "IS NULL" in sql)
check("in_null_has_or", "OR" in sql)
check("in_null_no_none_param", None not in params)

# Test 2: NOT IN with NULL should produce (col NOT IN (1,2) AND col IS NOT NULL)
q = QueryBuilder("t").where(not_in("status", [1, 2, None]))
sql, params = q.build()
check("not_in_null_has_is_not_null", "IS NOT NULL" in sql)
check("not_in_null_no_none_param", None not in params)

# Test 3: IN without NULL should work normally
q = QueryBuilder("t").where(in_("id", [1, 2, 3]))
sql, params = q.build()
check("in_normal", "IN (?, ?, ?)" in sql)
check("in_normal_params", params == [1, 2, 3])

# Test 4: Nested OR with IN NULL
q = QueryBuilder("t").where(or_(
    in_("status", [1, None]),
    eq("name", "test")
))
sql, params = q.build()
check("nested_or_in_null", "IS NULL" in sql)
check("nested_or_parens", sql.count("(") >= 2)  # proper grouping

# Test 5: Complex nested AND + OR with NULL IN
q = QueryBuilder("t").where(and_(
    eq("active", True),
    or_(
        in_("category", ["a", None]),
        not_in("tag", ["x", None])
    )
))
sql, params = q.build()
check("complex_nested", "IS NULL" in sql and "IS NOT NULL" in sql)
check("complex_params_no_none", None not in params)

# Test 6: IN with only NULL
q = QueryBuilder("t").where(in_("col", [None]))
sql, params = q.build()
check("in_only_null", "IS NULL" in sql)
check("in_only_null_no_in", "IN ()" not in sql)

# Test 7: NOT IN with only NULL
q = QueryBuilder("t").where(not_in("col", [None]))
sql, params = q.build()
check("not_in_only_null", "IS NOT NULL" in sql)

# Test 8: Empty IN
q = QueryBuilder("t").where(in_("col", []))
sql, params = q.build()
check("empty_in", "1=0" in sql or "FALSE" in sql.upper() or "IN ()" in sql)

# Test 9: Basic query still works
q = QueryBuilder("users").select("id", "name").where(eq("active", True)).order_by("name").limit(10)
sql, params = q.build()
check("basic_query", "SELECT id, name FROM users" in sql)
check("basic_where", "WHERE active = ?" in sql)
check("basic_params", params == [True])

# Test 10: Join + group by still works
q = QueryBuilder("orders").join("users", "orders.user_id = users.id").group_by("user_id").select("user_id", "COUNT(*)")
sql, params = q.build()
check("join_works", "INNER JOIN users" in sql)

print(f"Pass rate: {passed}/{total}")
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        tf = f.name
    try:
        result = subprocess.run([sys.executable, tf], capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print(result.stderr[:500], file=sys.stderr)
    finally:
        os.unlink(tf)

if __name__ == "__main__":
    main()
