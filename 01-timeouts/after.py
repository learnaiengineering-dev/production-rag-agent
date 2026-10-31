"""After: a short timeout, the SDK's retries, and a clear message if all fail."""
import time
from anthropic import Anthropic, APITimeoutError

client = Anthropic(
    base_url="http://127.0.0.1:8787", api_key="demo",
    timeout=5.0,     # give up on one attempt after 5 s
    max_retries=2,   # then retry, with backoff and jitter
)

start = time.monotonic()
try:
    reply = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=200,
        messages=[{"role": "user", "content": "How long do refunds take?"}],
    )
    print(f"{time.monotonic() - start:.1f} s:", reply.content[0].text)
except APITimeoutError:
    print("Sorry, that took too long. Please try again.")
