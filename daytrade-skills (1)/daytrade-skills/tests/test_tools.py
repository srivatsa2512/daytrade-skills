import csv, os, sys, tempfile, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ("dt-risk", "dt-journal", "dt-simulate"):
    sys.path.insert(0, os.path.join(ROOT, "skills", d))
import risk, journal, montecarlo


class TestRisk(unittest.TestCase):
    def test_long_size(self):
        r = risk.size_trade(10000, 1, 50, 49, 52)
        self.assertEqual(r["shares"], 100)
        self.assertEqual(r["reward_risk"], 2.0)
        self.assertEqual(r["actual_risk"], 100.0)

    def test_short_side(self):
        self.assertEqual(risk.size_trade(10000, 1, 50, 51)["side"], "short")

    def test_leverage_warning(self):
        r = risk.size_trade(1000, 5, 100, 99)
        self.assertTrue(any("leverage" in w for w in r["warnings"]))

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            risk.size_trade(1000, 1, 50, 50)
        with self.assertRaises(ValueError):
            risk.size_trade(1000, 1, 50, 49, 48)


class TestJournal(unittest.TestCase):
    def test_example(self):
        rows = journal.load(os.path.join(ROOT, "templates", "journal.example.csv"))
        s = journal.analyze(rows)
        self.assertEqual(s["trades"], 6)
        self.assertEqual(s["net_pnl"], 193.0)
        self.assertEqual(s["win_rate_pct"], 50.0)
        self.assertIn("ORB", s["by_setup"])

    def test_pnl_short(self):
        pnl, r = journal.trade_result({"side": "short", "entry": "10", "exit": "9", "shares": "10", "stop": "11", "fees": "0"})
        self.assertEqual(pnl, 10)
        self.assertAlmostEqual(r, 1.0)


class TestSim(unittest.TestCase):
    def test_paths_sum(self):
        r = montecarlo.simulate_paths(50, 49, 52, 0.1, 100, 500, seed=1)
        total = r["target_first_pct"] + r["stop_first_pct"] + r["neither_by_end_pct"]
        self.assertAlmostEqual(total, 100, delta=0.2)

    def test_equity_needs_data(self):
        with self.assertRaises(ValueError):
            montecarlo.simulate_equity([1, -1], 10, 1, 10)

    def test_equity_runs(self):
        r = montecarlo.simulate_equity([1.5, -1] * 10, 50, 1, 200, seed=2)
        self.assertIn("final_equity_multiple", r)


class TestReplay(unittest.TestCase):
    def days(self):
        return {
            "d1": [("09:35", 100, 100.5, 99.8, 100.2), ("09:40", 100.2, 102.5, 100, 102)],
            "d2": [("09:35", 100, 100.2, 98.5, 99)],
            "d3": [("09:35", 100, 100.5, 99.5, 100.5), ("09:40", 100.5, 101, 100.4, 101)],
        }

    def test_long_outcomes(self):
        r = montecarlo.replay(self.days(), "long", 1, 2)
        self.assertEqual(r["days_tested"], 3)
        self.assertEqual(r["target_first_pct"], 33.3)
        self.assertEqual(r["stop_first_pct"], 33.3)
        self.assertEqual(r["closed_at_end_of_day_pct"], 33.3)
        self.assertAlmostEqual(r["avg_r_per_trade"], 0.667, places=3)

    def test_stop_wins_when_both_in_one_bar(self):
        d = {"d": [("09:35", 100, 103, 98, 101)]}
        self.assertEqual(montecarlo.replay_day(d["d"], "long", 1, 2, "09:35")[0], "stop")

    def test_gap_through_stop_is_worse_than_one_r(self):
        bars = [("09:35", 100, 100.2, 99.9, 100), ("09:40", 97, 97.5, 96.5, 97)]
        outcome, r = montecarlo.replay_day(bars, "long", 1, 2, "09:35")
        self.assertEqual(outcome, "stop")
        self.assertLess(r, -1.0)

    def test_short_side(self):
        bars = [("09:35", 100, 100.2, 97.5, 98)]
        self.assertEqual(montecarlo.replay_day(bars, "short", 1, 2, "09:35")[0], "target")

    def test_cost_and_errors(self):
        r = montecarlo.replay(self.days(), "long", 1, 2, cost_r=0.1)
        self.assertAlmostEqual(r["avg_r_per_trade"], 0.567, places=3)
        with self.assertRaises(ValueError):
            montecarlo.replay(self.days(), "long", 0, 2)
        with self.assertRaises(ValueError):
            montecarlo.replay(self.days(), "long", 1, 2, entry_time="23:59")

    def test_example_file_loads(self):
        days = montecarlo.load_bars(os.path.join(ROOT, "templates", "bars.synthetic-example.csv"))
        self.assertEqual(len(days), 6)
        r = montecarlo.replay(days, "long", 0.4, 0.8)
        total = r["target_first_pct"] + r["stop_first_pct"] + r["closed_at_end_of_day_pct"]
        self.assertAlmostEqual(total, 100, delta=0.3)


if __name__ == "__main__":
    unittest.main()
