#!/usr/bin/env bash
# Benchmark v4 full pipeline: run → judge → report
set -uo pipefail
export PYTHONUNBUFFERED=1
cd ~/.openclaw/workspace-chloe/benchmark

echo "=== Benchmark v4 starting at $(date -u) ==="

# Phase 1: Contender Run
echo "--- Phase 1: Contender Run ---"
python3 run.py 2>&1

# Phase 2: Judge Run
echo "--- Phase 2: Judge Run ---"
python3 judge.py 2>&1

# Phase 3: Report
echo "--- Phase 3: Report Generation ---"
python3 report.py 2>&1

RESULTS_DIR=$(ls -d results/v4-* 2>/dev/null | sort | tail -1)
echo "=== Benchmark v4 COMPLETE at $(date -u) ==="
echo "Results: $RESULTS_DIR"
