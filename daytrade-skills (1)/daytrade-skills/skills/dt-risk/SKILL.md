---
name: dt-risk
description: Position sizing for a day trade. Use when the user gives an entry and stop (and optionally target, account size, risk %) and wants share count, dollar risk, or reward:risk. Triggers: "how many shares", "size this trade", "position size", "risk per trade", "R:R".
---

# dt-risk

Not financial advice. This skill does arithmetic on numbers the user supplies.

## Inputs
Read `~/.claude/daytrade/rules.md` if it exists for account size and max risk %. Otherwise ask for: account size, risk % per trade, entry, stop. Target and round-trip fees are optional.
**Never guess a missing number.** Ask.

## Run
If a shell is available: `python3 risk.py --account A --risk-pct P --entry E --stop S [--target T] [--fees F]` (file sits next to this SKILL.md).
If not, do the math by hand and show it:
1. risk $ = account x risk% 
2. risk per share = |entry - stop|
3. shares = floor(risk $ / risk per share)
4. reward:risk = |target - entry| / risk per share

## Output (keep it short)
- Shares, position value, dollars at risk, R:R
- Any warning: position bigger than account (leverage), R:R under 1, zero shares
- If the user's own rules set a minimum R:R or max risk and this trade breaks it, say so plainly

End with one question: take it at this size, change the stop, or skip?
