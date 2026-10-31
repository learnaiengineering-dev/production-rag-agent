"""The trap: a plain streaming loop. If the connection drops, the loop just ends."""
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:8787", api_key="demo")
shown = []
with client.messages.stream(model="claude-sonnet-5-5", max_tokens=300,
                            messages=[{"role": "user", "content": "How do returns work?"}]) as stream:
    for text in stream.text_stream:
        shown.append(text)
print(f"done: {len(''.join(shown).split())} words, no error raised")
