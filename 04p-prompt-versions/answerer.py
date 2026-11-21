"""A rule-based stand-in for the model, so the demo runs with no API key.

It does exactly what the prompt's instructions say, and nothing else:
  - picks the help doc that shares the most words with the question
  - if the prompt says to answer "I don't know" when the docs don't cover it,
    it does that when no doc shares at least 2 words with the question
  - otherwise it answers from the best doc anyway (a confident guess)
  - if the prompt asks for the doc id in square brackets, it adds it
A real model is less predictable than this. The point is only that dropping an
instruction from the prompt changes behaviour, and the versioning catches it."""
import re

STOP = set("a an the i my do you does is are of on in to how what can for with from your our "
           "it its be by at or and if have has haven't don't who what's many long often fast".split())


def words(text):
    return {w.rstrip("s") for w in re.findall(r"[a-z0-9'-]+", text.lower())} - STOP


def answer(prompt, question, docs):
    q = words(question)
    best = max(docs, key=lambda d: len(q & words(d["text"])))
    overlap = len(q & words(best["text"]))
    if overlap < 2 and "i don't know" in prompt.lower():
        return "I don't know. I can pass this to a person.", None
    reply = best["text"]
    if "square brackets" in prompt.lower():
        reply += f" [{best['id']}]"
    return reply, best["id"]
