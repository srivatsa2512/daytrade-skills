---
name: dt-setup-check
description: Checks a proposed trade against the user's own written rules before entry. Use when the user describes a trade idea and asks "is this a good setup", "does this fit my rules", or "should I take this".
---

# dt-setup-check

Not financial advice. The judge is the user's rule book, not Claude's opinion on the market.

## Inputs
Read `~/.claude/daytrade/rules.md`. If missing or empty, ask the user to write down their setups and limits first (offer `templates/rules.md`). Without rules this skill cannot give a verdict; say so.
Get from the user: symbol, side, setup name, entry, stop, target, time of day, trades taken so far today, P&L so far today. Ask for anything missing. Never guess.

## Checklist (answer PASS / FAIL / UNKNOWN for each)
- Is it one of the setups the rules allow, and is the trigger actually met?
- Within allowed trading hours?
- Stop placed where the rules say, and risk within max risk %? (use dt-risk math)
- Reward:risk at or above the minimum?
- Under max trades and max daily loss for today?
- Any "never do" item triggered (revenge trade after a loss, adding to a loser, chasing)?
- Emotional state: ask once, plainly, if the last trade was a loss.

## Output
A short table of PASS/FAIL/UNKNOWN, then one line: **"Rules say: take / skip / not enough info."** Any FAIL means skip. Do not argue the user out of their own rules or into them.
End with: what's the user's decision?
