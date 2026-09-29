"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # Five DIFFERENT phrasings of the same matching intent (a fun/vintage
        # graphic top under $30), not one phrasing run five times. Criterion 1.
        #
        # Revised after the "before" run: that version of this scenario reran
        # the exact string "vintage graphic tee under $30" five times.
        # search_listings is a deterministic keyword-overlap match, so five
        # identical inputs could only ever land on 0/5 or 5/5, meaning the
        # 20% of slack criterion 1's "4 of 5" target exists to absorb was
        # never actually exercisable. Five different phrasings of the same
        # intent let a real wording-brittleness miss show up if one is there.
        # One of these five ("quirky retro novelty find") verified as a
        # genuine zero-result miss against tools.py::search_listings before
        # this went in, see the README diagnosis.
        "name": "matching query completes",
        "queries": [
            "vintage graphic tee under $30",
            "band tee under $30",
            "y2k baby tee under $30",
            "funky throwback top under $30",
            "quirky retro novelty find under $30",
        ],
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A matching query, checked by trace: does selected_item["id"] equal
        # the id inside the new_item dict suggest_outfit actually received?
        # Criterion 3 — state.
        "name": "selected item matches item passed on",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Same query every try, so the same item and outfit go into
        # create_fit_card five times — what varies is only the model's
        # wording. Criterion 4 — fit card mentions price and platform.
        "name": "fit card mentions price and platform",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # A user with nothing saved. Criterion 5 — the empty-wardrobe branch
        # in suggest_outfit still returns non-empty general styling advice.
        "name": "empty wardrobe still returns styling advice",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if "queries" in scenario:
            queries = scenario["queries"]
            if not queries or any(not q.strip() for q in queries):
                problems.append(f"scenario {i} has an empty entry in 'queries'")
        elif not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
