---
name: dt-premarket
description: Builds a one-page pre-market plan from the user's watchlist, key levels and catalysts. Use for "plan my day", "pre-market prep", "what am I watching today", or when the user pastes a watchlist before the open.
---

# dt-premarket

Not financial advice. This skill organizes the user's own ideas. It does not pick stocks or predict direction.

## Inputs
Read `~/.claude/daytrade/rules.md` if it exists (setups allowed, max trades, max daily loss, trading hours).
Ask the user for, per symbol: key levels (prior high/low, premarket high/low), the catalyst if any, and which of THEIR setups it could fit. Do not invent levels or prices. If the user wants news or earnings checked and web search is available, search, cite the source and date, and label it as unverified context.

## Output: one page
1. **Day limits:** max trades, max daily loss in dollars, stop time (from rules)
2. **Watchlist table:** symbol | catalyst | levels | setup it could fit | trigger in plain words | invalidation
3. **If-then lines:** "If X breaks Y with volume, my rule says Z. If not, skip."
4. **Do-not-trade list:** anything failing the user's rules (no catalyst, wrong hours, too wide a stop)
5. **Event risk:** scheduled reports (CPI, FOMC, earnings) the user mentioned or that a search confirmed

Never write "buy" or "sell". Write what the user's rules say.
End with: anything to cut from this plan, or add?
