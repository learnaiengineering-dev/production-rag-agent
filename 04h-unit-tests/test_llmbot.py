"""Unit tests for the code AROUND the model call. No network, no API key,
deterministic. Run with:  python -m unittest -v   (or pytest)."""
import unittest
from llmbot import build_prompt, parse_reply, extract_part
from fakes import ScriptedLLM

GOOD = "part: XR-4471-D\nconfidence: high"
JUNK = "Sure! It's probably the XR-4471-D one, I think."


class BuildPrompt(unittest.TestCase):
    def test_includes_the_message(self):
        self.assertIn("HP-400", build_prompt("seal kit for the HP-400"))

    def test_asks_for_the_format(self):
        self.assertIn("part:", build_prompt("anything"))


class ParseReply(unittest.TestCase):
    def test_reads_a_good_reply(self):
        self.assertEqual(parse_reply(GOOD), {"part": "XR-4471-D", "confidence": "high"})

    def test_ignores_extra_whitespace(self):
        self.assertEqual(parse_reply("  part:  XR-4471-D \nconfidence:  low "),
                         {"part": "XR-4471-D", "confidence": "low"})

    def test_missing_part_line_raises(self):
        with self.assertRaises(ValueError):
            parse_reply("confidence: high")

    def test_junk_reply_raises(self):
        with self.assertRaises(ValueError):
            parse_reply(JUNK)


class ExtractPart(unittest.TestCase):
    def test_happy_path_calls_the_model_once(self):
        llm = ScriptedLLM(GOOD)
        self.assertEqual(extract_part("x", llm)["part"], "XR-4471-D")
        self.assertEqual(llm.calls, 1)

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
