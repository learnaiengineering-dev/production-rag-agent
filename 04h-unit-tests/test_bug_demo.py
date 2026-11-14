"""The SAME two retry tests, pointed at the buggy version, to show the suite
failing. Run:  python -m unittest -v test_bug_demo"""
import unittest
from llmbot_buggy import extract_part
from fakes import ScriptedLLM
GOOD = "part: XR-4471-D\nconfidence: high"
JUNK = "Sure! It's probably the XR-4471-D one, I think."

class BuggyExtract(unittest.TestCase):
    def test_retries_a_bad_reply_then_succeeds(self):
        llm = ScriptedLLM(JUNK, GOOD)
        out = extract_part("x", llm, max_tries=2)
        self.assertEqual(out["part"], "XR-4471-D")
        self.assertEqual(llm.calls, 2)

    def test_gives_up_after_max_tries(self):
        llm = ScriptedLLM(JUNK)
        with self.assertRaises(ValueError):
            extract_part("x", llm, max_tries=2)
        self.assertEqual(llm.calls, 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
