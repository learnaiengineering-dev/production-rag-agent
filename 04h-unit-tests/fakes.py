"""Fake LLMs for tests: scripted, deterministic, no network."""


class ScriptedLLM:
    """Returns canned replies in order; repeats the last one once exhausted.
    Records how many times it was called and the prompts it received."""

    def __init__(self, *replies):
        if not replies:
            raise ValueError("give at least one reply")
        self._replies = list(replies)
        self.calls = 0
        self.prompts = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        reply = self._replies[min(self.calls, len(self._replies) - 1)]
        self.calls += 1
        return reply
