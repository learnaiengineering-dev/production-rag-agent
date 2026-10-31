"""Before: wait for the whole answer. The user sees nothing until it's all done."""
import time
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:8787", api_key="demo")
start = time.monotonic()
reply = client.messages.create(model="claude-sonnet-5-5", max_tokens=300,
                               messages=[{"role": "user", "content": "How do returns work?"}])
print(f"first words on screen after {time.monotonic() - start:.1f} s")
