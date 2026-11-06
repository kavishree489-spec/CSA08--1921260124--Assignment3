"""
CSA08 - Assignment 3 (CO3)
Q6 - Nested Data: A Railway Timetable

Structure:
    timetable = {
        "12601": {
            "name":  "Chennai Mail",
            "stops": [(station, arrival, departure), ...],   # list of tuples
            "days":  {"Mon", "Wed", ...},                    # set
        },
    }

Run:  python q6_timetable.py
"""
import random
import sys
import time

random.seed(3)

ALL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def title(text):
    print("\n" + "=" * 66)
    print(text)
    print("=" * 66)


# ------------------------------------------------------------------
# PART A: HAND-MADE TIMETABLE (5 trains)
# ------------------------------------------------------------------
timetable = {
    "12601": {
        "name": "Chennai Mail",
        "stops": [("Chennai", "--", "20:00"), ("Katpadi", "22:10", "22:12"),
                  ("Jolarpettai", "23:20", "23:22"), ("Bengaluru", "01:30", "--")],
        "days": {"Mon", "Wed", "Fri"},
    },
    "12623": {
        "name": "Trivandrum Mail",
        "stops": [("Chennai", "--", "19:45"), ("Villupuram", "22:00", "22:02"),
                  ("Trichy", "00:45", "00:50"), ("Madurai", "03:10", "03:15"),
                  ("Trivandrum", "10:00", "--")],
        "days": {"Mon", "Tue", "Thu", "Sat"},
    },
    "12007": {
        "name": "Shatabdi Express",
        "stops": [("Chennai", "--", "06:00"), ("Katpadi", "07:35", "07:37"),
                  ("Bengaluru", "11:00", "--")],
        "days": {"Tue", "Wed", "Thu", "Fri", "Sat", "Sun"},
    },
    "12635": {
        "name": "Vaigai Express",
        "stops": [("Chennai", "--", "12:25"), ("Villupuram", "14:55", "14:57"),
                  ("Trichy", "17:30", "17:35"), ("Madurai", "20:30", "--")],
        "days": set(ALL_DAYS),
    },
    "16021": {
        "name": "Kaveri Express",
        "stops": [("Mysuru", "--", "13:30"), ("Bengaluru", "16:30", "16:45"),
                  ("Katpadi", "20:10", "20:12"), ("Chennai", "23:30", "--")],
        "days": {"Mon", "Thu", "Sun"},
    },
}


def print_timetable(tt):
    for number, info in tt.items():
        days = ", ".join(d for d in ALL_DAYS if d in info["days"])
        print(f"\nTrain {number} - {info['name']}   (runs: {days})")
        print(f"  {'Station':<14}{'Arrive':>8}{'Depart':>9}")
        for station, arr, dep in info["stops"]:
            print(f"  {station:<14}{arr:>8}{dep:>9}")


def dep_time(info, station):
    """Departure time of a train at a station (None if it does not stop there)."""
    for stn, arr, dep in info["stops"]:
        if stn == station:
            return dep
    return None


# ------------------------------------------------------------------
# QUERY WITHOUT INDEX: scan every train and every stop
# ------------------------------------------------------------------
def trains_at_scan(tt, station, day):
    results = []
    for number, info in tt.items():
        if day in info["days"]:
            for stn, arr, dep in info["stops"]:
                if stn == station:
                    results.append((number, info["name"], dep))
    # sort by departure time with key=lambda; "--" (no departure, last stop) goes last
    return sorted(results, key=lambda r: (r[2] == "--", r[2]))


# ------------------------------------------------------------------
# INDEX: station -> list of train numbers
# ------------------------------------------------------------------
def build_index(tt):
    index = {}
    for number, info in tt.items():
        for stn, arr, dep in info["stops"]:
            index.setdefault(stn, []).append(number)
    return index


def trains_at_indexed(tt, index, station, day):
    results = []
    for number in index.get(station, []):          # only trains that stop here
        info = tt[number]
        if day in info["days"]:
            results.append((number, info["name"], dep_time(info, station)))
    return sorted(results, key=lambda r: (r[2] == "--", r[2]))


# ------------------------------------------------------------------
# ALTERNATIVE: one flat list of tuples (train, station, arr, dep, days)
# ------------------------------------------------------------------
def to_flat(tt):
    flat = []
    for number, info in tt.items():
        for stn, arr, dep in info["stops"]:
            flat.append((number, info["name"], stn, arr, dep, frozenset(info["days"])))
    return flat


def trains_at_flat(flat, station, day):
    rows = [(r[0], r[1], r[4]) for r in flat if r[2] == station and day in r[5]]
    return sorted(rows, key=lambda r: (r[2] == "--", r[2]))


# ------------------------------------------------------------------
# BIG RANDOM TIMETABLE FOR EXPERIMENTS
# ------------------------------------------------------------------
STATIONS = [f"Station{i:03d}" for i in range(200)]


def make_big_timetable(n_trains):
    tt = {}
    for k in range(n_trains):
        n_stops = random.randint(5, 12)
        names = random.sample(STATIONS, n_stops)
        stops = []
        minutes = random.randint(0, 600)
        for s in names:
            arr = f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"
            minutes += 2
            dep = f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"
            minutes += random.randint(30, 120)
            stops.append((s, arr, dep))
        tt[f"T{k:05d}"] = {
            "name": f"Train {k}",
            "stops": stops,
            "days": set(random.sample(ALL_DAYS, random.randint(2, 7))),
        }
    return tt


def deep_size(obj, seen=None):
    """Rough total memory of nested containers (estimate only)."""
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_size(i, seen) for i in obj)
    return size


# ==================================================================
title("PART 1: THE TIMETABLE (nested structure)")
# ==================================================================
print_timetable(timetable)

print("\nDeparture time at the 3rd station of train 12623:")
print('  timetable["12623"]["stops"][2][2] ->', timetable["12623"]["stops"][2][2])
print('  (that stop is', timetable["12623"]["stops"][2][0] + ")")

# ==================================================================
title("PART 2: QUERIES - trains stopping at a station on a day")
# ==================================================================
index = build_index(timetable)
for station, day in [("Katpadi", "Wed"), ("Trichy", "Tue"), ("Chennai", "Sun")]:
    print(f"\nTrains at {station} on {day}, sorted by departure time:")
    scan = trains_at_scan(timetable, station, day)
    fast = trains_at_indexed(timetable, index, station, day)
    flat = trains_at_flat(to_flat(timetable), station, day)
    for number, name, dep in scan:
        print(f"   {dep}  {number}  {name}")
    print("   (scan, index and flat-list methods agree:", scan == fast == flat, ")")

# ==================================================================
title("PART 3: EDGE TESTS")
# ==================================================================
print("Unknown station 'Atlantis' :", trains_at_scan(timetable, "Atlantis", "Mon"),
      "| indexed:", trains_at_indexed(timetable, index, "Atlantis", "Mon"))
print("Train 12601 does not run on Sunday; Katpadi on Sun:",
      [r[0] for r in trains_at_scan(timetable, "Katpadi", "Sun")], "(12601 is absent)")
print("Station index (station -> trains):")
for stn in sorted(index):
    print(f"   {stn:<12}{index[stn]}")

# ==================================================================
title("PART 4: TIMING (100 / 1,000 / 10,000 trains, 300 queries each)")
# ==================================================================
QUERIES = 300
print(f"{'trains':>8} {'no index (s)':>14} {'with index (s)':>16} {'flat list (s)':>15}"
      f" {'build index (s)':>16} {'speed-up':>10}")
rows = []
for n in (100, 1000, 10000):
    big = make_big_timetable(n)
    qs = [(random.choice(STATIONS), random.choice(ALL_DAYS)) for _ in range(QUERIES)]

    t0 = time.perf_counter()
    for s, d in qs:
        trains_at_scan(big, s, d)
    t_scan = time.perf_counter() - t0

    t0 = time.perf_counter()
    idx = build_index(big)
    t_build = time.perf_counter() - t0

    t0 = time.perf_counter()
    for s, d in qs:
        trains_at_indexed(big, idx, s, d)
    t_idx = time.perf_counter() - t0

    flat = to_flat(big)
    t0 = time.perf_counter()
    for s, d in qs[:30]:                                   # fewer queries: it is slow
        trains_at_flat(flat, s, d)
    t_flat = (time.perf_counter() - t0) * (QUERIES / 30)   # scaled to 300 queries

    # correctness check on a few queries
    for s, d in qs[:20]:
        assert trains_at_scan(big, s, d) == trains_at_indexed(big, idx, s, d) \
            == trains_at_flat(flat, s, d)

    rows.append((n, t_scan, t_idx, t_flat, t_build, deep_size(idx), deep_size(big)))
    print(f"{n:>8} {t_scan:>14.4f} {t_idx:>16.4f} {t_flat:>15.4f} {t_build:>16.4f}"
          f" {t_scan / t_idx:>9.0f}x")
print("(flat-list time is measured on 30 queries and scaled up to 300)")

# ==================================================================
title("PART 5: EXTRA MEMORY USED BY THE INDEX (estimate)")
# ==================================================================
print(f"{'trains':>8} {'timetable (KB)':>16} {'index (KB)':>12} {'index / timetable':>19}")
for n, *_, idx_bytes, tt_bytes in [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]:
    print(f"{n:>8} {tt_bytes / 1024:>16,.0f} {idx_bytes / 1024:>12,.0f} {idx_bytes / tt_bytes:>18.1%}")
print("The index stores only references to train numbers, so it is a fraction of the timetable.")

# ------------------------------------------------------------------
# Optional graph
# ------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ns = [r[0] for r in rows]
    plt.figure(figsize=(7, 4.5))
    plt.plot(ns, [r[1] for r in rows], "o-", label="nested dicts, no index")
    plt.plot(ns, [r[2] for r in rows], "s-", label="with station index")
    plt.plot(ns, [r[3] for r in rows], "^-", label="flat list scan")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of trains")
    plt.ylabel("Time for 300 queries (seconds)")
    plt.title("Q6: station queries")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig("q6_timing_graph.png", dpi=150)
    print("\nGraph saved as q6_timing_graph.png")
except ImportError:
    print("\n(matplotlib not installed - run: pip install matplotlib to get the graph)")
