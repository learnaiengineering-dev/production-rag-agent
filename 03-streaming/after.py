"""After: stream the answer, then check the stream really finished."""
import time
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:8787", api_key="demo")


def show_retry(words):
    print(f"Answer interrupted at {words} words. Retry?")


start, first, shown = time.monotonic(), None, []
with client.messages.stream(model="claude-sonnet-5-5", max_tokens=300,
                            messages=[{"role": "user", "content": "How do returns work?"}]) as stream:
    for text in stream.text_stream:
        first = first or time.monotonic() - start
        shown.append(text)          # in a real app: add to the chat bubble
    snap = stream.current_message_snapshot

words = len("".join(shown).split())
if snap.stop_reason is None:        # no end-of-message event: the stream was cut off
    show_retry(words)
else:
    print(f"first words: {first:.1f} s, all {words}: {time.monotonic() - start:.1f} s")
