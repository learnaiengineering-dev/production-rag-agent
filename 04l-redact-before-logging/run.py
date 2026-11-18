"""Day 17: redact personal data before you log it.

Logs 12 made-up support messages three ways - raw, through RedactFilter, and
metadata only (no text) - then checks every labelled item (name, email, phone, card, address, key):
is it still readable in the log file?

    python3 run.py
No installs, no internet, no API key. Python 3.9+. Every name, number and
address in messages.json is made up (cards are public test numbers)."""
import json, logging, os
from collections import Counter
from redact import RedactFilter

msgs = json.load(open("messages.json", encoding="utf-8"))
os.makedirs("logs", exist_ok=True)


def write_log(path, redacting):
    log = logging.getLogger(path)
    log.handlers.clear()
    log.propagate = False
    log.setLevel(logging.INFO)
    h = logging.FileHandler(path, mode="w", encoding="utf-8")
    h.setFormatter(logging.Formatter("%(levelname)s chat %(message)s"))
    if redacting:
        h.addFilter(RedactFilter())
    log.addHandler(h)
    for m in msgs:
        log.info("%s user=%s", m["id"], m["text"])
    h.close()
    return open(path, encoding="utf-8").read()


raw = write_log("logs/raw.log", redacting=False)
red = write_log("logs/redacted.log", redacting=True)

# option 3: don't put the text in the log at all - log what you need to debug
with open("logs/metadata.log", "w", encoding="utf-8") as f:
    for m in msgs:
        f.write(f"INFO chat {m['id']} chars={len(m['text'])} words={len(m['text'].split())}\n")
meta = open("logs/metadata.log", encoding="utf-8").read()

items = [(kind, value) for m in msgs for kind, value in m["pii"]]
order = ["email", "phone", "card", "secret", "name", "address"]
total, leaked_raw, leaked_red = Counter(), Counter(), Counter()
missed = []
for kind, value in items:
    total[kind] += 1
    leaked_raw[kind] += value in raw
    if value in red:
        leaked_red[kind] += 1
        missed.append((kind, value))
keeps = [k for m in msgs for k in m.get("keep", [])]
kept = sum(k in red for k in keeps)

print("redact before you log")
print("=" * 52)
print(f"{len(msgs)} made-up messages, {len(items)} personal items labelled\n")
print("one line, before and after:")
print("  raw     :", raw.splitlines()[0])
print("  redacted:", red.splitlines()[0])
print()
print(f"{'type':<9}{'items':>6}{'in raw log':>12}{'in redacted log':>17}")
for k in order:
    print(f"{k:<9}{total[k]:>6}{leaked_raw[k]:>12}{leaked_red[k]:>17}")
caught = len(items) - len(missed)
print(f"{'total':<9}{len(items):>6}{sum(leaked_raw.values()):>12}{len(missed):>17}")
print()
print(f"caught {caught} of {len(items)}. still readable in the redacted log:")
for kind, value in missed:
    print(f"  {kind:<8} {value}")
print()
print(f"metadata-only log (id and size, no text): {sum(v in meta for _, v in items)} of {len(items)} readable")
print(f"not personal, should survive: {kept} of {len(keeps)} kept (order number, part numbers, a year)")
