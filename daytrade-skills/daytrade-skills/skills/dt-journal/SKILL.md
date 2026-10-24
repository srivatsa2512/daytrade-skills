---
name: dt-journal
description: Turns a trade-log CSV into stats: win rate, average R, expectancy, profit factor, drawdown, results by setup and weekday. Use when the user uploads or pastes trades, or asks "how am I doing", "my stats", "analyze my trades".
---

# dt-journal

Not financial advice. Descriptive statistics on the user's own past trades.

## Input
CSV with columns: `date,symbol,side,entry,exit,shares` and optionally `stop,fees,setup,note`. See `templates/journal.example.csv`. `side` is long or short; `date` is YYYY-MM-DD.
If the user pastes trades in another format, convert to this CSV and show it before running.

## Run
`python3 journal.py trades.csv` (file sits next to this SKILL.md). Without a shell, compute by hand from the definitions:
- P&L = direction x (exit - entry) x shares - fees
- R = P&L / (|entry - stop| x shares)
- expectancy = average P&L per trade; profit factor = gross wins / gross losses
- max drawdown = largest peak-to-trough fall in cumulative P&L

## Output
Lead with the 4 numbers that matter: win rate, avg win vs avg loss, expectancy, max drawdown. Then by-setup and by-weekday only if there is enough data.
**Sample size rule:** under 30 trades, say the stats are too noisy to act on. Under 100, say conclusions are tentative. Never present a small-sample edge as proven.
End with: want a behavior review (dt-review) or a stress test (dt-simulate)?
