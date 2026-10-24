# daytrade-skills

Six free Claude skills for day traders. MIT, no signup, no API key, nothing to connect.

**These skills plan, calculate and review. You place the trades.** Nothing here predicts the market, executes orders or promises returns. Day trading loses money for most people. **Not financial advice.**

## Install

Paste this repo link into Claude and say "install skills". Or, in Claude Code:

```bash
git clone https://github.com/srivatsa2512/daytrade-skills.git
cp -r daytrade-skills/skills/dt-* ~/.claude/skills/
```

Project-local: copy the same folders into your repo's `.claude/skills/`.
No Claude Code? Paste any single `SKILL.md` at the top of a chat and it runs as a mode (you lose the Python tools; Claude does the math by hand).

Then copy `templates/rules.md` to `~/.claude/daytrade/rules.md` and fill it in. Every skill reads it.

## The six

| skill | what it does |
|---|---|
| `dt-premarket` | turns your watchlist, levels and catalysts into a one-page plan for the day |
| `dt-risk` | position size, stop distance, R:R, with the math shown (`risk.py`) |
| `dt-setup-check` | tests a trade idea against YOUR rules before you enter |
| `dt-journal` | trade-log CSV into win rate, average R, expectancy, drawdown (`journal.py`) |
| `dt-review` | finds behavior patterns in your log: overtrading, revenge trades, moved stops |
| `dt-simulate` | random-walk replays of one trade, plus equity-curve stress tests (`montecarlo.py`) |

## Rules every skill follows

- Never invents a number. If a price, volume or figure is missing, it asks you.
- Never says "buy" or "sell". It says what your own rules say.
- Ends with a question: take it, change it, or skip it?
- Simulations are ranges of outcomes under stated assumptions, not predictions.

## Files

```
skills/dt-*/SKILL.md     the instructions
skills/dt-risk/risk.py   position sizing (stdlib only)
skills/dt-journal/journal.py
skills/dt-simulate/montecarlo.py
templates/rules.md       your rules, filled in once
templates/journal.example.csv
tests/                   python3 -m unittest discover tests
```

## Not built here, on purpose

Live scanning of thousands of charts, background price alerts and order execution need a market-data feed and a brokerage connection. They are out of scope. If you add them, start in paper trading.

## Licence

MIT. Use it, change it, ship it.
