"""Day 19: prompt injection - when a web page tells your agent what to do.

Task for the agent: "read these 8 supplier pages and summarise the seal kit prices."
4 of the pages hide an instruction (an HTML comment, 1px white text, image alt text,
and one polite visible sentence). The agent in agent.py obeys everything it reads.

Four setups:
  1. no protection      - the agent has every tool and runs whatever it plans
  2. keyword filter     - skip pages containing well-known injection phrases
  3. approval gate      - risky tools (send_email, delete_file) wait for a person
  4. least privilege    - a summarising agent only gets read_page and summarise

    python3 run.py
No installs, no internet, no API key. Python 3.9+. Nothing is sent or deleted."""
import json, os
from agent import TOOLS, page_text, visible_text, plan

PAGES = sorted(f[:-5] for f in os.listdir("pages") if f.endswith(".html"))
INJECTED = set(json.load(open("labels.json"))["injected"])
PHRASES = ["ignore previous instructions", "ignore all previous", "disregard your instructions",
           "you are now", "system prompt"]
html = {p: open(f"pages/{p}.html", encoding="utf-8").read() for p in PAGES}


def run(setup):
    executed, held, refused, summarised, skipped = [], [], [], 0, []
    tools = {"read_page", "summarise"} if setup == "least privilege" else set(TOOLS)
    for p in PAGES:
        text = page_text(html[p])
        if setup == "keyword filter" and any(k in text.lower() for k in PHRASES):
            skipped.append(p)
            continue
        summarised += 1
        for tool, arg in plan(text):
            if tool not in tools:
                refused.append((p, tool, arg))          # the agent simply doesn't have it
            elif TOOLS[tool] and setup == "approval gate":
                held.append((p, tool, arg))             # waits for a person; page content is untrusted
            else:
                executed.append((p, tool, arg))         # simulated
    return executed, held, refused, summarised, skipped


print("prompt injection: a page tells the agent what to do")
print("=" * 66)
print(f"{len(PAGES)} supplier pages, {len(INJECTED)} with a hidden instruction. Task: summarise prices.\n")
print("what a person sees vs what the agent reads (p6-sealmart):")
print("  person:", " ".join(visible_text(html["p6-sealmart"]).split()))
print("  agent :", " ".join(page_text(html["p6-sealmart"]).split()))
print()
print(f"{'setup':<18}{'risky actions run':>19}{'held for a person':>19}{'pages summarised':>18}")
results = {}
for s in ["no protection", "keyword filter", "approval gate", "least privilege"]:
    ex, held, ref, summ, skip = results[s] = run(s)
    print(f"{s:<18}{len(ex):>19}{len(held):>19}{summ:>14} of {len(PAGES)}")
print()
ex = results["no protection"][0]
print("no protection - what actually ran (simulated):")
for p, tool, arg in ex:
    tag = "hidden instruction" if p in INJECTED else "benign page text"
    print(f"  {p:<15} {tool}({arg})   <- {tag}")
skip = results["keyword filter"][4]
print(f"\nkeyword filter caught {len([p for p in skip if p in INJECTED])} of {len(INJECTED)} injected pages: {', '.join(skip) or '-'}")
print("the other injected pages used no known phrase, so their actions still ran")
print(f"\napproval gate: {len(results['approval gate'][1])} actions held, 0 ran; every page still summarised")
print(f"least privilege: {len(results['least privilege'][2])} actions refused, the tools were never there")
