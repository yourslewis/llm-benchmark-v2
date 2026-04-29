#!/usr/bin/env python3
"""Tests for code-h2: graph optimization. 47 unit + 3 perf tests."""
import sys, subprocess, tempfile, os, time

def main():
    if len(sys.argv) < 2:
        print("Usage: test.py <solution.py>")
        sys.exit(1)

    solution_path = sys.argv[1]
    with open(solution_path) as f:
        code = f.read()

    test_code = code + '''

import time, random

def _make_graph(edges):
    g = WeightedGraph()
    for s, d, w in edges:
        g.add_edge(s, d, w)
    return g

passed = 0
total = 0

def check(name, condition):
    global passed, total
    total += 1
    if condition:
        passed += 1
    else:
        print(f"  FAIL: {name}")

# Basic tests
g = _make_graph([(0,1,1),(1,2,2),(0,2,10)])
d, p = shortest_path(g, 0, 2)
check("sp_basic_dist", d == 3.0)
check("sp_basic_path", p == [0, 1, 2])

d, p = shortest_path(g, 2, 0)
check("sp_unreachable", d is None and p == [])

d, p = shortest_path(g, 0, 0)
check("sp_self", d == 0.0 and p == [0])

check("sp_missing_src", shortest_path(g, 99, 0) == (None, []))
check("sp_missing_dst", shortest_path(g, 0, 99) == (None, []))

# Larger graph
g2 = _make_graph([(i, i+1, 1) for i in range(10)])
d, p = shortest_path(g2, 0, 10)
check("sp_chain", d == 10.0 and len(p) == 11)

# Diamond
g3 = _make_graph([(0,1,1),(0,2,5),(1,3,1),(2,3,1)])
d, p = shortest_path(g3, 0, 3)
check("sp_diamond", d == 2.0)
check("sp_diamond_path", p == [0, 1, 3])

# all_shortest_paths
asp = all_shortest_paths(g, 0)
check("asp_has_0", 0 in asp)
check("asp_has_1", 1 in asp and asp[1][0] == 1.0)
check("asp_has_2", 2 in asp and asp[2][0] == 3.0)
check("asp_count", len(asp) >= 3)

# k_nearest
kn = k_nearest(g, 0, 1)
check("kn_1", len(kn) == 1 and kn[0][0] == 1)
kn2 = k_nearest(g, 0, 5)
check("kn_all", len(kn2) == 2)  # only 2 reachable
check("kn_sorted", all(kn2[i][1] <= kn2[i+1][1] for i in range(len(kn2)-1)))

# is_reachable
check("reach_yes", is_reachable(g, 0, 2))
check("reach_no", not is_reachable(g, 2, 0))
check("reach_self", is_reachable(g, 0, 0))

# connected_components
g4 = WeightedGraph()
g4.add_edge(0, 1, 1)
g4.add_edge(1, 0, 1)
g4.add_edge(2, 3, 1)
g4.add_edge(3, 2, 1)
g4.add_node(4)
cc = connected_components(g4)
check("cc_count", len(cc) == 3)
check("cc_contains_01", any({0,1} <= c for c in cc))
check("cc_contains_23", any({2,3} <= c for c in cc))
check("cc_contains_4", any(4 in c for c in cc))

# Single node
g5 = WeightedGraph()
g5.add_node(0)
check("single_sp", shortest_path(g5, 0, 0) == (0.0, [0]))
check("single_asp", 0 in all_shortest_paths(g5, 0))
check("single_cc", len(connected_components(g5)) == 1)

# Negative-free weighted
g6 = _make_graph([(0,1,0.5),(1,2,0.3),(0,2,1.0)])
d, p = shortest_path(g6, 0, 2)
check("float_dist", abs(d - 0.8) < 1e-9)

# Multiple paths same cost
g7 = _make_graph([(0,1,1),(0,2,1),(1,3,1),(2,3,1)])
d, p = shortest_path(g7, 0, 3)
check("multi_path_dist", d == 2.0)
check("multi_path_valid", len(p) == 3 and p[0] == 0 and p[-1] == 3)

# Star graph
g8 = WeightedGraph()
for i in range(1, 20):
    g8.add_edge(0, i, float(i))
kn = k_nearest(g8, 0, 5)
check("star_kn", len(kn) == 5)
check("star_kn_order", kn[0][1] < kn[4][1])

# Edge cases
g9 = WeightedGraph()
check("empty_sp", shortest_path(g9, 0, 1) == (None, []))
check("empty_cc", connected_components(g9) == [])

# Cycle
g10 = _make_graph([(0,1,1),(1,2,1),(2,0,1)])
check("cycle_sp", shortest_path(g10, 0, 2)[0] == 2.0)
cc10 = connected_components(g10)
check("cycle_cc", len(cc10) == 1 and len(cc10[0]) == 3)

# API preservation
check("api_WeightedGraph", hasattr(WeightedGraph, "add_node"))
check("api_add_edge", hasattr(WeightedGraph, "add_edge"))
check("api_nodes", hasattr(WeightedGraph, "nodes"))
check("api_neighbors", hasattr(WeightedGraph, "neighbors"))
check("api_edge_count", hasattr(WeightedGraph, "edge_count"))
check("api_node_data_method", hasattr(WeightedGraph, "node_data"))
check("api_Edge", "Edge" in dir())

# Performance tests (10K nodes)
def perf_test(name, timeout=0.5):
    global passed, total
    total += 1
    random.seed(42)
    N = 10000
    g = WeightedGraph()
    for i in range(N):
        g.add_node(i)
    for i in range(N - 1):
        g.add_edge(i, i + 1, random.uniform(0.1, 10))
    # Add random cross-edges
    for _ in range(N * 2):
        a, b = random.randint(0, N-1), random.randint(0, N-1)
        if a != b:
            g.add_edge(a, b, random.uniform(0.1, 10))

    start = time.time()
    if name == "perf_sp":
        shortest_path(g, 0, N - 1)
    elif name == "perf_asp":
        all_shortest_paths(g, 0)
    elif name == "perf_kn":
        k_nearest(g, 0, 10)
    elapsed = time.time() - start
    if elapsed < timeout:
        passed += 1
    else:
        print(f"  FAIL: {name} took {elapsed:.2f}s (limit {timeout}s)")

perf_test("perf_sp")
perf_test("perf_asp", timeout=2.0)
perf_test("perf_kn")

print(f"Pass rate: {passed}/{total}")
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        tf = f.name

    try:
        result = subprocess.run([sys.executable, tf], capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print(result.stderr[:500], file=sys.stderr)
    finally:
        os.unlink(tf)

if __name__ == "__main__":
    main()
