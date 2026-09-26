"""
Manual verification script — not part of the graded submission, not run by
run_eval.py. This checks the running code against the specific claims written
in README.md (Tool Inventory + Planning Loop), and prints the session dict
after every step of the loop so state moving through `session` is visible,
not just asserted.

Delete this file, or leave it — it isn't referenced by anything graded.

Run it from the project root:
    ./.venv/Scripts/python.exe check_agent.py      (bash / Git Bash)
    .\.venv\Scripts\python.exe check_agent.py      (PowerShell)
"""

import config
from agent import new_session, _parse_query
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_listings

PASS = "PASS"
FAIL = "FAIL"
results = []


def check(label, condition):
    results.append((label, PASS if condition else FAIL))
    print(f"  [{PASS if condition else FAIL}] {label}")


# ── Tool Inventory: search_listings ────────────────────────────────────────
print("\n=== search_listings ===")

r = search_listings("graphic tee", max_price=30)
check("returns a list", isinstance(r, list))
check("every result has price <= 30", all(x["price"] <= 30 for x in r))
check("capped at SEARCH_RESULT_LIMIT", len(r) <= config.SEARCH_RESULT_LIMIT)

# size semantics from the README: "m" matches "S/M" but not "us 9";
# "l" does NOT match "XL"
r_m = search_listings("tee", size="M")
check("size='M' returns only whole-token matches (no crash, list back)",
      isinstance(r_m, list))
r_l_vs_xl = search_listings("", size="L")
check("size='L' does not pick up 'XL' listings (whole-token match)",
      all(x["size"].upper() != "XL" for x in r_l_vs_xl))

empty = search_listings("this matches absolutely nothing zzqxv", max_price=1)
check("no match -> [] (empty list, not None)", empty == [])

first = load_listings()[0]
required_keys = {"id", "title", "description", "category", "style_tags",
                  "size", "condition", "price", "colors", "brand", "platform"}
check("listing dict has all documented fields", required_keys.issubset(first.keys()))

# ── Tool Inventory: suggest_outfit ──────────────────────────────────────────
print("\n=== suggest_outfit ===")

item = load_listings()[0]
out_full = suggest_outfit(item, get_example_wardrobe())
check("non-empty string with real wardrobe", isinstance(out_full, str) and out_full.strip() != "")

out_empty = suggest_outfit(item, get_empty_wardrobe())
check("empty wardrobe -> still non-empty string (not '', not raise)",
      isinstance(out_empty, str) and out_empty.strip() != "")

# ── Tool Inventory: create_fit_card ─────────────────────────────────────────
print("\n=== create_fit_card ===")

card = create_fit_card(out_full, item)
check("non-empty caption", isinstance(card, str) and card.strip() != "")
check("mentions the item's price (loose match on the number itself)",
      str(int(item["price"])) in card)
check("mentions the platform", item["platform"].lower() in card.lower())

card_blank = create_fit_card("", item)
check("blank outfit -> descriptive message, not a raise",
      isinstance(card_blank, str) and card_blank.strip() != "")
check("blank outfit -> does NOT call the model (message differs from a real card)",
      card_blank != card)

# ── Planning Loop: walk the session by hand, one field at a time ───────────
print("\n=== Planning Loop / session state, happy path ===")

query = "vintage graphic tee under $30"
session = new_session(query, get_example_wardrobe())
print("start:", {k: session[k] for k in ("query", "parsed", "search_results", "selected_item")})

session["parsed"] = _parse_query(query)
print("after parse:", session["parsed"])
check("parsed picked up max_price=30", session["parsed"]["max_price"] == 30.0)
check("parsed description has no leftover 'under $30'", "under" not in session["parsed"]["description"])

session["search_results"] = search_listings(**session["parsed"])
print(f"after search: {len(session['search_results'])} result(s), "
      f"first={session['search_results'][0]['title'] if session['search_results'] else None}")
check("search_results non-empty for this query", len(session["search_results"]) > 0)

session["selected_item"] = session["search_results"][0]
print("selected_item:", session["selected_item"]["id"], session["selected_item"]["title"])

session["outfit_suggestion"] = suggest_outfit(session["selected_item"], session["wardrobe"])
print("outfit_suggestion (first 80 chars):", session["outfit_suggestion"][:80], "...")

session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])
print("fit_card (first 80 chars):", session["fit_card"][:80], "...")

check("selected_item is the SAME object read by suggest_outfit (via session, not a fresh copy)",
      session["selected_item"] is session["search_results"][0])

# ── Planning Loop: the branch, empty search ────────────────────────────────
print("\n=== Planning Loop / session state, empty-search branch ===")

query2 = "designer ballgown size XXS under $5"
session2 = new_session(query2, get_example_wardrobe())
session2["parsed"] = _parse_query(query2)
print("after parse:", session2["parsed"])

session2["search_results"] = search_listings(**session2["parsed"])
print("search_results:", session2["search_results"])
check("this query has no matches (confirms it's testing the branch, not a bug)",
      session2["search_results"] == [])

if not session2["search_results"]:
    session2["error"] = "No results — placeholder to demonstrate the branch stopping here."

check("error is set", session2["error"] is not None)
check("selected_item stays None (never reached)", session2["selected_item"] is None)
check("outfit_suggestion stays None (suggest_outfit never called)", session2["outfit_suggestion"] is None)
check("fit_card stays None (create_fit_card never called)", session2["fit_card"] is None)

# ── Same two paths, but through the real run_agent() end to end ───────────
print("\n=== run_agent() end to end (this is what agent.py actually returns) ===")

from agent import run_agent

happy = run_agent(query, get_example_wardrobe())
check("run_agent happy path: error is None", happy["error"] is None)
check("run_agent happy path: fit_card is set", happy["fit_card"] is not None)

sad = run_agent(query2, get_example_wardrobe())
check("run_agent empty-search path: error is set", sad["error"] is not None)
check("run_agent empty-search path: fit_card is still None", sad["fit_card"] is None)

# ── Summary ──────────────────────────────────────────────────────────────
print("\n=== Summary ===")
n_pass = sum(1 for _, v in results if v == PASS)
n_fail = sum(1 for _, v in results if v == FAIL)
print(f"{n_pass} passed, {n_fail} failed out of {len(results)}")
for label, verdict in results:
    if verdict == FAIL:
        print(f"  FAILED: {label}")
