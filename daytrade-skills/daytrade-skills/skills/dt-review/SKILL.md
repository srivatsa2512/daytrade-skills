---
name: dt-review
description: Reviews a trade log for behavior patterns: overtrading, revenge trades, moved stops, cutting winners early, trading outside the rules. Use for "review my week", "what am I doing wrong", "find my mistakes".
---

# dt-review

Not financial advice. This is a process review, not a market view.

## Input
A trade log (see dt-journal format; `note` and `setup` columns help a lot) plus `~/.claude/daytrade/rules.md` if it exists. Ask for the user's notes if the log has none.

## Look for, citing the exact rows
- **Overtrading:** days over the max-trades rule; clusters of trades minutes apart after a loss
- **Revenge trades:** a larger size or an off-plan setup right after a loss
- **Stop discipline:** actual loss bigger than planned risk (1R); notes like "moved stop"
- **Early exits:** winners closed well under planned target while losers run to full stop
- **Rule breaks:** trades outside allowed setups or hours
- **Best vs worst conditions:** which setup/weekday/time actually made or lost money (only if sample is large enough; say when it is not)

## Output
Top 3 findings, each with: what the data shows (rows or numbers), what rule it touches, and one concrete rule change the user could test for the next 20 trades. Be direct and kind. Describe behavior, never character.
Do not claim causes the data cannot show. If it only suggests a pattern, say "suggests".
If the user describes distress or money they cannot afford to lose, gently pause the numbers and say stepping back from trading is a reasonable option.
End with: which one rule change do you want to test?
