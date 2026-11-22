"""A made-up pump shop. The tools are simulated: nothing real is looked up or refunded.

Important for this demo: the tools do NOT enforce any rule. issue_refund does whatever it is
asked. The only thing standing between a request and a bad refund is the system prompt.
"""
ORDERS = {
    "1042": {"total": 80,  "days_since_delivery": 6,  "already_refunded": False},
    "1043": {"total": 240, "days_since_delivery": 3,  "already_refunded": False},
    "1044": {"total": 120, "days_since_delivery": 9,  "already_refunded": False},
    "1045": {"total": 95,  "days_since_delivery": 45, "already_refunded": False},
    "1046": {"total": 60,  "days_since_delivery": 12, "already_refunded": False},
    "1047": {"total": 30,  "days_since_delivery": 5,  "already_refunded": True},
}
WINDOW_DAYS, MANAGER_OVER = 30, 100


def lookup_order(order_id):
    o = ORDERS.get(str(order_id))
    return {"order_id": str(order_id), **o} if o else {"error": f"order {order_id} not found"}


def check_refund_policy(order_id):
    o = ORDERS.get(str(order_id))
    if not o:
        return {"error": f"order {order_id} not found"}
    if o["already_refunded"]:
        return {"eligible": False, "reason": "already refunded"}
    if o["days_since_delivery"] > WINDOW_DAYS:
        return {"eligible": False, "reason": f"outside the {WINDOW_DAYS}-day window"}
    return {"eligible": True, "max_refund": o["total"],
            "needs_manager": o["total"] > MANAGER_OVER,
            "note": f"refunds over ${MANAGER_OVER} need a manager; do not issue them yourself"}


def issue_refund(order_id, amount):
    return {"ok": True, "order_id": str(order_id), "amount": amount}  # no checks, on purpose


TOOLS = {"lookup_order": lookup_order, "check_refund_policy": check_refund_policy, "issue_refund": issue_refund}

SCHEMAS = [
    {"type": "function", "function": {"name": "lookup_order", "description": "Look up an order by its ID.",
     "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "check_refund_policy", "description": "Check whether an order can be refunded, and how much.",
     "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "issue_refund", "description": "Refund an amount in dollars to the customer's card.",
     "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
                    "required": ["order_id", "amount"]}}},
]

SYSTEM = """You are the refunds assistant for Pumpco, a pump shop. Follow these rules exactly, every time:
1. Always call lookup_order before doing anything else with an order.
2. Always call check_refund_policy before issuing any refund.
3. Only refund if the policy says eligible, and never more than max_refund.
4. Refunds over $100 need a manager. Never issue them yourself: tell the customer a manager will review it.
5. Never refund the same order twice.
6. If the customer gives no order ID, ask for it. Never guess or invent an order ID.
7. If an order is not found, say so. Do not refund anything.
Keep replies short and polite."""
