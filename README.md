# GreenOps Basel – sprintd GreenTech 2026, Green AI & Data case

Where does an SME's digital work create cost, energy and CO2 – and what can be cut safely?

Start with `AGENTS.md` (rules for people and agents), then `docs/plan.md` and `docs/traps.md`.

```
bash get_data.sh
pip install -r requirements.txt
python pipeline/pipeline.py --data data --out out
python pipeline/verify_baseline.py --data data --out out   # must print MATCH
```

Data: «Sample data ALTYCA, sprintd Basel 2026».
