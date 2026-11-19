"""A stand-in agent for the demo. NOT a real model.

It reads a page and does what any instruction in the page's text tells it to - the
worst case for prompt injection. The point of the demo is that the protections in
run.py hold even then, because they don't depend on the model saying no.

Tools are simulated: nothing is emailed, deleted or fetched from the internet."""
import re

TOOLS = {  # name -> risky?
    "read_page": False,
    "summarise": False,
    "send_email": True,     # data leaves your system
    "delete_file": True,    # can't be undone
}


def page_text(html):
    """Everything a model would see: visible text, comments, alt text, hidden spans."""
    text = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r" \1 ", html)
    text = re.sub(r"<!--(.*?)-->", r" \1 ", text, flags=re.S)
    return re.sub(r"<[^>]+>", " ", text)


def visible_text(html):
    """Roughly what a person sees in a browser (no comments, alt text or 1px white text)."""
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r'<span style="color:#ffffff[^"]*">.*?</span>', " ", html, flags=re.S)
    html = re.sub(r"<img[^>]*>", " ", html)
    return re.sub(r"<[^>]+>", " ", html)


def plan(text):
    """The 'model': turn every instruction it reads into a tool call."""
    calls = []
    for s in re.split(r"(?<=[.!?:])\s+|\n", text):
        addr = re.search(r"[\w.+-]+@[\w-]+\.example", s)
        if addr and re.search(r"\b(email|send|forward)\b", s, re.I):
            calls.append(("send_email", addr.group()))
        f = re.search(r"\bdelete\b.*?([\w-]+\.\w+)", s, re.I)
        if f:
            calls.append(("delete_file", f.group(1)))
    return calls
