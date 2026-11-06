"""
CSA08 - Assignment 3 (CO3)
Q3 - Dictionaries: Farmer Helpline Complaint Analysis

Run:  python q3_dictionaries.py
"""
import random
import time
from collections import Counter

random.seed(7)


def title(text):
    print("\n" + "=" * 62)
    print(text)
    print("=" * 62)


# ------------------------------------------------------------------
title("PART 1: COMPLETE THE CODE (TODO 1 and TODO 2)")
# ------------------------------------------------------------------
calls = [
    "seeds not received seeds delayed",
    "fertiliser price high",
    "seeds price high subsidy not received",
]
STOP = {"not", "high"}

PUNCT = ".,;:!?\"'()"


def frequencies(texts, stop):
    # TODO 1 ANSWER: word -> count for every word not in stop, using dict.get()
    counts = {}
    for text in texts:
        for word in text.lower().split():
            word = word.strip(PUNCT)            # remove punctuation at the ends
            if word and word not in stop:
                counts[word] = counts.get(word, 0) + 1
    return counts


def top(counts, k):
    # TODO 2 ANSWER: k most frequent pairs, highest count first, A-Z for ties
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:k]


print(top(frequencies(calls, STOP), 3))
print("Expected: [('seeds', 3), ('price', 2), ('received', 2)]")
print("'price' comes before 'received' because the counts tie (2 and 2) and")
print("the tie is broken alphabetically: p comes before r.")

# ------------------------------------------------------------------
title("PART 2: COUNTING WITH setdefault() AND get()")
# ------------------------------------------------------------------
def frequencies_setdefault(texts, stop):
    counts = {}
    for text in texts:
        for word in text.lower().split():
            word = word.strip(PUNCT)
            if word and word not in stop:
                counts[word] = counts.setdefault(word, 0) + 1
    return counts


print("get() version        :", frequencies(calls, STOP))
print("setdefault() version :", frequencies_setdefault(calls, STOP))

# ------------------------------------------------------------------
title("PART 3: GROUP COMPLAINTS BY DISTRICT AND BY CROP")
# ------------------------------------------------------------------
complaints = [
    ("Madurai", "paddy", "seeds not received"),
    ("Salem", "cotton", "fertiliser price high"),
    ("Madurai", "cotton", "subsidy delayed"),
    ("Erode", "paddy", "seeds price high"),
    ("Salem", "paddy", "seeds delayed"),
]
by_district = {}
by_crop = {}
for district, crop, text in complaints:
    by_district.setdefault(district, []).append(text)   # dict of lists
    by_crop.setdefault(crop, []).append(text)

print("Complaints by district:")
for d, items in by_district.items():
    print(f"  {d:8} ({len(items)}): {items}")
print("Number of complaints per district:",
      {d: len(v) for d, v in by_district.items()})
print("Complaints by crop:")
for c, items in by_crop.items():
    print(f"  {c:8} ({len(items)}): {items}")

# ------------------------------------------------------------------
title("PART 4: KEY / VALUE / ITEM VIEWS AND KEY ORDER")
# ------------------------------------------------------------------
d = {"seeds": 3, "price": 2}
keys_view, values_view, items_view = d.keys(), d.values(), d.items()
print("keys()  :", keys_view)
print("values():", values_view)
print("items() :", items_view)
d["subsidy"] = 1                       # views are LIVE, they show the change
print("after adding 'subsidy' -> keys():", keys_view)
print("Insertion order is kept (Python 3.7+):", list(d))

# ------------------------------------------------------------------
title("PART 5: THREE COUNTING METHODS")
# ------------------------------------------------------------------
def clean_words(texts, stop):
    words = []
    for text in texts:
        for w in text.lower().split():
            w = w.strip(PUNCT)
            if w and w not in stop:
                words.append(w)
    return words


def count_dict(texts, stop):
    return frequencies(texts, stop)


def count_listcount(texts, stop):
    words = clean_words(texts, stop)
    return {w: words.count(w) for w in set(words)}     # scans the list once per distinct word


def count_counter(texts, stop):
    return dict(Counter(clean_words(texts, stop)))


# ------------------------------------------------------------------
title("PART 6: EDGE TESTS (empty, upper/lower case, punctuation)")
# ------------------------------------------------------------------
tests = [
    ("empty text", [""]),
    ("no complaints at all", []),
    ("mixed case", ["Seeds seeds SEEDS"]),
    ("punctuation", ["price, price! (price)."]),
    ("only stop words", ["not high not"]),
]
for name, data in tests:
    a, b, c = count_dict(data, STOP), count_listcount(data, STOP), count_counter(data, STOP)
    print(f"{name:22} dict={a}  same_as_listcount={a == b}  same_as_counter={a == c}")

# ------------------------------------------------------------------
title("PART 7: TIMING (1,000 / 10,000 / 100,000 complaints)")
# ------------------------------------------------------------------
VOCAB = ["seeds", "fertiliser", "price", "subsidy", "delayed", "received", "water",
         "pump", "loan", "insurance", "pest", "disease", "market", "transport",
         "electricity", "tractor", "rain", "drought", "yield", "quality"]
VOCAB += [f"item{i}" for i in range(80)]             # 100 distinct words in total
FILLER = ["not", "high", "the", "is"]                # some are stop words


def make_complaints(n):
    out = []
    for _ in range(n):
        k = random.randint(4, 8)
        words = [random.choice(VOCAB + FILLER) for _ in range(k)]
        out.append(" ".join(words).capitalize() + random.choice(["", ".", "!"]))
    return out


def best_time(func, data, repeat=2):
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        func(data, STOP)
        best = min(best, time.perf_counter() - t0)
    return best


print(f"{'complaints':>11} {'dict (s)':>10} {'list.count (s)':>15} {'Counter (s)':>12}"
      f" {'count/dict':>11}")
rows = []
for n in (1000, 10000, 100000):
    data = make_complaints(n)
    t_d = best_time(count_dict, data)
    t_l = best_time(count_listcount, data)
    t_c = best_time(count_counter, data)
    assert count_dict(data, STOP) == count_listcount(data, STOP) == count_counter(data, STOP)
    rows.append((n, t_d, t_l, t_c))
    print(f"{n:>11} {t_d:>10.4f} {t_l:>15.4f} {t_c:>12.4f} {t_l / t_d:>11.2f}")
print("(all three methods gave identical counts for every size)")

# ------------------------------------------------------------------
# Optional graph
# ------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ns = [r[0] for r in rows]
    plt.figure(figsize=(7, 4.5))
    plt.plot(ns, [r[1] for r in rows], "o-", label="dictionary loop")
    plt.plot(ns, [r[2] for r in rows], "s-", label="list.count()")
    plt.plot(ns, [r[3] for r in rows], "^-", label="Counter")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of complaints")
    plt.ylabel("Time (seconds)")
    plt.title("Q3: word counting methods")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig("q3_timing_graph.png", dpi=150)
    print("\nGraph saved as q3_timing_graph.png")
except ImportError:
    print("\n(matplotlib not installed - run: pip install matplotlib to get the graph)")

# ------------------------------------------------------------------
title("PART 8: WHEN THE NUMBER OF DISTINCT WORDS (d) ALSO GROWS")
# ------------------------------------------------------------------
# In real life a bigger data set has more distinct words too. Here d = n / 10.
def make_complaints_growing(n):
    vocab = [f"w{i}" for i in range(max(10, n // 10))]
    return [" ".join(random.choice(vocab) for _ in range(random.randint(4, 8)))
            for _ in range(n)]


print(f"{'complaints':>11} {'distinct d':>11} {'dict (s)':>10} {'list.count (s)':>15} {'ratio':>8}")
for n in (1000, 4000, 16000):
    data = make_complaints_growing(n)
    d_distinct = len(count_dict(data, STOP))
    t_d = best_time(count_dict, data, repeat=1)
    t_l = best_time(count_listcount, data, repeat=1)
    print(f"{n:>11} {d_distinct:>11} {t_d:>10.4f} {t_l:>15.4f} {t_l / t_d:>8.1f}")
print("The ratio keeps growing: list.count() is O(n x d), the dictionary is O(n).")
