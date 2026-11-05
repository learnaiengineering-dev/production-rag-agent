"""Show WHEN each word reached the screen: waiting for the whole answer vs streaming it.

  python mock_server.py            # terminal 1
  python timeline.py               # terminal 2
Writes timeline.json (seconds for each word) when TIMES_JSON is set, e.g. TIMES_JSON=times.json python timeline.py
"""
import json, os, time
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:8787", api_key="demo")
ask = dict(model="claude-sonnet-5-5", max_tokens=300, messages=[{"role": "user", "content": "How do returns work?"}])

start = time.monotonic()
reply = client.messages.create(**ask)                      # waits for everything
waited = time.monotonic() - start
words = reply.content[0].text.split()

start, arrivals = time.monotonic(), []
with client.messages.stream(**ask) as stream:
    for text in stream.text_stream:
        arrivals += [round(time.monotonic() - start, 2)] * len(text.split())

print(f"waiting: all {len(words)} words appear at once after {waited:.1f} s")
print(f"streaming: first word after {arrivals[0]:.1f} s, last word after {arrivals[-1]:.1f} s")
if os.environ.get("TIMES_JSON"):
    json.dump({"words": len(words), "waited": round(waited, 2), "arrivals": arrivals}, open(os.environ["TIMES_JSON"], "w"))
