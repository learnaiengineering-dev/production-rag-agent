"""Ask the same question many times at temperature 0 and count how many different answers come back.

Hosted API (needs ANTHROPIC_API_KEY):   python same_question.py anthropic 20
Local model (needs Ollama running):     python same_question.py ollama 20

Setup (once):  python -m venv .venv && .venv/bin/pip install anthropic requests
Change MODEL to a model you have access to.
"""
import sys, json, collections

PROMPT = "List three risks of running an LLM feature in production, one sentence each."
MODELS = {"anthropic": "claude-sonnet-5-5", "ollama": "llama3.2"}


def ask_anthropic(model):
    import anthropic
    r = anthropic.Anthropic().messages.create(
        model=model, max_tokens=200, temperature=0,
        messages=[{"role": "user", "content": PROMPT}])
    return r.content[0].text


def ask_ollama(model):
    import requests
    r = requests.post("http://127.0.0.1:11434/api/generate", timeout=120,
                      json={"model": model, "prompt": PROMPT, "stream": False,
                            "options": {"temperature": 0}})
    r.raise_for_status()
    return r.json()["response"]


def first_difference(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def main():
    backend = sys.argv[1] if len(sys.argv) > 1 else "anthropic"
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    ask = {"anthropic": ask_anthropic, "ollama": ask_ollama}[backend]
    model = MODELS[backend]
    answers = [ask(model) for _ in range(runs)]
    counts = collections.Counter(answers)
    print(f"{backend} / {model}: {runs} runs at temperature 0 -> {len(counts)} different answer(s)")
    first, _ = counts.most_common(1)[0]
    for text, n in counts.most_common():
        where = "" if text == first else f", first differs from the most common answer at character {first_difference(first, text)}"
        print(f"- {n} of {runs} runs{where}")
    json.dump({"backend": backend, "model": model, "prompt": PROMPT, "answers": answers},
              open(f"same_question_{backend}.json", "w"), indent=1)
    print(f"saved all {runs} answers to same_question_{backend}.json")


main()
