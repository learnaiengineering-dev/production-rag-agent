"""Day 14 run: a bare rating vs structured feedback on the same answers.

20 answers, each with one piece of user feedback. Deterministic, pure Python.
No model is called."""
from feedback import load, bare_summary, structured_summary, aggregatability, FIX_AREA

events = load("events.csv")
bare = bare_summary(events)
st = structured_summary(events)
agg = aggregatability(events)

print("Day 14 - feedback that tells you why")
print("=" * 56)
print()
print("What a thumbs-only system gives you:")
print(f"  {bare['down']} of {bare['total']} answers got a thumbs-down "
      f"({bare['down_rate']*100:.0f}%).")
print("  Something is wrong 40% of the time. What? No idea.")
print()
print("What a reason you can count gives you:")
for reason, n in st["by_reason"].most_common():
    print(f"  {n:>2}  {reason:<14} -> {FIX_AREA[reason]}")
print()
print(f"  Top reason: {st['top_reason']} ({st['top_n']} of {st['downs']} "
      f"downvotes) -> fix {st['fix_area']}.")
print("  Now you know where to look first.")
print()
print("Why the reason must be an enum, not free text:")
print(f"  Same {agg['downs']} downvotes, stored as free text: "
      f"{agg['distinct_free_text']} different strings - nothing to count.")
print(f"  Stored as an enum: {agg['enum_buckets']} buckets you can rank.")
