"""Day 20: least-privilege tools for agents.

Four agents, one toolbox of 8 tools. calls.jsonl holds 17 tool calls the agents ask for:
8 their job needs and 9 that something they read told them to make (injected).
No model is called: the calls are fixed, so the only thing that changes is the policy.

Three policies:
  1. shared toolbox                - every agent can call every tool with any arguments
  2. tool allowlist                - each agent only gets the tools its job needs
  3. allowlist + scoped arguments  - ... and only the arguments its job needs
                                     (recipient, folder, read-only SQL, refund limit)

    python3 run.py
No installs, no internet, no API key. Python 3.9+. Every tool is simulated."""
import json
from policy import TOOLBOX, ALLOW, decide

CALLS = [json.loads(line) for line in open("calls.jsonl")]
CTX = {"customer": "alice@customer.example"}  # the support ticket being answered
POLICIES = ["shared toolbox", "tool allowlist", "allowlist + scoped arguments"]


def fmt(c):
    return f"{c['tool']}({', '.join(str(v) for v in c['args'].values())})"


task = [c for c in CALLS if c["source"] == "task"]
inj = [c for c in CALLS if c["source"] == "injected"]
print("least-privilege tools: 4 agents, 1 toolbox")
print("=" * 70)
print(f"{len(CALLS)} tool calls asked for: {len(task)} the job needs, {len(inj)} injected.\n")

print("permissions matrix (tool allowlist):")
print(f"  {'':<12}" + "".join(f"{t[:9]:>11}" for t in TOOLBOX))
for a in ALLOW:
    print(f"  {a:<12}" + "".join(f"{('yes' if t in ALLOW[a] else '-'):>11}" for t in TOOLBOX))
print(f"  tools exposed: shared {len(ALLOW) * len(TOOLBOX)}, allowlist {sum(len(v) for v in ALLOW.values())}\n")

print(f"{'policy':<30}{'job calls done':>16}{'injected ran':>14}{'held':>6}{'refused':>9}")
res = {}
for p in POLICIES:
    out = res[p] = [(c, decide(p, c["agent"], c["tool"], c["args"], CTX)) for c in CALLS]
    job = sum(1 for c, d in out if c["source"] == "task" and d == "run")
    ran = sum(1 for c, d in out if c["source"] == "injected" and d == "run")
    held = sum(1 for c, d in out if c["source"] == "injected" and d == "hold")
    ref = sum(1 for c, d in out if c["source"] == "injected" and d not in ("run", "hold"))
    print(f"{p:<30}{job:>10} of {len(task)}{ran:>10} of {len(inj)}{held:>6}{ref:>9}")

print("\ninjected calls: tool allowlist -> allowlist + scoped arguments")
for i, c in enumerate(CALLS):
    if c["source"] == "injected":
        a, b = res["tool allowlist"][i][1], res["allowlist + scoped arguments"][i][1]
        print(f"  {c['agent']:<11}{fmt(c):<47}{a:<14}-> {b}")

print("\nwhat the tool allowlist alone let through (right tool, wrong argument):")
for c, d in res["tool allowlist"]:
    if c["source"] == "injected" and d == "run":
        print(f"  {c['agent']:<11}{fmt(c)}")
