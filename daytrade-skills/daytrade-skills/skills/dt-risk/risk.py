#!/usr/bin/env python3
"""Position sizing for one trade. Stdlib only.

Example:
  python3 risk.py --account 10000 --risk-pct 1 --entry 50 --stop 49.2 --target 52
"""
import argparse, json, math, sys


def size_trade(account, risk_pct, entry, stop, target=None, fees=0.0):
    if account <= 0 or risk_pct <= 0:
        raise ValueError("account and risk_pct must be positive")
    if entry <= 0 or stop <= 0:
        raise ValueError("entry and stop must be positive")
    if entry == stop:
        raise ValueError("entry and stop cannot be equal")
    side = "long" if stop < entry else "short"
    if target is not None:
        if side == "long" and target <= entry:
            raise ValueError("long target must be above entry")
        if side == "short" and target >= entry:
            raise ValueError("short target must be below entry")
    risk_dollars = account * risk_pct / 100.0
    per_share = abs(entry - stop)
    shares = math.floor(max(risk_dollars - fees, 0) / per_share)
    out = {
        "side": side,
        "risk_budget": round(risk_dollars, 2),
        "risk_per_share": round(per_share, 4),
        "shares": shares,
        "position_value": round(shares * entry, 2),
        "actual_risk": round(shares * per_share + fees, 2),
        "warnings": [],
    }
    if shares == 0:
        out["warnings"].append("Risk budget is smaller than the risk of one share. Skip or widen budget.")
    if shares * entry > account:
        out["warnings"].append("Position value exceeds account size: this needs margin/leverage.")
    if target is not None:
        reward = abs(target - entry)
        out["reward_per_share"] = round(reward, 4)
        out["reward_risk"] = round(reward / per_share, 2)
        out["potential_profit"] = round(shares * reward - fees, 2)
        if out["reward_risk"] < 1:
            out["warnings"].append("Reward:risk below 1:1.")
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--account", type=float, required=True)
    p.add_argument("--risk-pct", type=float, required=True)
    p.add_argument("--entry", type=float, required=True)
    p.add_argument("--stop", type=float, required=True)
    p.add_argument("--target", type=float)
    p.add_argument("--fees", type=float, default=0.0, help="round-trip fees in dollars")
    a = p.parse_args(argv)
    try:
        print(json.dumps(size_trade(a.account, a.risk_pct, a.entry, a.stop, a.target, a.fees), indent=2))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
