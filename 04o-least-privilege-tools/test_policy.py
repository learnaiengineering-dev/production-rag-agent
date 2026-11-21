"""python3 -m unittest -v test_policy"""
import json, unittest
from policy import decide, inside

CTX = {"customer": "alice@customer.example"}
CALLS = [json.loads(line) for line in open("calls.jsonl")]
STRICT = "allowlist + scoped arguments"


class LeastPrivilege(unittest.TestCase):
    def test_every_job_call_still_runs(self):
        for c in CALLS:
            if c["source"] == "task":
                self.assertEqual(decide(STRICT, c["agent"], c["tool"], c["args"], CTX), "run", c)

    def test_no_injected_call_runs(self):
        for c in CALLS:
            if c["source"] == "injected":
                self.assertNotEqual(decide(STRICT, c["agent"], c["tool"], c["args"], CTX), "run", c)

    def test_paths_cannot_climb_out(self):
        self.assertTrue(inside("reports/q3.csv", "reports"))
        self.assertTrue(inside("reports/./out/a.md", "reports/out"))
        self.assertFalse(inside("reports/../config/api-keys.txt", "reports"))
        self.assertFalse(inside("reports-old/q3.csv", "reports"))
        self.assertFalse(inside("../reports/q3.csv", "reports"))

    def test_sql_is_read_only(self):
        for q in ["UPDATE orders SET total = 0", "SELECT 1; DROP TABLE orders", "delete from orders"]:
            self.assertEqual(decide(STRICT, "refunds", "run_sql", {"query": q}, CTX), "read-only", q)

    def test_big_refund_waits_for_a_person(self):
        self.assertEqual(decide(STRICT, "refunds", "create_refund", {"order": 1, "amount": 51}, CTX), "hold")
        self.assertEqual(decide(STRICT, "refunds", "create_refund", {"order": 1, "amount": 50}, CTX), "run")


if __name__ == "__main__":
    unittest.main()
