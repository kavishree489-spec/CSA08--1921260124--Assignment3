"""
CSA08 - Assignment 3 (CO3)
Q1 - Lists and Slicing: Daily Rainfall Records

Run:  python q1_rainfall.py
"""
import random
import time
from collections import deque

random.seed(42)  # same random data every run, so results can be repeated


# ------------------------------------------------------------------
# PART 1: BASIC TASKS (weekly totals, max/min, dry days)
# ------------------------------------------------------------------
def make_readings(n):
    """Random daily rainfall in mm. About 30% of days are dry (0 mm)."""
    return [0 if random.random() < 0.3 else random.randint(1, 60) for _ in range(n)]


def weekly_totals(readings):
    """Sum of every block of 7 days using slicing. Last block may be partial."""
    return [sum(readings[i:i + 7]) for i in range(0, len(readings), 7)]


def dry_days(readings):
    """Day numbers (1-based) with 0 mm rainfall."""
    return [i + 1 for i, r in enumerate(readings) if r == 0]


# ------------------------------------------------------------------
# PART 2: MOVING AVERAGE (several methods)
# ------------------------------------------------------------------
def ma_naive(readings, w=7):
    """Naive: re-add all 7 values for every window (explicit inner loop)."""
    if len(readings) < w:
        return []
    result = []
    for i in range(len(readings) - w + 1):
        total = 0
        for j in range(i, i + w):
            total += readings[j]
        result.append(total / w)
    return result


def ma_slice(readings, w=7):
    """Naive but using slicing + sum()."""
    if len(readings) < w:
        return []
    return [sum(readings[i:i + w]) / w for i in range(len(readings) - w + 1)]


def ma_running(readings, w=7):
    """Running sum: add the new value, subtract the value that left."""
    if len(readings) < w:
        return []
    total = sum(readings[:w])
    result = [total / w]
    for i in range(w, len(readings)):
        total += readings[i] - readings[i - w]
        result.append(total / w)
    return result


def ma_deque(readings, w=7):
    """Alternative: keep only the current window in a deque(maxlen=7)."""
    window = deque(maxlen=w)
    total = 0
    result = []
    for r in readings:
        if len(window) == w:
            total -= window[0]  # the value about to be dropped
        window.append(r)
        total += r
        if len(window) == w:
            result.append(total / w)
    return result


def ma_dict(readings, w=7):
    """Alternative: readings stored in a dict keyed by day number."""
    by_day = {d: r for d, r in enumerate(readings, start=1)}
    n = len(by_day)
    if n < w:
        return []
    return [sum(by_day[d - k] for k in range(w)) / w for d in range(w, n + 1)]


# ------------------------------------------------------------------
# PART 3: COUNT ADDITIONS (to compare with the derived formulas)
# ------------------------------------------------------------------
def count_additions_naive(n, w=7):
    return w * (n - w + 1) if n >= w else 0


def count_additions_running(n, w=7):
    # first window: w additions; then 1 addition per remaining window
    return w + (n - w) if n >= w else 0


# ------------------------------------------------------------------
# PART 4: TIMING HELPER
# ------------------------------------------------------------------
def best_time(func, data, repeat=3):
    """Run several times and keep the best (least noisy) time."""
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        func(data)
        best = min(best, time.perf_counter() - t0)
    return best


def main():
    # ---------------- basic tasks ----------------
    print("=" * 60)
    print("PART 1: Basic tasks (365 days)")
    print("=" * 60)
    readings = make_readings(365)
    print("First 14 readings:", readings[:14])

    weekly = weekly_totals(readings)
    print("Number of weeks (last one partial):", len(weekly))
    print("Weekly totals (first 8):", weekly[:8])

    # exclude the partial last week when comparing, to be fair
    full_weeks = weekly[:365 // 7]
    wet_idx = full_weeks.index(max(full_weeks))
    dry_idx = full_weeks.index(min(full_weeks))
    print(f"Wettest week: week {wet_idx + 1} with {full_weeks[wet_idx]} mm")
    print(f"Driest  week: week {dry_idx + 1} with {full_weeks[dry_idx]} mm")

    mx, mn = max(readings), min(readings)
    print(f"Maximum rainfall: {mx} mm on day {readings.index(mx) + 1}")
    print(f"Minimum rainfall: {mn} mm on day {readings.index(mn) + 1}")

    dd = dry_days(readings)
    print(f"Number of dry days: {len(dd)}  (first 10: {dd[:10]})")

    # ---------------- slicing demo ----------------
    print("\n" + "=" * 60)
    print("PART 2: What the slices return")
    print("=" * 60)
    print("readings[7:14]  ->", readings[7:14], "(days 8 to 14)")
    print("readings[-7:]   ->", readings[-7:], "(last 7 days)")
    print("readings[::7]   ->", readings[::7][:8], "... (every 7th, length",
          len(readings[::7]), ")")

    # ---------------- correctness ----------------
    print("\n" + "=" * 60)
    print("PART 3: All moving-average methods give the same answer?")
    print("=" * 60)
    a, b, c, d, e = (ma_naive(readings), ma_slice(readings), ma_running(readings),
                     ma_deque(readings), ma_dict(readings))
    same = all(abs(x - y) < 1e-9 for lst in (b, c, d, e) for x, y in zip(a, lst)) \
        and len(a) == len(b) == len(c) == len(d) == len(e)
    print("Windows:", len(a), "| first 5 averages:", [round(x, 2) for x in a[:5]])
    print("naive == slice == running == deque == dict :", same)

    # ---------------- edge cases ----------------
    print("\n" + "=" * 60)
    print("PART 4: Edge cases")
    print("=" * 60)
    for name, data in [("empty list", []), ("3 values", [5, 0, 2]),
                       ("exactly 7 values", [1, 2, 3, 4, 5, 6, 7])]:
        print(f"{name:18}: naive={ma_naive(data)}  running={ma_running(data)}  "
              f"deque={ma_deque(data)}  weekly={weekly_totals(data)}  dry={dry_days(data)}")

    # ---------------- derived counts ----------------
    print("\n" + "=" * 60)
    print("PART 5: Derived number of additions")
    print("=" * 60)
    print(f"{'n':>10} {'naive 7(n-6)':>15} {'running ~n':>12}")
    for n in (365, 36500, 365000):
        print(f"{n:>10} {count_additions_naive(n):>15,} {count_additions_running(n):>12,}")

    # ---------------- experiments ----------------
    print("\n" + "=" * 60)
    print("PART 6: Timing experiment (best of 3 runs, seconds)")
    print("=" * 60)
    sizes = [365, 36500, 365000]
    rows = []
    header = f"{'n':>9} {'naive loop':>12} {'slice+sum':>12} {'running':>12} {'deque':>12} {'dict':>12} {'naive/running':>14}"
    print(header)
    for n in sizes:
        data = make_readings(n)
        t_naive = best_time(ma_naive, data)
        t_slice = best_time(ma_slice, data)
        t_run = best_time(ma_running, data)
        t_deq = best_time(ma_deque, data)
        t_dict = best_time(ma_dict, data)
        rows.append((n, t_naive, t_slice, t_run, t_deq, t_dict))
        print(f"{n:>9} {t_naive:>12.6f} {t_slice:>12.6f} {t_run:>12.6f} "
              f"{t_deq:>12.6f} {t_dict:>12.6f} {t_naive / t_run:>14.2f}")

    # ---------------- insert cost ----------------
    print("\n" + "=" * 60)
    print("PART 7: Cost of list.insert() at the front vs append() at the end")
    print("=" * 60)
    for n in (365, 36500, 365000):
        data = make_readings(n)
        t0 = time.perf_counter()
        for _ in range(1000):
            data.insert(0, 5)
        t_ins = time.perf_counter() - t0
        data = make_readings(n)
        t0 = time.perf_counter()
        for _ in range(1000):
            data.append(5)
        t_app = time.perf_counter() - t0
        print(f"n={n:>7}: 1000 x insert(0) = {t_ins:.6f}s | 1000 x append = {t_app:.6f}s")

    # ---------------- graph (optional) ----------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ns = [r[0] for r in rows]
        plt.figure(figsize=(7, 4.5))
        plt.plot(ns, [r[1] for r in rows], "o-", label="naive loop")
        plt.plot(ns, [r[3] for r in rows], "s-", label="running sum")
        plt.plot(ns, [r[4] for r in rows], "^-", label="deque")
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Number of readings (n)")
        plt.ylabel("Time (seconds)")
        plt.title("Q1: 7-day moving average timing")
        plt.legend()
        plt.grid(True, which="both", alpha=0.3)
        plt.tight_layout()
        plt.savefig("q1_timing_graph.png", dpi=150)
        print("\nGraph saved as q1_timing_graph.png")
    except ImportError:
        print("\n(matplotlib not installed - run: pip install matplotlib to get the graph)")


if __name__ == "__main__":
    main()
