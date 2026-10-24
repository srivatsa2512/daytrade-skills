#!/usr/bin/env python3
"""Trade-log CSV to stats. Stdlib only.

Columns: date,symbol,side,entry,exit,shares  (optional: stop,fees,setup,note)
  python3 journal.py trades.csv
"""
import csv, json, sys
from collections import defaultdict
from datetime import datetime

REQUIRED = ["date", "symbol", "side", "entry", "exit", "shares"]


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("no rows found")
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        raise ValueError("missing columns: " + ", ".join(missing))
    return rows


def trade_result(r):
    side = r["side"].strip().lower()
    if side not in ("long", "short"):
        raise ValueError(f"side must be long or short, got {side!r}")
    entry, exit_, shares = float(r["entry"]), float(r["exit"]), float(r["shares"])
    fees = float(r.get("fees") or 0)
    direction = 1 if side == "long" else -1
    pnl = direction * (exit_ - entry) * shares - fees
    rmult = None
    stop = (r.get("stop") or "").strip()
    if stop:
        risk = abs(entry - float(stop)) * shares
        if risk > 0:
            rmult = pnl / risk
    return pnl, rmult


def analyze(rows):
    res = []
    for r in rows:
        pnl, rm = trade_result(r)
        res.append({"row": r, "pnl": pnl, "r": rm})
    pnls = [x["pnl"] for x in res]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    n = len(pnls)
    equity, peak, max_dd = 0.0, 0.0, 0.0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    out = {
        "trades": n,
        "net_pnl": round(sum(pnls), 2),
        "win_rate_pct": round(100 * len(wins) / n, 1),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0.0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0.0,
        "expectancy_per_trade": round(sum(pnls) / n, 2),
        "profit_factor": round(sum(wins) / -sum(losses), 2) if losses else None,
        "max_drawdown": round(max_dd, 2),
        "best_trade": round(max(pnls), 2),
        "worst_trade": round(min(pnls), 2),
    }
    rs = [x["r"] for x in res if x["r"] is not None]
    if rs:
        out["trades_with_stop"] = len(rs)
        out["avg_r"] = round(sum(rs) / len(rs), 2)
    by_setup = defaultdict(list)
    for x in res:
        by_setup[(x["row"].get("setup") or "unlabeled").strip() or "unlabeled"].append(x["pnl"])
    out["by_setup"] = {k: {"trades": len(v), "net": round(sum(v), 2)} for k, v in by_setup.items()}
    by_day = defaultdict(float)
    for x in res:
        try:
            d = datetime.strptime(x["row"]["date"].strip(), "%Y-%m-%d").strftime("%a")
        except ValueError:
            d = "?"
        by_day[d] += x["pnl"]
    out["by_weekday_net"] = {k: round(v, 2) for k, v in by_day.items()}
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 1
    try:
        print(json.dumps(analyze(load(argv[0])), indent=2))
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
