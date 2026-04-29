#!/usr/bin/env bash
# Watch benchmark v4 and notify when done
cd ~/.openclaw/workspace-chloe/benchmark
PID=$(cat v4.pid 2>/dev/null)

while kill -0 "$PID" 2>/dev/null; do
    sleep 300  # check every 5 min
done

echo "Benchmark v4 finished at $(date). Generating notification..."

# Find results dir
RESULTS_DIR=$(ls -d results/v4-* 2>/dev/null | sort | tail -1)

# Count results
if [ -d "$RESULTS_DIR/raw" ]; then
    TOTAL=$(find "$RESULTS_DIR/raw" -name "*.json" | wc -l | tr -d ' ')
    ERRORS=$(find "$RESULTS_DIR/raw" -name "*.json" -exec grep -l '"status": "error"' {} \; | wc -l | tr -d ' ')
    SCORES=$(python3 -c "import json; d=json.load(open('$RESULTS_DIR/scores.json')); print(len(d))" 2>/dev/null || echo "0")
else
    TOTAL=0; ERRORS=0; SCORES=0
fi

# Generate summary from report.txt if exists
SUMMARY=""
if [ -f "$RESULTS_DIR/report.txt" ]; then
    SUMMARY=$(head -30 "$RESULTS_DIR/report.txt")
fi

echo "Results: $TOTAL calls, $ERRORS errors, $SCORES scores"
echo "Dir: $RESULTS_DIR"
