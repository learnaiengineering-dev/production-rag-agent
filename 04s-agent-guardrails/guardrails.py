"""Two guardrails that live in code, not in the prompt.

1. with_gate: issue_refund checks the rules itself before any money moves. Over $100 is held for
   a manager no matter what the model, the prompt or the customer says.
2. the step limit is max_steps in agent.py; run.py hands the case to a person when it is hit.

Two broken-world helpers make the failures repeatable: with_outage (the order system is down) and
with_pending (the policy engine never finishes). They are simulated; nothing real is touched.
"""
from shop import ORDERS, WINDOW_DAYS, MANAGER_OVER, issue_refund


def with_gate(tools, queue):
    refunded = set()

    def gated_issue_refund(order_id, amount):
        oid, o = str(order_id), ORDERS.get(str(order_id))
        if not o or o["already_refunded"] or oid in refunded or o["days_since_delivery"] > WINDOW_DAYS:
            return {"ok": False, "error": "this order cannot be refunded"}
        if amount > o["total"]:
            return {"ok": False, "error": f"the amount is more than the order total (${o['total']})"}
        if amount > MANAGER_OVER:
            queue.append({"order_id": oid, "amount": amount})
            return {"ok": False, "status": "held_for_manager",
                    "message": "A manager has to approve this refund. It has been sent for review. Tell the customer that."}
        refunded.add(oid)
        return issue_refund(oid, amount)

    return {**tools, "issue_refund": gated_issue_refund}


def with_outage(tools):
    return {**tools, "lookup_order": lambda order_id: {"error": "503 service unavailable: the order system is down, try again"}}


def with_pending(tools):
    return {**tools, "check_refund_policy": lambda order_id: {"status": "pending", "note": "the policy engine is still working on this, call again in a moment"}}


def with_paging(tools):
    """A list_orders tool with a bug: its next_page never runs out."""
    ids = sorted(ORDERS)

    def list_orders(page=1):
        page = int(page)
        batch = [{"order_id": ids[(2 * (page - 1) + k) % len(ids)], **ORDERS[ids[(2 * (page - 1) + k) % len(ids)]]} for k in range(2)]
        return {"page": page, "orders": batch, "next_page": page + 1}   # the bug: never null

    return {**tools, "list_orders": list_orders}


PAGING_SCHEMA = {"type": "function", "function": {"name": "list_orders", "description": "List orders, two per page. Returns next_page when there are more.",
                 "parameters": {"type": "object", "properties": {"page": {"type": "integer"}}, "required": []}}}


def with_cents_bug(tools):
    """issue_refund rejects every amount: the tool is buggy, and the error message makes a retry look sensible."""
    return {**tools, "issue_refund": lambda order_id, amount: {"error": "amount must be a whole number of cents, for example 8000 for $80"}}


def with_status_poll(tools):
    """issue_refund works, but the status it can be polled for never leaves 'processing'."""
    return {**tools, "get_refund_status": lambda order_id: {"order_id": str(order_id), "status": "processing"}}


STATUS_SCHEMA = {"type": "function", "function": {"name": "get_refund_status", "description": "Check whether a refund has completed.",
                 "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}}

HELD_MESSAGE = "This refund needs a manager's approval. I've sent it for review, and we'll email you once it has been decided."


def customer_reply(model_reply, queue):
    """The gate stops the money, not the words: in the saved runs the model still told the customer
    'A manager has approved the refund'. When a refund was held, send the customer this sentence from code instead."""
    return HELD_MESSAGE if queue else model_reply


HANDOFF = "I couldn't finish this one. I've passed it to a person, who will follow up with you."
