"""The test that should fail the build if tenant filtering breaks.

    python3 -m unittest -v"""
import csv, unittest
from search import load, search

DOCS = load()
QS = list(csv.DictReader(open("questions.csv", encoding="utf-8")))


class TenantIsolation(unittest.TestCase):
    def test_no_result_from_another_tenant(self):
        for tenant in ("acme", "bayside"):
            for q in QS:  # every question, asked as every tenant
                for d in search(DOCS, q["question"], tenant=tenant, k=10):
                    self.assertIn(d["tenant"], (tenant, "shared"), f"{tenant} saw {d['id']}")

    def test_tenant_is_required(self):
        with self.assertRaises(TypeError):
            search(DOCS, "seal kit discount")  # forgot tenant=
        with self.assertRaises(ValueError):
            search(DOCS, "seal kit discount", tenant="")


if __name__ == "__main__":
    unittest.main()
