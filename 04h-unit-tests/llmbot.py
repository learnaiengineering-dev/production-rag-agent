"""A tiny 'find the part number' helper that calls an LLM through an INJECTED
boundary. The deterministic code around the call - building the prompt, parsing
the reply, retrying a bad one - can then be unit-tested without ever touching a
real model. The real model is never imported in this file."""
from typing import Callable

LLM = Callable[[str], str]  # takes a prompt, returns the model's text reply


def build_prompt(message: str) -> str:
    """Turn a user message into the prompt we send. Pure string work."""
    return (
        "Find the pump part number in the message.\n"
        "Reply with exactly two lines:\n"
        "part: <PART-ID or NONE>\n"
        "confidence: <low|medium|high>\n\n"
        f"Message: {message}"
    )


def parse_reply(text: str) -> dict:
    """Turn the model's two lines into a dict. Raises ValueError when the
    required 'part' line is missing or empty - so a junk reply is caught here,
    not three functions later."""
    fields = {}
    for line in text.strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip().lower()] = val.strip()
    part = fields.get("part", "")
    if not part:
        raise ValueError("reply has no 'part' line")
    return {"part": part, "confidence": fields.get("confidence", "unknown")}


def extract_part(message: str, llm: LLM, max_tries: int = 2) -> dict:
    """Build the prompt, call the injected llm, parse the reply. Retry a bad
    reply up to max_tries, then raise. `llm` is passed in, so a test can hand it
    a fake and no network call ever happens."""
    prompt = build_prompt(message)
    last_error = None
    for _ in range(max_tries):
        reply = llm(prompt)
        try:
            return parse_reply(reply)
        except ValueError as err:
            last_error = err
    raise ValueError(f"no usable reply after {max_tries} tries: {last_error}")
