"""python3 -m unittest -v test_prompts"""
import os, shutil, tempfile, unittest
from registry import load, read
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import run  # runs the demo once, quietly, then we check its results

class PromptVersions(unittest.TestCase):
    def test_every_version_matches_its_lock(self):
        for v in ("v1", "v2"):
            self.assertEqual(load("support-answer", v)[0], v)

    def test_in_place_edit_is_refused(self):
        tmp = tempfile.mkdtemp()
        try:
            shutil.copytree(".", tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns("logs", "__pycache__"))
            p = os.path.join(tmp, "prompts", "support-answer", "v1.txt")
            text = read(p).replace("one or two", "two or three")
            with open(p, "w") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                load("support-answer", root=tmp)
        finally:
            shutil.rmtree(tmp)

    def test_gate_blocks_v2(self):
        self.assertLess(run.score(run.res["v2"])[0], run.score(run.res["v1"])[0])

    def test_v1_says_i_dont_know_when_docs_dont_cover_it(self):
        self.assertEqual(run.score(run.res["v1"], "out"), (4, 4))

    def test_logs_carry_version_and_hash(self):
        import json
        for line in read("logs/answers.jsonl").splitlines():
            r = json.loads(line)
            self.assertIn(r["version"], ("v1", "v2"))
            self.assertEqual(len(r["hash"]), 8)

if __name__ == "__main__":
    unittest.main()
