#!/usr/bin/env python3
"""Simulations. Stdlib only. Ranges under stated assumptions, NOT predictions.

paths:  replay one trade as a random walk; how often does target hit before stop?
  python3 montecarlo.py paths --entry 50 --stop 49.2 --target 52 --vol-pct 0.15 --bars 390 --runs 10000

equity: bootstrap your own past R-multiples into possible equity curves.
  python3 montecarlo.py equity --r-file r.txt --trades 100 --risk-pct 1 --runs 5000
  (r.txt: one R-multiple per line, e.g. 1.5 / -1 / 0.8)
"""
import argparse, json, math, random, sys


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
    args = p.parse_args(argv)
    try:
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
