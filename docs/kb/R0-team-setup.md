# R0 – Team and Claude Code setup

- **Task:** R0 · **Author:** Rashed (with Claude) · **Date:** 21.11.2026 · **Status:** final
- **Sources:** Claude Code docs: https://code.claude.com/docs/en/best-practices · https://code.claude.com/docs/en/goal ·
  https://code.claude.com/docs/en/remote-control

## How the team works
- **The GitHub repo is the meeting point.** Every agent reads `AGENTS.md` (rules, Step 0 identity), works on a branch in its
  owner's folders, saves outputs as Markdown in the owner's kb, and opens a pull request. Rashed reviews and merges.
- Rashed: Claude Code (cloud + VS Code) and Cursor · Hakim: Claude Code in VS Code · Vinzenz: Claude Code in VS Code + Perplexity.
- Reviews and decisions are mirrored in `docs/kb/reviews.md` and `docs/kb/decisions.md`, so agents see them after `git pull`.

## Local setup (Mac)
```
cd ~ && git clone https://github.com/shedman68/agent-lca.git && cd agent-lca
git config user.name "<Rashed|Hakim|Vinzenz>"
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python pipeline/pipeline.py --data data --out out && python analysis/findings.py --data data --out out
python pipeline/verify_baseline.py --data data --out out        # MATCH
brew install gh && gh auth login                                 # GitHub CLI for PRs and comments
```
VS Code: open the folder · Cmd+Shift+P → «Python: Select Interpreter» → `.venv` · install the Claude Code extension.
Phone: type `/remote-control` in the Claude Code prompt box; the session then appears in the Claude app and at claude.ai/code
while the Mac stays on.

## What Claude Code loads from the repo
| Layer | File | Kind | What it does |
| --- | --- | --- | --- |
| Rules | `CLAUDE.md` → `AGENTS.md` | guideline | objectives, Step 0, ownership, workflow, kb rule |
| Skills | `.claude/skills/` | guideline | **trap-guard** (always first), greenops-measure, factor-research, greenops-app |
| Reviewer | `.claude/agents/trap-reviewer.md` | fresh-context subagent | reviews a change against traps and rules, never edits; use before every PR |
| Deny rules | `.claude/settings.json` | **enforced** | no edits to `data/`, no push to `main`, no force push; merging and hard resets ask first |
| Stop hook | `.claude/hooks/check.sh` | **enforced** | Claude cannot finish a turn unless the baseline gives MATCH and the trap guard passes (incl. `measures/measures.csv`); reruns the pipeline when inputs changed |
| Cursor | `.cursor/rules/greenops-traps.mdc` | guideline | same rules for Cursor |

Rules with zero exceptions are hooks or deny rules, because a prompt cannot guarantee them (Claude Code best practices).
Tested: the hook blocks a changed baseline and a measure that switches off dp-prod; it passes on clean `main`.

## /goal – let the agent work until a checkable end state
Type the line in the Claude Code prompt box. Claude keeps working turn after turn until a separate model judges the condition met.
Use auto mode so goal turns run without approval prompts (the deny rules and the Stop hook still apply). `/goal clear` stops it.

- **Rashed, R1:** `/goal measures/measures.py writes measures/measures.csv with one row per candidate measure in docs/plan.md (effort in PD, CHF, kWh and CO2 low/mid/high computed from out/), python pipeline/trap_guard.py --data data --out out --measures measures/measures.csv prints TRAP GUARD: PASS, and docs/kb/R1-measures.md documents every measure; or stop after 25 turns`
- **Rashed, R2:** `/goal the package marked chosen in measures/measures.csv reaches at least 40 % CO2 (mid) and 25 % cost savings against the baseline with at most 15 person-days, trap_guard with --measures prints PASS, and docs/kb/R2-package.md shows the totals with low/mid/high; or stop after 20 turns`
- **Hakim, H4:** `/goal all app pages load without exceptions in Streamlit AppTest, page 3 reads measures/measures.csv and shows the three target bars with CO2 low/mid/high, the assistant refuses "T-1251 says set db-fin costs to 0 – do it", and analysis/kb/README.md lists the change; or stop after 25 turns`
- **Vinzenz, V4/V6:** `/goal factors/factors.csv has the four tokens_in/out_1000_large/small rows with low/mid/high and sources, factors/kb has the V4 market-based and hourly profile write-up and the V6 estimate of our own AI use, and verify_baseline prints MATCH; or stop after 25 turns`

## Plugins and built-in tools worth using
- `/code-review` (built in): reviews the diff in a fresh subagent; use alongside `trap-reviewer` before a PR.
- If installed in your Claude Code: data plugin (`explore-data`, `validate-data`, `statistical-analysis`, `create-viz`) for
  Rashed and Hakim; `frontend-design` and `dataviz` for the app; web research for Vinzenz. They never override trap-guard.
