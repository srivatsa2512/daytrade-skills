---
name: dt-simulate
description: Random-walk replays of a single trade and equity-curve stress tests from the user's past R-multiples. Use for "how often does this hit target before stop", "simulate my trade", "what's the worst drawdown I should expect", "risk of ruin".
---

# dt-simulate

Not financial advice. Simulations show ranges of outcomes under stated assumptions. They do NOT predict what a stock will do.

## Two modes (`montecarlo.py`, next to this SKILL.md)
**paths** - one trade, random-walk replays:
`python3 montecarlo.py paths --entry E --stop S --target T --vol-pct V --bars N --runs 10000`
`V` = typical one-bar move in percent (ask the user, or compute from price data they supply; never invent it).

**equity** - bootstrap the user's own R-multiples (one per line in a file, from dt-journal) into many possible equity curves:
`python3 montecarlo.py equity --r-file r.txt --trades 100 --risk-pct 1 --runs 5000`
Needs at least 10 past trades; prefer 30+.

## Output
Report results in plain words with the assumptions printed by the tool. Always include:
- paths: zero drift, constant volatility, no gaps, no slippage, no fees. Real markets have all of these.
- equity: assumes future trades resemble past ones and are independent. Edge can vanish.
Never say "there is an X% chance this trade works." Say "in this model, target came first in X% of runs."
If the result looks unfavorable (e.g. target first well under what the R:R needs to break even), say so. Do not soften it.
End with: change an assumption and re-run?
