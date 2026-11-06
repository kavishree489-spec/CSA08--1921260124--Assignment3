"""
CSA08 - Assignment 3 (CO3)
Q4 - Sets: Elective Registration Clash Detection

Run:  python q4_sets.py
"""
import random
import time

random.seed(11)


def title(text):
    print("\n" + "=" * 62)
    print(text)
    print("=" * 62)


# ------------------------------------------------------------------
title("PART 1: COMPLETE THE CODE (TODO 1) - set OPERATORS")
# ------------------------------------------------------------------
ai_elective = {"192311001", "192311004", "192311007", "192311009"}
iot_elective = {"192311002", "192311004", "192311009", "192311010"}
all_students = {f"1923110{i:02d}" for i in range(1, 11)}

# TODO 1 ANSWER (operators only)
both = ai_elective & iot_elective                         # intersection
exactly_one = ai_elective ^ iot_elective                  # symmetric difference
neither = all_students - (ai_elective | iot_elective)     # difference + union

print("clash      :", sorted(both))
print("exactly one:", sorted(exactly_one))
print("neither    :", sorted(neither))

# ------------------------------------------------------------------
title("PART 2: SAME TASK WITH set METHODS (results must be identical)")
# ------------------------------------------------------------------
both_m = ai_elective.intersection(iot_elective)
exactly_one_m = ai_elective.symmetric_difference(iot_elective)
neither_m = all_students.difference(ai_elective.union(iot_elective))

print("clash      :", sorted(both_m))
print("exactly one:", sorted(exactly_one_m))
print("neither    :", sorted(neither_m))
print("Operators and methods give the same results:",
      both == both_m and exactly_one == exactly_one_m and neither == neither_m)

# ------------------------------------------------------------------
title("PART 3: OTHER SET OPERATIONS (for the Venn diagrams)")
# ------------------------------------------------------------------
print("only AI      (A - B):", sorted(ai_elective - iot_elective))
print("only IoT     (B - A):", sorted(iot_elective - ai_elective))
print("either       (A | B):", sorted(ai_elective | iot_elective))
print("counts: |A|=%d |B|=%d |A&B|=%d |A|B|=%d |A^B|=%d |neither|=%d" % (
    len(ai_elective), len(iot_elective), len(both),
    len(ai_elective | iot_elective), len(exactly_one), len(neither)))

# ------------------------------------------------------------------
title("PART 4: REMOVING DUPLICATE REGISTRATIONS")
# ------------------------------------------------------------------
raw_registrations = ["192311001", "192311004", "192311001", "192311007",
                     "192311004", "192311004"]
unique = set(raw_registrations)
print("raw list    :", raw_registrations, "->", len(raw_registrations), "entries")
print("as a set    :", sorted(unique), "->", len(unique), "unique students")
print("Information lost: order and how many times each number appeared.")

# ------------------------------------------------------------------
title("PART 5: SETS CANNOT HOLD LISTS BUT CAN HOLD TUPLES")
# ------------------------------------------------------------------
try:
    bad = {["192311001", "AI"]}
except TypeError as err:
    print("set containing a list  -> TypeError:", err)
ok = {("192311001", "AI"), ("192311004", "IoT")}
print("set containing tuples  ->", ok)

# ------------------------------------------------------------------
title("PART 6: EDGE TESTS")
# ------------------------------------------------------------------
def report(a, b, universe):
    return sorted(a & b), sorted(a ^ b), sorted(universe - (a | b))


empty = set()
print("One elective empty :", report(ai_elective, empty, all_students))
print("Both empty         :", report(empty, empty, all_students))
print("Identical electives:", report(ai_elective, set(ai_elective), all_students))

# ------------------------------------------------------------------
title("PART 7: x in list  vs  x in set  (searching for a MISSING value)")
# ------------------------------------------------------------------
SEARCHES = 100
print(f"{'size':>10} {'list (s)':>12} {'set (s)':>12} {'speed-up':>12}")
mem_rows = []
for size in (10_000, 100_000, 1_000_000):
    numbers = list(range(size))
    random.shuffle(numbers)
    s = set(numbers)
    target = -1                       # not present: the list must check every item

    t0 = time.perf_counter()
    for _ in range(SEARCHES):
        target in numbers
    t_list = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(SEARCHES):
        target in s
    t_set = time.perf_counter() - t0

    mem_rows.append((size, t_list, t_set))
    print(f"{size:>10} {t_list:>12.6f} {t_set:>12.6f} {t_list / max(t_set, 1e-9):>12.0f}x")
print(f"(each time is the total for {SEARCHES} searches)")

# ------------------------------------------------------------------
title("PART 8: COMMON STUDENTS - nested loops vs sets vs sorted walk")
# ------------------------------------------------------------------
def common_nested(a, b):
    out = []
    for x in a:
        for y in b:
            if x == y:
                out.append(x)
                break
    return out


def common_sorted(a, b):
    a, b = sorted(a), sorted(b)
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def common_set(a, b):
    return list(set(a) & set(b))


print(f"{'n = m':>8} {'nested loops (s)':>18} {'sorted walk (s)':>17} {'set & (s)':>12}")
rows = []
for n in (1000, 2000, 4000):
    a = random.sample(range(10 * n), n)
    b = random.sample(range(10 * n), n)

    t0 = time.perf_counter(); r1 = common_nested(a, b); t1 = time.perf_counter() - t0
    t0 = time.perf_counter(); r2 = common_sorted(a, b); t2 = time.perf_counter() - t0
    t0 = time.perf_counter(); r3 = common_set(a, b);    t3 = time.perf_counter() - t0
    assert sorted(r1) == sorted(r2) == sorted(r3)
    rows.append((n, t1, t2, t3))
    print(f"{n:>8} {t1:>18.5f} {t2:>17.6f} {t3:>12.6f}")
print("All three methods found the same common students.")
print("Doubling n makes nested loops about 4x slower (O(n x m)).")

# ------------------------------------------------------------------
# Optional graphs
# ------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot([r[0] for r in mem_rows], [r[1] for r in mem_rows], "o-", label="x in list")
    ax[0].plot([r[0] for r in mem_rows], [r[2] for r in mem_rows], "s-", label="x in set")
    ax[0].set(xscale="log", yscale="log", xlabel="size", ylabel="seconds",
              title="Membership test (100 searches)")
    ax[0].legend(); ax[0].grid(True, which="both", alpha=0.3)

    ax[1].plot([r[0] for r in rows], [r[1] for r in rows], "o-", label="nested loops")
    ax[1].plot([r[0] for r in rows], [r[2] for r in rows], "^-", label="sorted walk")
    ax[1].plot([r[0] for r in rows], [r[3] for r in rows], "s-", label="set &")
    ax[1].set(yscale="log", xlabel="n = m", ylabel="seconds", title="Finding common students")
    ax[1].legend(); ax[1].grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    plt.savefig("q4_timing_graph.png", dpi=150)
    print("\nGraph saved as q4_timing_graph.png")
except ImportError:
    print("\n(matplotlib not installed - run: pip install matplotlib to get the graph)")
