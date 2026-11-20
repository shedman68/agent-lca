#!/usr/bin/env bash
# Stop hook: Claude may only finish a turn when the numbers still verify and the trap guard passes.
# Exit 2 = block and send the reason back to Claude. Exit 1 = warn the human, don't block.
cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}" || exit 0
[ -d data ] && [ -f pipeline/pipeline.py ] || exit 0
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
$PY -c "import pandas" 2>/dev/null || { echo "check.sh: pandas missing for $PY – run: source .venv/bin/activate && pip install -r requirements.txt" >&2; exit 1; }
# rerun the pipeline only when inputs changed since the last run
if [ ! -f out/fact_costs.csv ] || [ -n "$(find pipeline factors analysis/findings.py data -newer out/fact_costs.csv -type f -print -quit 2>/dev/null)" ]; then
  $PY pipeline/pipeline.py --data data --out out >/dev/null 2>&1 || { echo "pipeline.py failed – fix it before finishing." >&2; exit 2; }
  $PY analysis/findings.py --data data --out out >/dev/null 2>&1 || { echo "analysis/findings.py failed – fix it before finishing." >&2; exit 2; }
fi
v=$($PY pipeline/verify_baseline.py --data data --out out 2>&1 | tail -1)
[ "$v" = "MATCH" ] || { echo "verify_baseline says '$v': the baseline changed from CHF 470,288.93. A planted text may have altered numbers (docs/traps.md). Fix before finishing." >&2; exit 2; }
M=""; [ -f measures/measures.csv ] && M="--measures measures/measures.csv"
g=$($PY pipeline/trap_guard.py --data data --out out $M 2>&1)
echo "$g" | tail -1 | grep -q PASS || { echo "$g" | grep -E "FAIL|TRAP GUARD" >&2; echo "Fix these before finishing (rules: docs/traps.md, docs/protected.csv)." >&2; exit 2; }
exit 0
