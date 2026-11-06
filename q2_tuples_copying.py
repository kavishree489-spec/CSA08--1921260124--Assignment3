"""
CSA08 - Assignment 3 (CO3)
Q2 - Tuples, Mutability and Copying: City Bus-Stop Map

Run:  python q2_tuples_copying.py
"""
import copy
import sys
import time


def title(text):
    print("\n" + "=" * 62)
    print(text)
    print("=" * 62)


def best_time(func, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        func()
        best = min(best, time.perf_counter() - t0)
    return best


# ------------------------------------------------------------------
title("PART 1: COMPLETE THE CODE (TODO 1)")
# ------------------------------------------------------------------
rows, cols = 3, 4
bad = [[0] * cols] * rows          # every row is the SAME list object
bad[0][1] = 7

# TODO 1 ANSWER: list comprehension, so every row is a separate list
good = [[0] * cols for _ in range(rows)]
good[0][1] = 7

print("bad :", bad)
print("good:", good)
print(bad[0] is bad[1], good[0] is good[1])

# Tuples are immutable, so they can be used as dictionary keys
stops = {(13.0827, 80.2707): "Chennai Central", (13.0418, 80.2341): "T. Nagar"}
print(stops[(13.0418, 80.2341)])

# ------------------------------------------------------------------
title("PART 2: A LIST AS A DICTIONARY KEY (error)")
# ------------------------------------------------------------------
try:
    wrong = {[13.0418, 80.2341]: "T. Nagar"}
except TypeError as err:
    print("TypeError:", err)
    print("Reason: a list is mutable, so it has no fixed hash and cannot be a key.")

# ------------------------------------------------------------------
title("PART 3: BUG AND FIX SHOWN WITH is AND id()")
# ------------------------------------------------------------------
print("bad  row ids :", [id(r) for r in bad])
print("good row ids :", [id(r) for r in good])
print("bad[0] is bad[1]   ->", bad[0] is bad[1], "(same object - the bug)")
print("good[0] is good[1] ->", good[0] is good[1], "(different objects - fixed)")

# ------------------------------------------------------------------
title("PART 4: ALIASING, SHALLOW COPY, DEEP COPY")
# ------------------------------------------------------------------
original = [[1, 2], [3, 4]]
alias = original                     # no copy at all
shallow1 = copy.copy(original)       # new outer list, same inner lists
shallow2 = original[:]               # slicing = shallow copy as well
deep = copy.deepcopy(original)       # everything copied

original[0][0] = 99                  # change an INNER list of the original

print("original :", original)
print("alias    :", alias,    "| same object as original?", alias is original)
print("shallow1 :", shallow1, "| outer same?", shallow1 is original,
      "| inner same?", shallow1[0] is original[0])
print("shallow2 :", shallow2, "| outer same?", shallow2 is original,
      "| inner same?", shallow2[0] is original[0])
print("deep     :", deep,     "| outer same?", deep is original,
      "| inner same?", deep[0] is original[0])

print("\nChanging the OUTER list of the original (append a row):")
original.append([5, 6])
print("original :", original)
print("alias    :", alias,    "(sees the new row)")
print("shallow1 :", shallow1, "(does not)")
print("deep     :", deep,     "(does not)")

# ------------------------------------------------------------------
title("PART 5: UNPACK TUPLES IN A FOR LOOP")
# ------------------------------------------------------------------
for (lat, lon), name in stops.items():
    print(f"{name:16} latitude={lat}  longitude={lon}")

# ------------------------------------------------------------------
title("PART 6: FUNCTION THAT CHANGES A LIST ARGUMENT")
# ------------------------------------------------------------------
def add_stop_in_place(lst):
    lst.append("New Stop")           # changes the caller's list

def add_stop_rebind(lst):
    lst = lst + ["New Stop"]         # creates a NEW list; caller unaffected
    return lst

route = ["A", "B"]
add_stop_rebind(route)
print("after rebind function :", route)
add_stop_in_place(route)
print("after in-place function:", route, "(the caller's list changed)")

safe = ["A", "B"]
add_stop_in_place(safe[:])           # pass a copy to protect the original
print("after passing a copy   :", safe, "(unchanged)")

# ------------------------------------------------------------------
title("PART 7: LIST INSIDE A TUPLE")
# ------------------------------------------------------------------
t = ([1, 2], 3)
print("start:", t)
t[0].append(9)
print("t[0].append(9) works ->", t)
try:
    t[0] = [5]
except TypeError as err:
    print("t[0] = [5] fails ->", err)
t2 = ([1, 2], 3)
try:
    t2[0] += [4]
except TypeError as err:
    print("t2[0] += [4] raises ->", err)
print("...but the list inside still changed ->", t2)

# ------------------------------------------------------------------
title("PART 8: MEMORY AND SPEED, LIST vs TUPLE (1,000,000 values)")
# ------------------------------------------------------------------
N = 1_000_000
lst = list(range(N))
tup = tuple(range(N))
print(f"sys.getsizeof(list)  = {sys.getsizeof(lst):,} bytes")
print(f"sys.getsizeof(tuple) = {sys.getsizeof(tup):,} bytes")
print("(getsizeof counts only the container, not the integer objects inside)")

t_make_list = best_time(lambda: list(range(N)))
t_make_tuple = best_time(lambda: tuple(range(N)))


def index_all(seq):
    s = 0
    for i in range(0, N, 1):
        s += seq[i]
    return s


t_idx_list = best_time(lambda: index_all(lst))
t_idx_tuple = best_time(lambda: index_all(tup))
print(f"\n{'':22}{'list':>12}{'tuple':>12}")
print(f"{'creation time (s)':22}{t_make_list:>12.5f}{t_make_tuple:>12.5f}")
print(f"{'index 1,000,000 (s)':22}{t_idx_list:>12.5f}{t_idx_tuple:>12.5f}")

# ------------------------------------------------------------------
title("PART 9: ALTERNATIVE - GRID AS DICT KEYED BY (row, col)")
# ------------------------------------------------------------------
R, C = 1000, 1000
grid_list = [[0] * C for _ in range(R)]
grid_dict = {}
boardings = [(5, 7), (5, 7), (100, 200), (999, 999)]
for r, c in boardings:
    grid_list[r][c] += 1
    grid_dict[(r, c)] = grid_dict.get((r, c), 0) + 1

print("dict grid (only non-empty zones):", grid_dict)
print("zone (5,7) from list:", grid_list[5][7], "| from dict:", grid_dict.get((5, 7), 0))
print("zone (1,1) from list:", grid_list[1][1], "| from dict:", grid_dict.get((1, 1), 0))
list_bytes = sys.getsizeof(grid_list) + sum(sys.getsizeof(row) for row in grid_list)
print(f"list-of-lists size: about {list_bytes:,} bytes for {R*C:,} zones")
print(f"dict size         : about {sys.getsizeof(grid_dict):,} bytes for {len(grid_dict)} used zones")
