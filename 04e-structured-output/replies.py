"""20 replies WE WROTE to show common failure shapes. They are not output from a real model, so nothing here says how often a model fails."""
TICKET = "My card was charged twice for the same invoice."
GOOD = {"category": "billing", "priority": 2, "needs_human": True, "summary": "Customer charged twice for one invoice."}
J = '{"category": "billing", "priority": 2, "needs_human": true, "summary": "Customer charged twice for one invoice."}'

REPLIES = [
    ("valid JSON, nothing else", J),
    ("wrapped in a code fence", "```json\n" + J + "\n```"),
    ("sentence before the JSON", "Here is the JSON you asked for:\n" + J),
    ("sentence after the JSON", J + "\nLet me know if you want more detail."),
    ("trailing comma", '{"category": "billing", "priority": 2, "needs_human": true, "summary": "Customer charged twice for one invoice.",}'),
    ("single quotes", "{'category': 'billing', 'priority': 2, 'needs_human': true, 'summary': 'Customer charged twice.'}"),
    ("Python True instead of true", '{"category": "billing", "priority": 2, "needs_human": True, "summary": "Customer charged twice."}'),
    ("cut off by the token limit", '{"category": "billing", "priority": 2, "needs_human": true, "summary": "Customer charged tw'),
    ("an array holding the object", "[" + J + "]"),
    ("priority is the word high", '{"category": "billing", "priority": "high", "needs_human": true, "summary": "Customer charged twice."}'),
    ("priority is the text 2", '{"category": "billing", "priority": "2", "needs_human": true, "summary": "Customer charged twice."}'),
    ("category is Billing", '{"category": "Billing", "priority": 2, "needs_human": true, "summary": "Customer charged twice."}'),
    ("category is refund", '{"category": "refund", "priority": 2, "needs_human": true, "summary": "Customer charged twice."}'),
    ("needs_human is missing", '{"category": "billing", "priority": 2, "summary": "Customer charged twice."}'),
    ("an extra field", '{"category": "billing", "priority": 2, "needs_human": true, "summary": "Customer charged twice.", "confidence": 0.9}'),
    ("summary is null", '{"category": "billing", "priority": 2, "needs_human": true, "summary": null}'),
    ("summary is too long", '{"category": "billing", "priority": 2, "needs_human": true, "summary": "' + "Customer was charged twice for the same invoice. " * 4 + '"}'),
    ("keys capitalised", '{"Category": "billing", "Priority": 2, "Needs_human": true, "Summary": "Customer charged twice."}'),
    ("two objects in a row", J + "\n" + J),
    ("a refusal in words", "I'm sorry, I can't help with that request."),
]
