"""The pattern from the article: one try on the main model, then a backup model, then a plain message.

answer() returns (who, text). who is "main", "backup" or "message".
"""
import anthropic

MAIN, BACKUP = "claude-sonnet-5-5", "claude-haiku-5-5"
SORRY = "Our assistant is unavailable right now. Please try again in a minute."


def is_outage(e):
    """Fall back for timeouts, dropped connections, 429 and 5xx. A 400 or 401 is our bug: a backup model will not fix it."""
    if isinstance(e, (anthropic.APIConnectionError, anthropic.APITimeoutError)):
        return True
    return isinstance(e, anthropic.APIStatusError) and (e.status_code == 429 or e.status_code >= 500)


async def answer(client, **ask):
    once = client.with_options(max_retries=0)          # no waiting around on a model that is down
    for who, model in (("main", MAIN), ("backup", BACKUP)):
        try:
            msg = await once.messages.create(model=model, **ask)
            return who, msg.content[0].text
        except anthropic.APIError as e:
            if not is_outage(e):
                raise                                    # our bug, not an outage
    return "message", SORRY
