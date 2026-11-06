"""
CSA08 - Assignment 3 (CO3)
Q5 - List Comprehension: Cleaning Sensor Readings (cold storage)

Run:  python q5_comprehension.py
"""
import random
import sys
import time

random.seed(5)

LOW, HIGH = -50, 50        # outside this range = sensor error
SAFE_LOW, SAFE_HIGH = 2, 8  # vaccine safe range in Celsius


def title(text):
    print("\n" + "=" * 62)
    print(text)
    print("=" * 62)


def make_readings(n, error_rate=0.02, out_of_range_rate=0.08):
    """Mostly 2-8 C, some warmer/colder, and some sensor errors."""
    data = []
    for _ in range(n):
        x = random.random()
        if x < error_rate:
            data.append(random.choice([-99.0, 99.0, 120.0, -75.0]))   # sensor error
        elif x < error_rate + out_of_range_rate:
            data.append(round(random.uniform(8.5, 15.0), 1))          # too warm
        else:
            data.append(round(random.uniform(2.0, 8.0), 1))           # safe
    return data


# ------------------------------------------------------------------
# VERSION 1: for loop with append
# ------------------------------------------------------------------
def clean_loop(readings):
    celsius, fahrenheit = [], []
    for t in readings:
        if LOW <= t <= HIGH:
            celsius.append(t)
            fahrenheit.append(t * 9 / 5 + 32)
    return celsius, fahrenheit


# ------------------------------------------------------------------
# VERSION 2: list comprehension with condition
# ------------------------------------------------------------------
def clean_comprehension(readings):
    celsius = [t for t in readings if LOW <= t <= HIGH]
    fahrenheit = [t * 9 / 5 + 32 for t in celsius]
    return celsius, fahrenheit


# ------------------------------------------------------------------
# VERSION 3: map() and filter() with lambda
# ------------------------------------------------------------------
def clean_map_filter(readings):
    celsius = list(filter(lambda t: LOW <= t <= HIGH, readings))
    fahrenheit = list(map(lambda t: t * 9 / 5 + 32, celsius))
    return celsius, fahrenheit


# ------------------------------------------------------------------
# Alarm minutes using enumerate (keeps the ORIGINAL minute numbers)
# ------------------------------------------------------------------
def alarm_minutes(readings):
    return [minute for minute, t in enumerate(readings)
            if LOW <= t <= HIGH and not (SAFE_LOW <= t <= SAFE_HIGH)]


def alarm_minutes_loop(readings):
    out = []
    for minute, t in enumerate(readings):
        if LOW <= t <= HIGH and not (SAFE_LOW <= t <= SAFE_HIGH):
            out.append(minute)
    return out


def best_time(func, data, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        func(data)
        best = min(best, time.perf_counter() - t0)
    return best


# ------------------------------------------------------------------
title("PART 1: SMALL EXAMPLE (all three versions)")
# ------------------------------------------------------------------
sample = [4.5, 99.0, 7.2, -80.0, 9.5, 2.0, 3.3, 120.0, 1.0]
print("Readings        :", sample)
c1, f1 = clean_loop(sample)
c2, f2 = clean_comprehension(sample)
c3, f3 = clean_map_filter(sample)
print("Valid Celsius   :", c1)
print("Fahrenheit      :", [round(x, 1) for x in f1])
print("Alarm minutes   :", alarm_minutes(sample), "(outside 2-8 C, errors ignored)")
print("Loop == comprehension == map/filter:",
      (c1, f1) == (c2, f2) == (c3, f3))

# ------------------------------------------------------------------
title("PART 2: DICTIONARY AND SET COMPREHENSIONS")
# ------------------------------------------------------------------
valid_by_minute = {m: t for m, t in enumerate(sample) if LOW <= t <= HIGH}
distinct_temps = {round(t) for t in sample if LOW <= t <= HIGH}
print("Dict comprehension (minute -> temp):", valid_by_minute)
print("Set comprehension (distinct rounded temps):", sorted(distinct_temps))

# ------------------------------------------------------------------
title("PART 3: GENERAL FORMS")
# ------------------------------------------------------------------
print("[expression for item in iterable if condition]")
labels = ["OK" if SAFE_LOW <= t <= SAFE_HIGH else "ALARM" for t in sample if LOW <= t <= HIGH]
print("with if/else:", labels)

# ------------------------------------------------------------------
title("PART 4: EDGE TESTS")
# ------------------------------------------------------------------
all_valid = [3.0, 4.0, 5.0, 6.0]
all_invalid = [99.0, -99.0, 150.0]
for name, data in [("all valid", all_valid), ("all invalid", all_invalid), ("empty", [])]:
    a, b, c = clean_loop(data), clean_comprehension(data), clean_map_filter(data)
    print(f"{name:12}: valid={a[0]}  alarms={alarm_minutes(data)}  identical={a == b == c}")

# ------------------------------------------------------------------
title("PART 5: TIMING (10,000 / 100,000 / 1,000,000 readings)")
# ------------------------------------------------------------------
print(f"{'readings':>10} {'for + append':>14} {'comprehension':>14} {'map+filter':>12}")
rows = []
for n in (10_000, 100_000, 1_000_000):
    data = make_readings(n)
    t_loop = best_time(clean_loop, data)
    t_comp = best_time(clean_comprehension, data)
    t_mf = best_time(clean_map_filter, data)
    assert clean_loop(data) == clean_comprehension(data) == clean_map_filter(data)
    assert alarm_minutes(data) == alarm_minutes_loop(data)
    rows.append((n, t_loop, t_comp, t_mf))
    print(f"{n:>10} {t_loop:>14.5f} {t_comp:>14.5f} {t_mf:>12.5f}")
print("All three versions gave identical results for every size.")

# ------------------------------------------------------------------
title("PART 6: MEMORY - LIST COMPREHENSION vs GENERATOR (1,000,000 readings)")
# ------------------------------------------------------------------
data = make_readings(1_000_000)
as_list = [t for t in data if LOW <= t <= HIGH]
as_gen = (t for t in data if LOW <= t <= HIGH)
print(f"list comprehension : {sys.getsizeof(as_list):>10,} bytes  ({len(as_list):,} values stored)")
print(f"generator expression: {sys.getsizeof(as_gen):>9,} bytes  (values made one at a time)")

# the generator can be used only once
print("sum from generator :", round(sum(as_gen), 1))
print("sum again          :", sum(as_gen), "(already used up - a generator can be used only once)")
print("sum from list      :", round(sum(as_list), 1))

# ------------------------------------------------------------------
title("PART 7: ALTERNATIVE - sum() WITH A GENERATOR EXPRESSION")
# ------------------------------------------------------------------
def sum_with_list(d):
    return sum([c for c in d if LOW <= c <= HIGH])


def sum_with_generator(d):
    return sum(c for c in d if LOW <= c <= HIGH)


print(f"{'readings':>10} {'sum(list) (s)':>15} {'sum(generator) (s)':>20}")
for n in (10_000, 100_000, 1_000_000):
    d = make_readings(n)
    t1 = best_time(sum_with_list, d)
    t2 = best_time(sum_with_generator, d)
    assert abs(sum_with_list(d) - sum_with_generator(d)) < 1e-6
    print(f"{n:>10} {t1:>15.5f} {t2:>20.5f}")
print("Same answer, both O(n) time; the generator needs O(1) extra memory.")

# ------------------------------------------------------------------
# Optional graph
# ------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ns = [r[0] for r in rows]
    plt.figure(figsize=(7, 4.5))
    plt.plot(ns, [r[1] for r in rows], "o-", label="for + append")
    plt.plot(ns, [r[2] for r in rows], "s-", label="list comprehension")
    plt.plot(ns, [r[3] for r in rows], "^-", label="map + filter + lambda")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of readings")
    plt.ylabel("Time (seconds)")
    plt.title("Q5: cleaning readings, three versions")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig("q5_timing_graph.png", dpi=150)
    print("\nGraph saved as q5_timing_graph.png")
except ImportError:
    print("\n(matplotlib not installed - run: pip install matplotlib to get the graph)")
