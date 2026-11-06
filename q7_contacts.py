"""
CSA08 - Assignment 3 (CO3)
Q7 - Design a Contact-Merging Program from First Principles

DESIGN (Stage 2)
  * normalise_number : keep digits only, keep the LAST 10 digits
  * normalise_name   : lowercase, remove punctuation and titles (dr, mr ...)
  * index            : dict  normalised number -> record id        (O(1) lookup)
  * record           : {"names": set, "numbers": set, "emails": set}
  * Two contacts are the SAME PERSON if they share at least one normalised number.
  * If a contact's numbers match two different records, those records are merged.
  * A contact with no number is matched by e-mail instead; if it has neither,
    it stays as its own record.

Run:  python q7_contacts.py
"""
import random
import re
import time

random.seed(99)

TITLES = {"dr", "mr", "mrs", "ms", "miss", "prof", "shri", "smt"}


def title(text):
    print("\n" + "=" * 66)
    print(text)
    print("=" * 66)


# ------------------------------------------------------------------
# NORMALISATION
# ------------------------------------------------------------------
def normalise_number(raw):
    """'+91 98400 12345' / '09840012345' / '98400-12345' -> '9840012345'."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", str(raw))        # keep only 0-9
    if len(digits) > 10:
        digits = digits[-10:]                   # drop +91, 91 or a leading 0
    if len(digits) < 7:
        return None                             # too short to be a real number
    return digits


def normalise_name(raw):
    """'Dr. Ravi' -> 'ravi' ;  'ravi  kumar' -> 'ravi kumar'."""
    if not raw:
        return None
    words = re.sub(r"[^a-z\s]", " ", str(raw).lower()).split()
    words = [w for w in words if w not in TITLES]
    return " ".join(words) if words else None


def normalise_email(raw):
    return str(raw).strip().lower() if raw and "@" in str(raw) else None


# ------------------------------------------------------------------
# THE MERGE (dictionary keyed by normalised number, with sets)
# ------------------------------------------------------------------
def merge_contacts(contacts):
    """Return a list of merged records. Runs in O(n) on average."""
    index = {}       # key (number or mail:email) -> record id
    records = {}     # record id -> {"names", "numbers", "emails"}
    next_id = 0

    for c in contacts:
        numbers = {n for n in (normalise_number(x) for x in c.get("numbers", [])) if n}
        emails = {e for e in (normalise_email(x) for x in c.get("emails", [])) if e}
        name = normalise_name(c.get("name"))

        # keys used to recognise the person
        keys = set(numbers) if numbers else {"mail:" + e for e in emails}

        # which existing records does this contact touch?
        hits = []
        for k in keys:
            rid = index.get(k)
            if rid is not None and rid not in hits:
                hits.append(rid)

        if not hits:                                   # new person
            rid = next_id
            next_id += 1
            records[rid] = {"names": set(), "numbers": set(), "emails": set()}
        else:                                          # existing person
            rid = hits[0]
            for other in hits[1:]:                     # contact links two records: merge them
                for field in ("names", "numbers", "emails"):
                    records[rid][field] |= records[other][field]
                _repoint(index, other, rid)            # keys of the old record now point here
                del records[other]

        rec = records[rid]
        if name:
            rec["names"].add(name)
        rec["numbers"] |= numbers
        rec["emails"] |= emails

        for n in rec["numbers"]:
            index[n] = rid
        for e in rec["emails"]:
            index["mail:" + e] = rid

    return list(records.values())


def _repoint(index, old_id, new_id):
    """Make every key that pointed to old_id point to new_id."""
    for k, v in index.items():
        if v == old_id:
            index[k] = new_id


# ------------------------------------------------------------------
# ALTERNATIVE: compare every pair (O(n squared)), grouped with union-find
# ------------------------------------------------------------------
def count_people_pairwise(contacts):
    """Compare every pair of contacts. Returns the number of distinct people."""
    nums = [{n for n in (normalise_number(x) for x in c.get("numbers", [])) if n}
            for c in contacts]
    parent = list(range(len(contacts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comparisons = 0
    for i in range(len(contacts)):
        for j in range(i + 1, len(contacts)):
            comparisons += 1
            if nums[i] & nums[j]:                    # share a number
                parent[find(i)] = find(j)
    return len({find(i) for i in range(len(contacts))}), comparisons


def show(records):
    for i, r in enumerate(sorted(records, key=lambda r: sorted(r["numbers"])), 1):
        print(f"  {i}. names={sorted(r['names'])}  numbers={sorted(r['numbers'])}  "
              f"emails={sorted(r['emails'])}")


# ==================================================================
title("STAGE 3 - TEST A: HAND-CHECKED SMALL EXAMPLE")
# ==================================================================
small = [
    {"name": "Dr. Ravi", "numbers": ["+91 98400 12345"], "emails": ["r@x.com"]},
    {"name": "ravi kumar", "numbers": ["9840012345"], "emails": ["ravi@y.com"]},
    {"name": "Meena", "numbers": ["98765 43210"], "emails": []},
    {"name": "Meena S", "numbers": ["09876543210", "044-2345678"], "emails": ["meena@z.com"]},
    {"name": "Ravi", "numbers": ["99999 11111"], "emails": []},     # different person, same name
]
print("Input contacts:")
for c in small:
    print("  ", c)
result = merge_contacts(small)
print("\nMerged result:")
show(result)
print("\nHAND RESULT (worked out on paper):")
print("  Ravi (two entries share 9840012345)  -> 1 record, 2 name variants, 2 e-mails")
print("  Meena (two entries share 9876543210) -> 1 record, 2 numbers, 1 e-mail")
print("  Ravi with 9999911111                 -> a separate person (different number)")
print("  So we expect 3 records. Program gives:", len(result),
      "->", "MATCH" if len(result) == 3 else "MISMATCH")

# ==================================================================
title("STAGE 3 - TEST B: NORMALISATION")
# ==================================================================
for raw in ["+91 98400 12345", "09840012345", "98400-12345", "9840012345", "12345", "", None]:
    print(f"  number {str(raw)!r:20} -> {normalise_number(raw)!r}")
for raw in ["Dr. Ravi", "ravi   kumar", "MR. S. Kumar", "Prof.", None]:
    print(f"  name   {str(raw)!r:20} -> {normalise_name(raw)!r}")

# ==================================================================
title("STAGE 3 - TEST C: MISSING FIELDS, DUPLICATES, LINKING TWO RECORDS")
# ==================================================================
tests = {
    "empty list": [],
    "no name": [{"numbers": ["9840012345"]}],
    "no number, has e-mail (matched by e-mail)":
        [{"name": "A", "emails": ["a@x.com"]}, {"name": "A2", "emails": ["A@X.com"]}],
    "no number, no e-mail (kept alone)": [{"name": "Ghost"}, {"name": "Ghost"}],
    "exact duplicates": [{"name": "Z", "numbers": ["9000000001"]}] * 3,
    "contact links two records": [
        {"name": "P", "numbers": ["9111111111"]},
        {"name": "Q", "numbers": ["9222222222"]},
        {"name": "P/Q", "numbers": ["9111111111", "9222222222"]},
    ],
}
for name, data in tests.items():
    out = merge_contacts(data)
    print(f"{name:42} -> {len(out)} record(s)")
    if name == "contact links two records":
        show(out)

# ==================================================================
title("STAGE 3 - MEASUREMENTS: 1,000 and 100,000 contacts")
# ==================================================================
def make_contacts(n):
    """~70% unique people, the rest are duplicates in different formats."""
    people = int(n * 0.7)
    used = set()
    base = []
    while len(base) < people:
        num = f"9{random.randint(0, 999999999):09d}"
        if num not in used:
            used.add(num)
            base.append(num)

    def fmt(num):
        return random.choice([f"+91 {num[:5]} {num[5:]}", f"0{num}", f"{num[:5]}-{num[5:]}", num])

    contacts = []
    for i, num in enumerate(base):
        contacts.append({"name": random.choice(["Dr. ", "", "Mr. "]) + f"Person{i}",
                         "numbers": [fmt(num)], "emails": [f"p{i}@mail.com"]})
    while len(contacts) < n:
        i = random.randrange(people)
        contacts.append({"name": f"person{i} alt", "numbers": [fmt(base[i])], "emails": []})
    random.shuffle(contacts)
    return contacts, people


print(f"{'contacts':>10} {'unique expected':>16} {'unique found':>13} {'time (s)':>10}")
timings = {}
for n in (1_000, 100_000):
    data, expected = make_contacts(n)
    t0 = time.perf_counter()
    merged = merge_contacts(data)
    dt = time.perf_counter() - t0
    timings[n] = dt
    print(f"{n:>10,} {expected:>16,} {len(merged):>13,} {dt:>10.4f}   "
          f"{'OK' if len(merged) == expected else 'MISMATCH'}")
print(f"Time grew {timings[100_000] / timings[1_000]:.0f}x for 100x more contacts (about linear, O(n)).")

# ==================================================================
title("ALTERNATIVE: COMPARE EVERY PAIR (O(n squared))")
# ==================================================================
print(f"{'contacts':>10} {'comparisons':>14} {'pairwise (s)':>14} {'dictionary (s)':>15} {'people':>8}")
pair_times = {}
for n in (1_000, 2_000, 4_000):
    data, expected = make_contacts(n)
    t0 = time.perf_counter()
    people_pair, comps = count_people_pairwise(data)
    t_pair = time.perf_counter() - t0
    t0 = time.perf_counter()
    people_dict = len(merge_contacts(data))
    t_dict = time.perf_counter() - t0
    pair_times[n] = t_pair
    print(f"{n:>10,} {comps:>14,} {t_pair:>14.4f} {t_dict:>15.5f} {people_pair:>8}"
          f"   {'same answer' if people_pair == people_dict else 'DIFFERENT'}")

n_big = 100_000
est = pair_times[4_000] * (n_big / 4_000) ** 2
print(f"\nPairwise comparisons needed for 100,000 contacts: {n_big * (n_big - 1) // 2:,}")
print(f"Estimated pairwise time for 100,000 contacts (scaled from n=4,000): "
      f"about {est:,.0f} seconds (~{est / 3600:.1f} hours)")
print(f"Dictionary method measured for 100,000 contacts: {timings[100_000]:.2f} seconds")
