---
name: dt-simulate
description: Random-walk simulations of one trade, historical replay of one rule on real past intraday bars, and equity-curve stress tests from past R-multiples. Use for "how often does this hit target before stop", "simulate my trade", "what's the worst drawdown I should expect", "risk of ruin".
---

# dt-simulate

Not financial advice. Simulations show ranges of outcomes under stated assumptions. They do NOT predict what a stock will do.

## Three modes (`montecarlo.py`, next to this SKILL.md)
**paths** - one trade, random-walk replays:
`python3 montecarlo.py paths --entry E --stop S --target T --vol-pct V --bars N --runs 10000`
`V` = typical one-bar move in percent (ask the user, or compute from price data they supply; never invent it).

**equity** - bootstrap the user's own R-multiples (one per line in a file, from dt-journal) into many possible equity curves:
`python3 montecarlo.py equity --r-file r.txt --trades 100 --risk-pct 1 --runs 5000`
Needs at least 10 past trades; prefer 30+.

**replay** - test ONE rule on every day in the user's own CSV of real past intraday bars (this is the closest thing to a "time machine"):
`python3 montecarlo.py replay --bars-file bars.csv --side long --stop-pct 0.8 --target-pct 2 --entry-time 09:35 [--cost-r 0.05] [--detail] [--save-r r.txt]`
CSV columns: `datetime,open,high,low,close` (e.g. `2026-10-05 09:35,100.2,100.5,99.9,100.1`). The user gets this from their broker or charting platform export. Claude cannot fetch price data itself here; never make bars up. `templates/bars.synthetic-example.csv` is made-up data for testing only: say so if you run it.
`--save-r` writes each day's result in R so the **equity** mode can stress-test it.

## Output
Report results in plain words with the assumptions printed by the tool. Always include:
- paths: zero drift, constant volatility, no gaps, no slippage, no fees. Real markets have all of these.
- replay: one fixed rule on past days, stop counted first when stop and target share a bar, no fees unless `--cost-r` is set. Past days are not future days.
- replay: under 30 days is too noisy to act on; say so every time. Warn against tuning stop/target until the numbers look best on the same days (curve-fitting); suggest testing on days the rule was NOT tuned on.
- equity: assumes future trades resemble past ones and are independent. Edge can vanish.
Never say "there is an X% chance this trade works." Say "in this model, target came first in X% of runs."
If the result looks unfavorable (e.g. target first well under what the R:R needs to break even), say so. Do not soften it.
End with: change an assumption and re-run?
