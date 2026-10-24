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


if __name__ == "__main__":
    unittest.main()
