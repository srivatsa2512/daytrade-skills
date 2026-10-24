#!/usr/bin/env python3
"""Simulations. Stdlib only. Ranges under stated assumptions, NOT predictions.

paths:  replay one trade as a random walk; how often does target hit before stop?
  python3 montecarlo.py paths --entry 50 --stop 49.2 --target 52 --vol-pct 0.15 --bars 390 --runs 10000

equity: bootstrap your own past R-multiples into possible equity curves.
  python3 montecarlo.py equity --r-file r.txt --trades 100 --risk-pct 1 --runs 5000
  (r.txt: one R-multiple per line, e.g. 1.5 / -1 / 0.8)

replay: test ONE rule on every day in a CSV of real past intraday bars.
  python3 montecarlo.py replay --bars-file bars.csv --side long --stop-pct 0.8 --target-pct 2 --entry-time 09:35
  (bars.csv columns: datetime,open,high,low,close  e.g. 2026-10-05 09:35,100.2,100.5,99.9,100.1)
  Add --save-r r.txt to feed the results into the equity mode.
"""
import argparse, csv, json, math, random, sys
from collections import OrderedDict


def simulate_paths(entry, stop, target, vol_pct, bars, runs, seed=None):
    """vol_pct = std dev of ONE bar's return in percent. Zero drift."""
    rng = random.Random(seed)
    long_ = stop < entry
    hit_t = hit_s = timeout = 0
    sigma = vol_pct / 100.0
    for _ in range(runs):
        price = entry
        outcome = None
        for _ in range(bars):
            price *= math.exp(rng.gauss(-0.5 * sigma * sigma, sigma))
            up_t = price >= target if long_ else price <= target
            dn_s = price <= stop if long_ else price >= stop
            if dn_s:  # if both could hit in one bar, count the stop (conservative)
                outcome = "stop"
                break
            if up_t:
                outcome = "target"
                break
        if outcome == "target":
            hit_t += 1
        elif outcome == "stop":
            hit_s += 1
        else:
            timeout += 1
    return {
        "runs": runs,
        "target_first_pct": round(100 * hit_t / runs, 1),
        "stop_first_pct": round(100 * hit_s / runs, 1),
        "neither_by_end_pct": round(100 * timeout / runs, 1),
        "assumptions": "zero-drift random walk, constant volatility, no gaps, no slippage, no fees",
    }


def simulate_equity(r_list, trades, risk_pct, runs, ruin_dd_pct=30.0, seed=None):
    if len(r_list) < 10:
        raise ValueError("need at least 10 past R-multiples")
    rng = random.Random(seed)
    finals, dds, ruined = [], [], 0
    for _ in range(runs):
        eq, peak, max_dd, hit = 1.0, 1.0, 0.0, False
        for _ in range(trades):
            eq *= 1 + risk_pct / 100.0 * rng.choice(r_list)
            peak = max(peak, eq)
            dd = (peak - eq) / peak
            max_dd = max(max_dd, dd)
            if dd * 100 >= ruin_dd_pct:
                hit = True
        finals.append(eq)
        dds.append(max_dd)
        ruined += hit
    finals.sort()
    dds.sort()

    def q(a, p):
        return a[min(len(a) - 1, int(p * len(a)))]

    return {
        "runs": runs,
        "trades_per_run": trades,
        "risk_pct_per_trade": risk_pct,
        "final_equity_multiple": {"p5": round(q(finals, .05), 3), "median": round(q(finals, .5), 3), "p95": round(q(finals, .95), 3)},
        "max_drawdown_pct": {"median": round(100 * q(dds, .5), 1), "p95": round(100 * q(dds, .95), 1)},
        f"prob_drawdown_ge_{int(ruin_dd_pct)}pct": round(100 * ruined / runs, 1),
        "assumptions": "trades are independent draws from your past R-multiples; the future may differ",
    }


def load_bars(path):
    """CSV of intraday bars -> {day: [(HH:MM, open, high, low, close), ...]}"""
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames is None:
            raise ValueError("bars file is empty")
        cols = {c.strip().lower(): c for c in rd.fieldnames}
        tcol = next((cols[k] for k in ("datetime", "timestamp", "time") if k in cols), None)
        missing = [k for k in ("open", "high", "low", "close") if k not in cols]
        if tcol is None or missing:
            raise ValueError("need columns datetime,open,high,low,close (missing: %s)"
                             % ", ".join(missing + ([] if tcol else ["datetime"])))
        days = OrderedDict()
        for row in rd:
            t = row[tcol].strip().replace("T", " ")
            if len(t) < 16 or t[10] != " ":
                raise ValueError("need intraday timestamps like 2026-10-05 09:35, got %r" % t)
            bar = (t[11:16], float(row[cols["open"]]), float(row[cols["high"]]),
                   float(row[cols["low"]]), float(row[cols["close"]]))
            days.setdefault(t[:10], []).append(bar)
    if not days:
        raise ValueError("no bars found")
    for d in days:
        days[d].sort(key=lambda b: b[0])
    return days


def replay_day(bars, side, stop_pct, target_pct, entry_time):
    """One day. Returns (outcome, R) or None if no bar at/after entry_time."""
    long_ = side == "long"
    idx = next((i for i, b in enumerate(bars) if b[0] >= entry_time), None)
    if idx is None:
        return None
    entry = bars[idx][1]  # enter at the open of that bar
    risk = entry * stop_pct / 100.0
    sgn = 1 if long_ else -1
    stop = entry - sgn * risk
    target = entry * (1 + sgn * target_pct / 100.0)
    target_r = target_pct / stop_pct
    for i in range(idx, len(bars)):
        _, o, h, l, c = bars[i]
        if i > idx:  # gaps at the open of later bars
            if (long_ and o <= stop) or (not long_ and o >= stop):
                return "stop", sgn * (o - entry) / risk  # filled at the worse open price
            if (long_ and o >= target) or (not long_ and o <= target):
                return "target", target_r  # conservative: credit only the target price
        hit_stop = l <= stop if long_ else h >= stop
        hit_tgt = h >= target if long_ else l <= target
        if hit_stop:  # if both fall inside one bar, count the stop
            return "stop", -1.0
        if hit_tgt:
            return "target", target_r
    return "close", sgn * (bars[-1][4] - entry) / risk


def replay(days, side, stop_pct, target_pct, entry_time="09:35", cost_r=0.0, detail=False):
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    if stop_pct <= 0 or target_pct <= 0:
        raise ValueError("stop-pct and target-pct must be positive")
    if len(entry_time) != 5 or entry_time[2] != ":":
        raise ValueError("entry-time must look like 09:35")
    res = []
    for day, bars in days.items():
        r = replay_day(bars, side, stop_pct, target_pct, entry_time)
        if r is not None:
            res.append((day, r[0], r[1] - cost_r))
    n = len(res)
    if n == 0:
        raise ValueError("no day had a bar at or after the entry time")
    rs = [x[2] for x in res]
    cnt = lambda k: sum(1 for x in res if x[1] == k)
    eq = peak = dd = 0.0
    streak = cur = 0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
        cur = cur + 1 if r < 0 else 0
        streak = max(streak, cur)
    warnings = []
    if n < 30:
        warnings.append("Only %d days tested. Under 30 is too noisy to act on." % n)
    elif n < 100:
        warnings.append("%d days tested. Treat any result as tentative." % n)
    out = {
        "days_tested": n,
        "target_first_pct": round(100 * cnt("target") / n, 1),
        "stop_first_pct": round(100 * cnt("stop") / n, 1),
        "closed_at_end_of_day_pct": round(100 * cnt("close") / n, 1),
        "win_rate_pct": round(100 * sum(1 for r in rs if r > 0) / n, 1),
        "avg_r_per_trade": round(sum(rs) / n, 3),
        "best_day_r": round(max(rs), 2),
        "worst_day_r": round(min(rs), 2),
        "max_drawdown_r": round(dd, 2),
        "longest_losing_streak_days": streak,
        "warnings": warnings,
        "assumptions": ("enters at the open of the first bar at/after entry time; stop is checked before "
                        "target inside the same bar; gap through a stop fills at the worse open; target fills "
                        "at the target; no fees or slippage beyond cost-r. One fixed rule on past data: "
                        "this is NOT a forecast, and tuning stop/target to look best on the same days is curve-fitting"),
    }
    if detail:
        out["days"] = [{"day": d, "outcome": o, "r": round(r, 2)} for d, o, r in res]
    out["_r_list"] = rs
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("paths")
    a.add_argument("--entry", type=float, required=True)
    a.add_argument("--stop", type=float, required=True)
    a.add_argument("--target", type=float, required=True)
    a.add_argument("--vol-pct", type=float, required=True)
    a.add_argument("--bars", type=int, default=390)
    a.add_argument("--runs", type=int, default=10000)
    a.add_argument("--seed", type=int)
    b = sub.add_parser("equity")
    b.add_argument("--r-file", required=True)
    b.add_argument("--trades", type=int, default=100)
    b.add_argument("--risk-pct", type=float, required=True)
    b.add_argument("--runs", type=int, default=5000)
    b.add_argument("--ruin-dd-pct", type=float, default=30.0)
    b.add_argument("--seed", type=int)
    c = sub.add_parser("replay")
    c.add_argument("--bars-file", required=True)
    c.add_argument("--side", choices=["long", "short"], required=True)
    c.add_argument("--stop-pct", type=float, required=True, help="stop distance, percent of entry price")
    c.add_argument("--target-pct", type=float, required=True, help="target distance, percent of entry price")
    c.add_argument("--entry-time", default="09:35", help="HH:MM, enter at the open of the first bar at/after this time")
    c.add_argument("--cost-r", type=float, default=0.0, help="fees+slippage per trade, in R")
    c.add_argument("--detail", action="store_true", help="list every day")
    c.add_argument("--save-r", help="write each day's R to this file (for equity mode)")
    args = p.parse_args(argv)
    try:
        if args.cmd == "replay":
            out = replay(load_bars(args.bars_file), args.side, args.stop_pct, args.target_pct,
                         args.entry_time, args.cost_r, args.detail)
            rl = out.pop("_r_list")
            if args.save_r:
                with open(args.save_r, "w") as f:
                    f.write("\n".join("%.4f" % r for r in rl) + "\n")
            print(json.dumps(out, indent=2))
            return 0
        if args.cmd == "paths":
            if not (args.stop < args.entry < args.target or args.target < args.entry < args.stop):
                raise ValueError("need stop < entry < target (long) or target < entry < stop (short)")
            out = simulate_paths(args.entry, args.stop, args.target, args.vol_pct, args.bars, args.runs, args.seed)
        else:
            with open(args.r_file) as f:
                rs = [float(x) for x in f.read().split() if x.strip()]
            out = simulate_equity(rs, args.trades, args.risk_pct, args.runs, args.ruin_dd_pct, args.seed)
        print(json.dumps(out, indent=2))
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
