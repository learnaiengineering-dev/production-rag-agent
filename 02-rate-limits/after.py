"""After: cap how many requests are in flight, and keep the SDK's retries as a backup."""
import asyncio, time
from anthropic import AsyncAnthropic, RateLimitError

client = AsyncAnthropic(base_url="http://127.0.0.1:8787", api_key="demo")
limit = asyncio.Semaphore(4)   # at most 4 requests in flight


async def ask(i):
    async with limit:
        await client.messages.create(model="claude-sonnet-5-5", max_tokens=50,
                                     messages=[{"role": "user", "content": f"Summarise ticket {i}"}])


async def main():
    start = time.monotonic()
    results = await asyncio.gather(*(ask(i) for i in range(20)), return_exceptions=True)
    failed = sum(isinstance(r, RateLimitError) for r in results)
    print(f"{20 - failed} answered, {failed} failed with 429 in {time.monotonic() - start:.1f} s")

asyncio.run(main())
