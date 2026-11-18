"""Redact personal data from a log message before it is written.

Pattern-based, standard library only. It is good at things with a shape
(emails, phone numbers, card numbers, API keys) and blind to things without one
(names, street addresses) - run.py measures exactly that."""
import logging, re

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
SECRET = re.compile(r"\bsk-[A-Za-z0-9-]{16,}\b")
CARD = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
PHONE = re.compile(r"(?:\+61[ -]?\d|\(0\d\)|\b0\d)(?:[ -]?\d){7,9}\b")


def luhn_ok(digits):
    total, alt = 0, False
    for d in reversed(digits):
        n = int(d) * (2 if alt else 1)
        total += n - 9 if n > 9 else n
        alt = not alt
    return total % 10 == 0


def _card(m):
    digits = re.sub(r"\D", "", m.group())
    return "[CARD]" if 13 <= len(digits) <= 19 and luhn_ok(digits) else m.group()


def redact(text):
    text = EMAIL.sub("[EMAIL]", text)
    text = SECRET.sub("[SECRET]", text)
    text = CARD.sub(_card, text)          # cards before phones: both are runs of digits
    text = PHONE.sub("[PHONE]", text)
    return text


class RedactFilter(logging.Filter):
    """Attach to a handler: every record is redacted on its way to the file."""
    def filter(self, record):
        record.msg = redact(record.getMessage())
        record.args = ()
        return True
