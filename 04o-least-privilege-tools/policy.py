"""Least-privilege tools: what each agent may call, and with which arguments.

The check runs at the tool layer, before anything executes, so it holds whatever the
model asks for. Tools are simulated: nothing is read, written, sent, refunded or queried."""
import posixpath

TOOLBOX = ["read_page", "search_docs", "read_file", "write_file",
           "delete_file", "send_email", "create_refund", "run_sql"]

# Each agent gets only the tools its job needs ...
ALLOW = {
    "summariser": {"read_page"},
    "support":    {"search_docs", "send_email"},
    "reports":    {"read_file", "write_file"},
    "refunds":    {"run_sql", "create_refund"},
}

REFUND_LIMIT = 50  # dollars; above this a person approves


def inside(path, folder):
    """True only if the path stays inside folder once ../ is resolved."""
    p = posixpath.normpath(path)
    return not p.startswith("..") and (p + "/").startswith(folder.rstrip("/") + "/")


def scope(agent, tool, args, ctx):
    """... and only the arguments its job needs. Returns 'run', 'hold' or a refusal reason."""
    if tool == "send_email" and args["to"] != ctx["customer"]:
        return "only the ticket's customer"
    if tool == "read_file" and not inside(args["path"], "reports"):
        return "outside reports/"
    if tool == "write_file" and not inside(args["path"], "reports/out"):
        return "outside reports/out/"
    if tool == "run_sql":
        q = args["query"].strip().rstrip(";")
        if not q.upper().startswith("SELECT") or ";" in q:
            return "read-only"  # stands in for a read-only database role
    if tool == "create_refund" and args["amount"] > REFUND_LIMIT:
        return "hold"
    return "run"


def decide(policy, agent, tool, args, ctx):
    """policy: 'shared toolbox' | 'tool allowlist' | 'allowlist + scoped arguments'"""
    if policy == "shared toolbox":
        return "run"
    if tool not in ALLOW[agent]:
        return "no such tool"
    if policy == "tool allowlist":
        return "run"
    return scope(agent, tool, args, ctx)
