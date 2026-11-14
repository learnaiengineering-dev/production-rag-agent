"""Same helper, but with a real bug: extract_part forgets to retry - it calls
the model once and returns whatever comes back. Kept so the test suite can be
shown catching it. Do not use this version."""
from typing import Callable
from llmbot import build_prompt, parse_reply
LLM = Callable[[str], str]

def extract_part(message: str, llm: LLM, max_tries: int = 2) -> dict:
    # BUG: ignores max_tries, never retries a bad reply
    return parse_reply(llm(build_prompt(message)))
