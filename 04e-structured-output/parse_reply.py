"""A small, dependency-free toolkit for turning a model reply into a checked Python dict.

Copy this file. Swap SCHEMA for your own. For bigger schemas use `jsonschema` or Pydantic instead of the mini-schema here.

  reply text --extract_json--> JSON text --json.loads--> object --validate--> errors? --fix--> object --validate--> ok / retry
"""
import json, re

# Mini-schema: every field is required, no other fields are allowed.
SCHEMA = {
    "category": {"type": "string", "enum": ["billing", "bug", "account", "other"]},
    "priority": {"type": "integer", "min": 1, "max": 4},
    "needs_human": {"type": "boolean"},
    "summary": {"type": "string", "max_len": 140},
}


def extract_json(text):
    """Find ONE JSON object or array inside a reply. Returns (json_text, problem). problem is None when it looks fine."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S).strip() if t.startswith("```") else t
    starts = [i for i in (t.find("{"), t.find("[")) if i != -1]
    if not starts:
        return None, "no JSON found"
    i = min(starts)
    depth, in_str, esc, end = 0, False, False, None
    for j in range(i, len(t)):
        c = t[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            continue
        if c == '"': in_str = True
        elif c in "{[": depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0: end = j; break
    if end is None:
        return None, "JSON is cut off (never closed)"
    rest = t[end + 1:]
    if re.search(r"[{\[]", rest) and re.match(r"\s*[{\[]", rest):
        return None, "more than one JSON value in the reply"
    return t[i:end + 1], None


def validate(obj, schema=SCHEMA):
    """Return a list of readable problems. Empty list = valid."""
    if not isinstance(obj, dict):
        return [f"expected a JSON object, got {type(obj).__name__}"]
    errs = []
    for k, rule in schema.items():
        if k not in obj:
            errs.append(f"{k}: missing"); continue
        v = obj[k]; t = rule["type"]
        ok = {"string": isinstance(v, str), "integer": isinstance(v, int) and not isinstance(v, bool), "boolean": isinstance(v, bool)}[t]
        if not ok:
            errs.append(f"{k}: expected {t}, got {type(v).__name__} {v!r}"); continue
        if "enum" in rule and v not in rule["enum"]:
            errs.append(f"{k}: {v!r} is not one of {rule['enum']}")
        if "min" in rule and v < rule["min"] or "max" in rule and v > rule["max"]:
            errs.append(f"{k}: {v} is outside {rule['min']} to {rule['max']}")
        if "max_len" in rule and len(v) > rule["max_len"]:
            errs.append(f"{k}: {len(v)} characters, the limit is {rule['max_len']}")
    for k in obj:
        if k not in schema:
            errs.append(f"{k}: not allowed")
    return errs


def fix(obj, schema=SCHEMA):
    """Safe, boring repairs. Each one is a POLICY choice: delete any you do not want. Returns (new_obj, what_changed)."""
    if not isinstance(obj, dict):
        return obj, []
    out, did = dict(obj), []
    for k, rule in schema.items():
        v = out.get(k)
        if rule["type"] == "integer" and isinstance(v, str) and re.fullmatch(r"\s*\d+\s*", v):
            out[k] = int(v); did.append(f"{k}: text number to integer")
        if "enum" in rule and isinstance(out.get(k), str) and out[k] not in rule["enum"] and out[k].strip().lower() in rule["enum"]:
            out[k] = out[k].strip().lower(); did.append(f"{k}: lower-cased")
    for k in [k for k in out if k not in schema]:
        del out[k]; did.append(f"{k}: unknown field dropped")
    return out, did


def parse_reply(text, schema=SCHEMA, repair=True):
    """Returns (obj_or_None, notes, errors). obj is None when the reply could not be used as it is."""
    notes = []
    js, problem = extract_json(text)
    if problem:
        return None, notes, [problem]
    if js != text.strip():
        notes.append("extracted the JSON from the reply")
    js2 = re.sub(r",\s*([}\]])", r"\1", js) if repair else js        # trailing commas
    if js2 != js:
        notes.append("removed a trailing comma"); js = js2
    try:
        obj = json.loads(js)
    except json.JSONDecodeError as e:
        return None, notes, [f"not valid JSON: {e.msg} (line {e.lineno} column {e.colno})"]
    if repair:
        obj, did = fix(obj, schema); notes += did
    errs = validate(obj, schema)
    return (obj if not errs else None), notes, errs


def retry_message(errors):
    """What to send back to the model when the reply could not be used."""
    return "Your last reply could not be used:\n" + "\n".join(f"- {e}" for e in errors) + "\nReply again with only a JSON object that matches the schema."
