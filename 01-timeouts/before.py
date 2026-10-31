"""Before: the SDK defaults. One stuck call can hold a user for 10 minutes."""
import time
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:8787", api_key="demo")
print(f"timeout: {client.timeout.read:.0f} s, retries: {client.max_retries}")

start = time.monotonic()
reply = client.messages.create(
    model="claude-sonnet-5-5", max_tokens=200,
    messages=[{"role": "user", "content": "How long do refunds take?"}],
)
print(f"{time.monotonic() - start:.1f} s:", reply.content[0].text)
