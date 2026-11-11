"""Temperature is not determinism. A toy sampler, 20 runs per setting.

  python run.py

No API key, no downloads, no packages. NOT a language model: the word scores below are invented.
Part 1: temperature rescales the scores before one word is drawn. 20 runs at each temperature, counting different answers.
Part 2: at temperature 0 the top word always wins, so where does variation come from? Rounding. Adding the same
        numbers in a different order gives a slightly different total in 32-bit floats. When two words are
        near-tied, a different order can flip the winner. We add up the same numbers in 20 different orders.
Settings are fixed in the file and were not tuned. Everything is seeded, so the output is the same every time.
"""
import math, random, struct
from collections import Counter

# ---- Part 1: a toy answer made of three word choices. Scores are invented. ----
SLOTS = [  # (words and scores for the choice)
    [("wrong", 2.0), ("slow", 1.2), ("costly", 0.8), ("untested", 0.4)],
    [("measure", 1.8), ("test", 1.3), ("monitor", 1.0), ("log", 0.2)],
    [("early", 1.5), ("often", 1.0), ("first", 0.6)],
]
TEMPS = [0, 0.3, 0.7, 1.0, 1.5]
RUNS = 20


def probs(scores, t):
    ex = [math.exp(s / t) for _, s in scores]
    z = sum(ex)
    return [e / z for e in ex]


def pick(scores, t, rng):
    if t == 0:                                   # greedy: the top score always wins
        return max(scores, key=lambda x: x[1])[0]
    return rng.choices([w for w, _ in scores], weights=probs(scores, t))[0]


def answer(t, rng):
    a, b, c = (pick(s, t, rng) for s in SLOTS)
    return f"The biggest risk is {a} answers, so {b} them {c}."


def part1():
    out = {}
    for t in TEMPS:
        rng = random.Random(1000 + int(t * 100))
        out[t] = [answer(t, rng) for _ in range(RUNS)]
    return out


# ---- Part 2: temperature 0, rounding, and near-ties ----
def f32(x):                                       # round to the nearest 32-bit float
    return struct.unpack("f", struct.pack("f", x))[0]


def dot32(h, w, order):                           # add up h[i]*w[i] one at a time, in the given order, in 32-bit floats
    s = 0.0
    for i in order:
        s = f32(s + f32(h[i] * w[i]))
    return s


N = 2048
def make_pair(gap, seed=7):
    """Two words with the same inputs h and almost the same weights. gap = their true score difference (in the real numbers)."""
    rng = random.Random(seed)
    h = [rng.gauss(0, 1) for _ in range(N)]
    wa = [rng.gauss(0, 1) for _ in range(N)]
    exact_a = math.fsum(x * y for x, y in zip(h, wa))
    wb = [rng.gauss(0, 1) for _ in range(N)]       # B gets its own random weights, then one weight is nudged
    k = max(range(N), key=lambda i: abs(h[i]))      # so that B's true score is exactly `gap` below A's
    wb[k] += (exact_a - gap - math.fsum(x * y for x, y in zip(h, wb))) / h[k]
    exact_b = math.fsum(x * y for x, y in zip(h, wb))
    return h, wa, wb, exact_a - exact_b, exact_a


def noise(orders=RUNS):
    """How much does one word's 32-bit total move when the same numbers are added in a different order? (standard deviation)"""
    h, wa, _, _, _ = make_pair(0.0)
    rng = random.Random(99); tot = []
    for _ in range(orders):
        order = list(range(N)); rng.shuffle(order); tot.append(dot32(h, wa, order))
    m = sum(tot) / len(tot)
    return math.sqrt(sum((x - m) ** 2 for x in tot) / len(tot)), len(set(tot)), max(tot) - min(tot)


def part2(gap, orders=RUNS):
    h, wa, wb, true_gap, _ = make_pair(gap)
    rng = random.Random(99)
    picks = []
    for _ in range(orders):
        order = list(range(N)); rng.shuffle(order)
        picks.append("A" if dot32(h, wa, order) >= dot32(h, wb, order) else "B")
    return picks, true_gap


def main():
    res = part1()
    print("PART 1. A toy sampler (invented word scores), 20 runs at each temperature.\n")
    print("  temperature | different answers in 20 runs | most common answer appeared")
    for t in TEMPS:
        c = Counter(res[t])
        print(f"  {t:<11} | {len(c):>3}                          | {c.most_common(1)[0][1]} of {RUNS}")
    print("\n  Chance the single top word is picked at each choice (word 1 'wrong' / word 2 'measure' / word 3 'early'):")
    for t in TEMPS[1:]:
        print(f"    temperature {t}: " + " / ".join(f"{max(probs(s, t)):.2f}" for s in SLOTS))
    print("\n  Temperature 0, all 20 runs:", Counter(res[0]).most_common(1)[0][0])
    print("\nPART 2. Temperature 0, so the top word always wins. Same numbers, added up in 20 different orders (32-bit floats).\n")
    _, _, _, _, ex = make_pair(0.0)
    sd, distinct, spread = noise()
    print(f"  Word A's total came out as {distinct} different 32-bit values over 20 orders (spread {spread:.6f}, standard deviation {sd:.6f}).")
    print("  A near-tie is defined as a true gap equal to one standard deviation of that rounding noise.\n")
    for label, gap in (("clear lead (gap 0.5)", 0.5), (f"near-tie (gap {sd:.6f})", sd)):
        picks, tg = part2(gap)
        c = Counter(picks)
        print(f"  {label:<30} true gap {tg:.6f} | word A wins {c['A']} of 20, word B wins {c['B']} of 20")
    print("\n  A score of about", f"{ex:.1f}", "was added up from", N, "numbers each time.")


if __name__ == "__main__":
    main()
