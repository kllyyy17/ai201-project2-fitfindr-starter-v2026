# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr takes a plain-language request like `"vintage graphic tee under $30, size M"` and turns it into a full secondhand-shopping recommendation. It pulls the size and price ceiling out of the query, searches a mock listings dataset for the best keyword match, then asks the model to suggest an outfit pairing that item with the user's existing wardrobe (or general styling advice if the wardrobe is empty), and finally turns that suggestion into a short, postable caption naming the item, its price, and its platform. If nothing in the dataset survives the filters, it stops early and tells the user what to loosen — price, size, or keywords — instead of guessing.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the mock listings dataset by size and price ceiling, scores what's left by keyword overlap with the description, and returns the best matches.
- **Inputs:**
  - `description` (str) — free-text keywords describing what the user wants, e.g. `"vintage graphic tee"`.
  - `size` (str or None) — a size string to filter by, matched case-insensitively against each listing's `size` field as a whole-token match (e.g. splitting on `/` and `,`), not a substring test — so `"m"` matches `"S/M"` but not `"us 9"`, and `"l"` does not match `"XL"`. `None` skips size filtering.
  - `max_price` (float or None) — maximum price, inclusive. `None` skips price filtering.
- **Returns:** A `list[dict]`, sorted best-match-first, of at most `config.SEARCH_RESULT_LIMIT` listing dicts. Each dict has: `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or None), `platform` (str).
- **When it has nothing:** Returns `[]` — an empty list, never `None` and never an exception — when no listing survives the size/price filters, or when everything that survives scores zero keyword overlap with `description`.

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfits pairing a thrifted item with the user's existing wardrobe (or with general styling advice if they have none).
- **Inputs:**
  - `new_item` (dict) — a listing dict (the shape returned by `search_listings`) for the item under consideration.
  - `wardrobe` (dict) — a wardrobe dict with an `'items'` key holding a `list[dict]`, each item shaped like `{id, name, category, colors, style_tags, notes}` (`notes` may be `None`). `items` may be `[]`.
- **Returns:** A non-empty `str` of outfit suggestions in prose, naming specific wardrobe pieces by name when the wardrobe is non-empty.
- **When it has nothing:** When `wardrobe['items']` is `[]`, it does not return `""` and does not raise — it returns a non-empty `str` of general styling advice for `new_item` alone (no wardrobe pieces named, since none exist).

### `create_fit_card`

- **What it does:** Calls the model to turn an outfit suggestion and an item into a short, postable caption.
- **Inputs:**
  - `outfit` (str) — the suggestion string returned by `suggest_outfit()`.
  - `new_item` (dict) — the listing dict for the item (same shape as `search_listings` returns).
- **Returns:** A `str`, two to four sentences, that mentions the item, its price, and its platform once each, and reads like a social post rather than a product description.
- **When it has nothing:** If `outfit` is `""` or whitespace-only, returns a descriptive message string explaining the card couldn't be built — it does not raise and does not call the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (loosen the price, drop the size, try different keywords) and return the session immediately — do not call `suggest_outfit`. Otherwise, take `session["search_results"][0]` as `session["selected_item"]` and continue to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex — pull `size` from a `\bsize\s+(\S+)\b` pattern and `max_price` from an `under \$?(\d+(\.\d+)?)` pattern, then strip those matched substrings out of the query and use whatever text remains as `description`.

**What moves through the session, in order:** `query` → `parsed` (`description`, `size`, `max_price`) → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`. `error` is set only on the empty-search branch, in which case everything after `search_results` stays `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two outfit ideas using the new Y2K Butterfly Baby Tee and pieces from your existing wardrobe:

**Outfit 1: Casual Y2K Streetwear**
*   **Top:** Y2K Baby Tee (Butterfly Print)
*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   **Why it works:** The tight, fitted silhouette of the baby tee creates a great Y2K-inspired proportion balance when paired with your baggy, dark wash jeans. Add the chunky white sneakers and black crossbody bag to complete an effortless, everyday throwback look.

**Outfit 2: Edgy Contrast**
*   **Top:** Y2K Baby Tee (Butterfly Print)
*   **Bottoms:** Wide-leg khaki trousers
*   **Outerwear:** Vintage black denim jacket (slightly cropped)
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt
*   **Why it works:** Pairing the feminine, pink-and-purple butterfly print with your structured wide-leg khakis and chunky black combat boots creates a cool contrast between soft and edgy. Tucking the baby tee in with the brown leather belt and layering the slightly cropped denim jacket on top ties the whole outfit together.

  Fit card: I am losing my mind over this thrift find—I just scored the cutest Y2K Butterfly Baby Tee on Depop for only $18, and it's literal perfection! The pink-and-purple print gives off major 2000s pop-star energy, whether you want to style it with baggy jeans for effortless streetwear or toughen it up with combat boots. Honestly, my inner child is screaming, and I can't wait to wear this everywhere. 🦋✨

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two outfit ideas that pair the new Vintage Levi's 501s with pieces from your existing wardrobe:

*   **Top:** White ribbed tank top
*   **Outerwear:** Vintage black denim jacket (slightly cropped)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* The medium-wash 501s will pop against the black denim jacket for a classic "denim-on-denim" look. Tucking in the white ribbed tank breaks up the dark tones, while the cropped jacket and chunky sneakers keep the silhouette balanced and effortless.

**Outfit 2: Edgy & Relaxed**
*   **Top:** Oversized grey crewneck sweatshirt 
*   **Shoes:** Black combat boots (lace-up)
*   **Accessories:** Brown leather belt and black crossbody bag
*   *Why it works:* Tucking the front of the oversized grey crewneck into the 501s (secured with your brown leather belt) creates a cool, slouchy proportion. Pairing the medium-blue denim with the mid-ankle combat boots gives off an easy, grunge-inspired vintage aesthetic.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

I am still hyperventilating over these vintage Levi's 501 jeans because they fit like an absolute dream! Scoring the ultimate medium wash on depop for just $38.00 feels like highway robbery in the best way possible. I'm already planning to live in them this fall with crisp white sneakers for that effortlessly cool, off-duty model vibe.
```

**Verifying `create_fit_card` actually varies**

Running that same command three times in a row gave the identical string above each time — that's `CACHE_ENABLED` (`config.py`), which reuses the answer to an identical prompt while building, not a bug in the tool. Re-running with `AI201_CACHE=0` to bypass the cache confirms `TEMPERATURE=0.9` produces real variation:

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; [print(create_fit_card('jeans and white sneakers', load_listings()[0]), '\n---') for _ in range(3)]"

I am still not over the absolute luck of scoring these vintage Levi's 501 jeans for just $38.00 on Depop! The medium wash has that perfectly broken-in, effortless 90s aesthetic that you just can't manufacture. Throwing them on with some fresh white sneakers for the ultimate off-duty casual look.
---
I still can't believe I found these dream vintage Levi's 501 jeans on Depop for just $38. The medium wash has that perfectly broken-in, effortless 90s slouch that you literally cannot fake. Just threw them on with crisp white sneakers for the ultimate casual-cool weekend vibe.
---
I am literally losing my mind over these vintage Levi's 501 jeans I just scored on Depop for $38! The medium wash has that perfectly broken-in, effortless 90s slouch that you just can't fake. Throwing them on with crisp white sneakers for that ultimate effortlessly cool weekend uniform. ✨
---
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* After wiring up the loop, I asked Claude to create a test file so I could see exactly what was being checked and the actual results, rather than just taking its word for it.
- *What came back:* A verification script (`check_agent.py`) checking the tools and loop against the README's own claims — including that `create_fit_card` mentions the item's price. That check looked for `str(item["price"])` (`"38.0"`) or `f"${price:.2f}"` (`"$38.00"`) inside the caption. Running it came back 24/25 passed — the one failure was a real fit card that wrote the price as `"$38"`, which matched neither string.
- *What I changed:* Had the price check loosened to `str(int(item["price"])) in card` — matching just the digits instead of a specific formatting. The tool was fine; the check's assumption about how the model would phrase the price wasn't.

**Moment 2**

- *What I asked for:* After wiring up the loop, I told Claude "I don't think it's able to pick up the $30 in `run_agent`" — my test of `'vintage graphic tee under $30'` looked like it wasn't parsing the price.
- *What came back:* It ran `_parse_query` directly in bash and got the correct result (`max_price: 30.0`), then re-ran my exact PowerShell command and reproduced the failure — PowerShell was interpolating `$30` as an (empty) variable inside the double-quoted `-c` string before Python ever saw it, so the regex had nothing to match.
- *What I changed:* Nothing in `agent.py` — the parsing code was already correct. I changed how I tested it (single-quoting the query / using `python app.py ask '...'` instead of a `-c` one-liner), and now know to be careful with `$` in PowerShell when testing.

**Moment 3**

- *What I asked for:* For the MCP move, I asked Claude to register `search_listings` in `mcp_server.py` with the same contract as the direct-call version (size/price filtering rule, empty-list-on-no-match), and rewire `agent.py::run_agent` to call it through `mcp_client.call_tool("search_listings", {...})` instead of importing `tools.search_listings` directly.
- *What came back:* It filled in the commented-out `@mcp.tool()` stub with a docstring restating the size-match, price-ceiling, and empty-list rules, and swapped the direct call in `agent.py` for the `call_tool(...)` version. It worked on the first attempt — no exceptions, no missing fields.
- *What I changed:* Nothing in the code. Rather than take "it ran without erroring" as proof, I ran `python app.py ask 'vintage graphic tee under $30' --trace` before and after the move and diffed the two traces: the 10-item result list was identical, just relabeled `search_listings (via MCP)` instead of a direct call. That comparison, not the absence of an error, is what I'm actually trusting as evidence the rewire didn't change behavior.

**Moment 4**

- *What I asked for:* After my first three trials, I asked Claude to diagnose the misses for criteria 4 and 5.
- *What came back:* A diagnosis built on the log rather than guesses: it counted the model calls in the 60 seconds before each slow run, and timed the `google.genai` import separately. The first count it wrote into the README was wrong in three places (25 slow runs with 14 or more calls instead of 26, 13 slow runs at exactly 14 calls instead of 14, and 8 unexplained runs instead of 7).
- *What I changed:* Claude recomputed the counts from the log with a script before I committed, and corrected all three. I'm trusting the corrected numbers and not the first draft, and the README says where the diagnosis is inferred from timestamps rather than observed.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item["id"]` matches the `new_item["id"]` `suggest_outfit` receives | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Every fit card mentions the item's price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe still returns non-empty styling advice through to a fit card | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Full output for all 25 tries (5 scenarios × 5 tries) is in
[`results/run_2026-09-27_2004_before.md`](results/run_2026-09-27_2004_before.md),
produced by `python run_eval.py --label before` with caching off.

**Real output for each criterion**, pasted as text, naming the file and
function that produced it.

**Criterion 1** — `run_eval.py::run_once` → `agent.py::run_agent`, scenario
`"matching query completes"`, try 1:

```
[1] _parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two outfit ideas using the new Y2K Butterfly Baby Tee and pieces from your existing wardrobe:  **Outf…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I literally screamed when I found this Y2K butterfly baby tee on Depop for just $18! The little rhinestone gra…

selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
fit_card: I literally screamed when I found this Y2K butterfly baby tee on Depop for just $18! The little rhinestone graphics give it the ultimate early-2000s mall-rat energy. I can't wait to style the fitted, cropped silhouette with some baggy dark-wash jeans for that effortless off-duty look.
```

**Criterion 2** — `run_eval.py::run_once` → `agent.py::run_agent`, scenario
`"impossible query stops early"`, try 1:

```
[1] _parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    search_results empty — stopping before suggest_outfit

stopped early: yes — No listings matched that search. Try loosening the price ceiling, dropping the size filter, or using different keywords in the description.
```

**Criterion 3** — `check_agent.py` → `agent.py::run_agent`, try 1 (of the 5
`check_agent.py`'s Criterion 3 section runs): it patches `agent.suggest_outfit`
with a spy so the `new_item` dict `run_agent` actually passes in is captured
independently of the session dict. A spy at the call boundary, on purpose,
rather than adding the id to `agent.py`'s existing trace line; see the
comment above that section in `check_agent.py` for why a trace line alone
wouldn't have been strong enough evidence:

```
  try 1: selected_item.id='lst_002'  id suggest_outfit received='lst_002'
  [PASS] try 1: id suggest_outfit received matches selected_item
```

**Criterion 4** — `run_eval.py::run_once` → `agent.py::run_agent`, scenario
`"fit card mentions price and platform"`, try 1:

```
Try 1: I am literally losing my mind over this Y2K butterfly baby tee I just scored on Depop for only $18! It has the absolute best nostalgic, early-2000s mall-goth energy, especially paired with baggy denim or wide-leg trousers. I already have a million outfits planned in my head! 🦋✨
```

**Criterion 5** — `run_eval.py::run_once` → `agent.py::run_agent`, scenario
`"empty wardrobe still returns styling advice"`, try 1:

```
selected_item: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)

outfit_suggestion (first 2 lines):
A light-wash, cropped Wrangler denim jacket is a fantastic vintage-leaning staple that adds an instant cool-girl edge to any outfit. Since it's cropped, it naturally accentuates the waist and pairs best with high-waisted bottoms, balancing proportions effortlessly.

fit_card: I am still not over scoring this dreamy light-wash cropped Wrangler jacket on Poshmark for just $42! It has that ultimate 90s off-duty model vibe that instantly makes any high-waisted pant or slip dress look ten times cooler. I seriously cannot wait to live in this all season long!
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools and returns a fit card | 4 of 5 | MET (5/5) | All 5 tries in `results/run_2026-09-27_2004_before.md` show `stopped early: no`, a trace hitting `search_listings` → `suggest_outfit` → `create_fit_card`, and a non-empty fit card. 5 passes clears the 4-of-5 bar. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET (5/5) | All 5 tries show `stopped early: yes`, with the trace ending at `[3] branch → search_results empty — stopping before suggest_outfit`. `suggest_outfit` and `create_fit_card` never appear in any of the 5 traces. |
| 3 | `session["selected_item"]["id"]` equals the `id` of the `new_item` dict `suggest_outfit` actually receives | 5 of 5 | MET (5/5) | `check_agent.py`'s Criterion 3 section patches `agent.suggest_outfit` with a spy that records the real `new_item` argument at the call boundary, then runs `run_agent` 5 times. All 5 tries print `selected_item.id='lst_002'` next to `id suggest_outfit received='lst_002'` and a `[PASS]` verdict. |
| 4 | Every fit card mentions the item's price and platform | 5 of 5 | MET (5/5) | Read all 5 fit-card strings for the same item (`$18.0`, depop) plainly: each of the 5 contains "$18" and "Depop" somewhere in the text, with only the surrounding wording varying. |
| 5 | Empty wardrobe still returns non-empty styling advice through to a fit card | 5 of 5 | MET (5/5) | All 5 empty-wardrobe tries show `stopped early: no`, a non-empty `outfit_suggestion` that gives general advice and names zero wardrobe items (correct, since there are none), and a non-empty fit card. |

**Diagnoses**

No misses this round: all five held at or above their targets, so there's no tool/branch/session/model mechanism to trace down. That's a real result, not a reason to stop reading it critically. The more useful question is whether any target was too easy to fail, and one was.

Criterion 1's `4 of 5` target exists specifically because `search_listings` is a plain keyword-overlap match with no fuzzy matching, so differently-worded queries for the same intent can score zero. But the eval reruns the *exact same string* (`"vintage graphic tee under $30"`) five times. `search_listings` is deterministic (same input, same output, every time), so there was never a way for this run to land anywhere except 0/5 or 5/5. The 20% of slack the target was built to absorb was never actually exercisable; getting 5/5 here confirms the loop and the tool work, but it doesn't tell me anything about the wording-brittleness risk the target names. **This is the criterion I'd tighten**, not by lowering the number, but by changing what gets run: 5 *different* phrasings of a matching intent (e.g. `"vintage graphic tee under $30"`, `"90s band shirt cheap"`, `"graphic tee, budget"`) instead of one phrasing repeated 5 times. That would let a real partial miss show up if one is actually there.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace

[1] _parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two outfit ideas using the new Y2K Butterfly Baby Tee and pieces from your existing wardrobe:  **Outf…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am losing my mind over this thrift find—I just scored the cutest Y2K Butterfly Baby Tee on Depop for only $1…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two outfit ideas using the new Y2K Butterfly Baby Tee and pieces from your existing wardrobe:

**Outfit 1: Casual Y2K Streetwear**
*   **Top:** Y2K Baby Tee (Butterfly Print)
*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   **Why it works:** The tight, fitted silhouette of the baby tee creates a great Y2K-inspired proportion balance when paired with your baggy, dark wash jeans. Add the chunky white sneakers and black crossbody bag to complete an effortless, everyday throwback look.

**Outfit 2: Edgy Contrast**
*   **Top:** Y2K Baby Tee (Butterfly Print)
*   **Bottoms:** Wide-leg khaki trousers
*   **Outerwear:** Vintage black denim jacket (slightly cropped)
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt
*   **Why it works:** Pairing the feminine, pink-and-purple butterfly print with your structured wide-leg khakis and chunky black combat boots creates a cool contrast between soft and edgy. Tucking the baby tee in with the brown leather belt and layering the slightly cropped denim jacket on top ties the whole outfit together.

  Fit card: I am losing my mind over this thrift find—I just scored the cutest Y2K Butterfly Baby Tee on Depop for only $18, and it’s literal perfection! The pink-and-purple print gives off major 2000s pop-star energy, whether you want to style it with baggy jeans for effortless streetwear or toughen it up with combat boots. Honestly, my inner child is screaming, and I can't wait to wear this everywhere. 🦋✨

0 model calls this session, 2 served from cache
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace

[1] _parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    search_results empty — stopping before suggest_outfit

  No listings matched that search. Try loosening the price ceiling, dropping the size filter, or using different keywords in the description.

0 model calls this session
```

The empty-search trace is three steps against the happy path's four: it stops right after `search_listings` sees nothing, instead of going on to `suggest_outfit` and `create_fit_card`.

**On the MCP move:** `search_listings` is registered in `mcp_server.py` under its own name, with a docstring stating the size-match rule, the price ceiling, and the empty-list return, the same contract as the Tool Inventory above. `agent.py::run_agent` calls it through `mcp_client.call_tool("search_listings", {...})` instead of importing `tools.search_listings` directly. The rewire worked on the first attempt; the trace line `search_listings (via MCP)` above is the same 10-item result the direct call used to return, so nothing about the tool's behavior changed, only how it's reached.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** `scenarios.py`'s criterion-1 scenario ("matching query completes") no longer reruns the single string `"vintage graphic tee under $30"` five times. It now carries a `"queries"` list of five *different* phrasings of the same shopping intent, a fun/vintage graphic top under $30, and `run_eval.py::_query_for` feeds a different one of the five to `run_agent` on each try (`run_eval.py::main`'s loop calls `_query_for(scenario, attempt)` instead of reading a fixed `scenario["query"]`). The five phrasings: `"vintage graphic tee under $30"`, `"band tee under $30"`, `"y2k baby tee under $30"`, `"funky throwback top under $30"`, `"quirky retro novelty find under $30"`. Before picking them, I ran each one directly against `tools.py::search_listings` to confirm what it would actually do, rather than guessing, and the last one measured out to a genuine `0` results.

**Which failure it was meant to fix:** Not a bug, a broken *test*. The diagnosis above, under "Verdicts and Diagnoses," pointed out that criterion 1's "4 of 5" target exists specifically to absorb wording misses from `search_listings`'s plain keyword-overlap matching, but the "before" scenario reran the exact same string five times against a deterministic function, so it could only ever land on 0/5 or 5/5, never actually landing a partial miss even if the underlying risk was real. Changing *what gets run*, not the tool or the loop, was the fix the diagnosis named.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | FAIL | MET (4/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item["id"]` matches the `new_item["id"]` `suggest_outfit` receives | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Every fit card mentions the item's price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe still returns non-empty styling advice through to a fit card | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Full output for all 25 tries is in
[`results/run_2026-09-28_1936_after.md`](results/run_2026-09-28_1936_after.md),
produced by `python run_eval.py --label after` with caching off.

**Real output for the criterion this change touched**, pasted as text
(console output of `run_eval.py::main`, calling `agent.py::run_agent` through
`run_eval.py::run_once`), scenario `"matching query completes"`, all 5 tries,
one phrasing each:

```
matching query completes  (example wardrobe)
  queries (one per try): ['vintage graphic tee under $30', 'band tee under $30', 'y2k baby tee under $30', 'funky throwback top under $30', 'quirky retro novelty find under $30']
[1] _parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two outfit ideas that pair the Y2K Butterfly Baby Tee with pieces from your existing wardrobe:  **Out…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am still screaming over this Y2K butterfly baby tee I just scored on Depop for only $18. The pink-and-purple…
  try 1: completed — fit card 340 chars
[1] _parse_query
      in:  band tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 5 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Y2K Baby Tee — Butterfly Print … +2 more
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two ways to style the new 2003 Tour Bootleg Graphic Tee using pieces already in your wardrobe:  ### O…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am still screaming over this 2003 tour bootleg graphic tee I just scored on Depop for $24! The fade on it is…
  try 2: completed — fit card 305 chars
[1] _parse_query
      in:  y2k baby tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 6 items: Y2K Baby Tee — Butterfly Print, Low-Rise Cargo Pants — Khaki, Mesh Long-Sleeve Top — Black … +3 more
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two outfit ideas that pair the Y2K Butterfly Baby Tee with pieces from your existing wardrobe:  **Out…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am still not over this Y2K butterfly baby tee I just scored on Depop for $18! The graphic print gives the ab…
  try 3: completed — fit card 304 chars
[1] _parse_query
      in:  funky throwback top under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 3 items: Mesh Long-Sleeve Top — Black, Crochet Halter Top — Cream, Low-Top Canvas Sneakers — Off-White
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two ways to style the new mesh long-sleeve top using pieces from your current wardrobe:  **Outfit 1: …
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am still screaming over finding this black mesh long-sleeve top on Depop for only $15! It adds the absolute …
  try 4: completed — fit card 327 chars
[1] _parse_query
      in:  quirky retro novelty find under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    search_results empty — stopping before suggest_outfit
  try 5: stopped early — No listings matched that search. Try loosening the price cei
```

Criteria 2, 3, 4, and 5 didn't change, same scenarios, same code paths as
"before", and came back 5/5 again, confirming the rewire didn't disturb
anything else. (Criterion 3 reconfirmed separately via `check_agent.py`'s
spy, same method as the "before" run.)

**Did it help, and how do I know:** Yes, but not by raising the pass count,
it made the number *mean something*. "Before," criterion 1 was 5/5 against a
target of 4/5, and the diagnosis called that result untrustworthy: the same
deterministic string run five times could only ever produce 0/5 or 5/5, so
5/5 didn't tell me whether the 20% slack in my own target was real or just
never exercised. "After," with five genuinely different phrasings of the
same shopping intent, one of them (`"quirky retro novelty find under $30"`)
measured out to zero results and the loop correctly stopped early instead of
crashing or hallucinating a match, landing at 4/5, exactly on the target
instead of padded above it. That's a more honest number: it shows the
4-of-5 target is real (a genuine miss is reachable) and that my loop's
branch handles that miss correctly when it happens, which the "before" run
could never have shown no matter how many times it reran.



---

## What's Still Broken

Nothing missed its target this round, criterion 1 landed exactly on 4/5,
the others held at 5/5. But "exactly on target" for criterion 1 is worth
being honest about rather than treating as a clean pass: `search_listings`
still has no fuzzy matching or synonym handling, so `"quirky retro novelty
find"`, a phrasing a real user might type for the same item, returns
nothing and the agent's only recourse is to tell the user to reword. A
better search (stemming, a synonym table, or embedding-based matching
instead of raw token overlap) would turn some of these misses into hits.
I didn't build that this round because it's a bigger change than "fix one
thing" calls for, and criterion 1's target already accounts for this class
of miss rather than promising it away, but it's the next thing I'd improve
if I kept going.

---

<!-- ═══════════════════════ UNIT 9 — DEPLOY AND INSTRUMENT ═══════════════════════ -->

## What This Extends

This extends **FitFindr**, the secondhand-shopping agent from units 3 and 4
(`agent.py::run_agent`, with `search_listings` called through MCP). The agent
itself is unchanged. What's new is the operational layer in
[serve.py](serve.py): one structured log line per request (including failures
and rejected input), timing split into queue wait and run time, token counts,
input validation, and the scripts that exercise it (`send_requests.py`,
`measure_cost.py`, `run_criteria.py`).

## The Shape

**System:** FitFindr, the agent from units 3–4 (`agent.py::run_agent`, with
`search_listings` moved onto MCP), unchanged.

**Shape: A — Deploy and instrument.** FitFindr currently only runs as a
one-shot CLI command on my laptop, and [serve.py](serve.py) ships with no
logging, no timing and no request counting. I'm adding the operational layer
around the existing `run_agent()`: one structured log line per `POST /ask`
request (timestamp, query, outcome, `error` if any, and wall-clock duration
split out from time spent waiting on the one-at-a-time lock), written to a
file I commit from a real session of several requests, plus a single
documented start command in RUNNING.md tested from a clean checkout. The
claim I'll make at the end is a measured one: here is how long a request
actually takes, and the log proves it ran more than once.

**Path:** B — local with logs. The agent spawns an MCP subprocess per call,
which is already tight against the free tier's 512 MB, and Path B scores the
same.

**Out of scope** — things I considered and am not doing:

- **No changes to the agent or its tools.** No new search logic, no fuzzy or
  synonym matching (the thing "What's Still Broken" says I'd improve next),
  no new tool. Shape A is about observing the system I have, and changing it
  mid-measurement would make the numbers meaningless.
- **No concurrency.** I'm keeping the one-request-at-a-time lock. A real
  queue or async workers would break `mcp_client.call_tool`'s `asyncio.run()`
  anyway, and it's a different project.
- **No hosted deployment or frontend.** No signup, no card, no UI beyond
  `curl` against `/ask`.

**Size check:** two pieces of building — the log line in `serve.py`, and
`RUNNING.md` plus the committed run record. Well under ninety minutes.



## Running It

Path B, local with logs. The full instructions are in
[RUNNING.md](RUNNING.md), under "Run it locally with logging". In short, with
Python 3.11–3.13 (tested on 3.12.10), the pinned packages from
`requirements.txt`, and `GEMINI_API_KEY` in `.env`:

```powershell
$env:AI201_CACHE = "0"
python serve.py
```

then `python send_requests.py` in a second terminal. There are no model files:
the model is called over the API, so nothing is downloaded beyond the
packages. I followed these instructions from a fresh clone in a separate
folder before running the trials.

## Instrumentation

`serve.py` appends one JSON object per `POST /ask` to
`results/serve_log.jsonl`, including requests that fail. Fields: `ts` (UTC),
`outcome` (`ok`, `no_results`, `agent_error`, `crash`, `bad_request`), `http`,
`query`, `error`, `wait_s` (queued behind another request), `run_s` (inside
`run_agent()`), `model_calls` and `tokens` (both read from `generate.py`'s
counters as before/after deltas). The log below is the full file from one
session with the cache off (`AI201_CACHE=0`), pasted as written. Lines 1–8 are
a session with a deliberately bad API key, followed by the normal run
(`send_requests.py`, then `measure_cost.py`). In this session a bad request
logged only the fields it had, so it carries no timing; the fix described under
"Unit 9 — The Improvement" made every record carry all nine fields.

```jsonl
{"ts": "2026-10-26T00:03:52+00:00", "outcome": "agent_error", "http": 200, "query": "vintage graphic tee under $30", "error": "The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "wait_s": 0.0, "run_s": 3.992, "model_calls": 1, "tokens": 0}
{"ts": "2026-10-26T00:03:55+00:00", "outcome": "agent_error", "http": 200, "query": "denim jacket under $40", "error": "The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "wait_s": 0.0, "run_s": 1.086, "model_calls": 1, "tokens": 0}
{"ts": "2026-10-26T00:03:59+00:00", "outcome": "agent_error", "http": 200, "query": "vintage graphic tee size M under $30", "error": "The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "wait_s": 0.0, "run_s": 1.125, "model_calls": 1, "tokens": 0}
{"ts": "2026-10-26T00:04:02+00:00", "outcome": "no_results", "http": 200, "query": "black combat boots size 9", "error": "No listings matched that search. Try loosening the price ceiling, dropping the size filter, or using different keywords in the description.", "wait_s": 0.0, "run_s": 0.966, "model_calls": 0, "tokens": 0}
{"ts": "2026-10-26T00:04:05+00:00", "outcome": "no_results", "http": 200, "query": "xyzzy plugh under $5", "error": "No listings matched that search. Try loosening the price ceiling, dropping the size filter, or using different keywords in the description.", "wait_s": 0.0, "run_s": 1.152, "model_calls": 0, "tokens": 0}
{"ts": "2026-10-26T00:04:07+00:00", "outcome": "bad_request", "http": 400, "query": null}
{"ts": "2026-10-26T00:04:10+00:00", "outcome": "agent_error", "http": 200, "query": "y2k baby tee under $25", "error": "The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "wait_s": 0.0, "run_s": 1.234, "model_calls": 1, "tokens": 0}
{"ts": "2026-10-26T00:04:11+00:00", "outcome": "agent_error", "http": 200, "query": "oversized flannel under $35", "error": "The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "wait_s": 1.22, "run_s": 1.071, "model_calls": 1, "tokens": 0}
{"ts": "2026-10-26T00:04:47+00:00", "outcome": "ok", "http": 200, "query": "vintage graphic tee under $30", "error": null, "wait_s": 0.0, "run_s": 5.257, "model_calls": 2, "tokens": 951}
{"ts": "2026-10-26T00:04:52+00:00", "outcome": "ok", "http": 200, "query": "denim jacket under $40", "error": null, "wait_s": 0.0, "run_s": 3.259, "model_calls": 2, "tokens": 1124}
{"ts": "2026-10-26T00:04:58+00:00", "outcome": "ok", "http": 200, "query": "vintage graphic tee size M under $30", "error": null, "wait_s": 0.0, "run_s": 3.099, "model_calls": 2, "tokens": 960}
{"ts": "2026-10-26T00:05:01+00:00", "outcome": "no_results", "http": 200, "query": "black combat boots size 9", "error": "No listings matched that search. Try loosening the price ceiling, dropping the size filter, or using different keywords in the description.", "wait_s": 0.0, "run_s": 0.973, "model_calls": 0, "tokens": 0}
{"ts": "2026-10-26T00:05:04+00:00", "outcome": "no_results", "http": 200, "query": "xyzzy plugh under $5", "error": "No listings matched that search. Try loosening the price ceiling, dropping the size filter, or using different keywords in the description.", "wait_s": 0.0, "run_s": 1.0, "model_calls": 0, "tokens": 0}
{"ts": "2026-10-26T00:05:06+00:00", "outcome": "bad_request", "http": 400, "query": null}
{"ts": "2026-10-26T00:05:11+00:00", "outcome": "ok", "http": 200, "query": "oversized flannel under $35", "error": null, "wait_s": 0.0, "run_s": 3.687, "model_calls": 2, "tokens": 1049}
{"ts": "2026-10-26T00:05:16+00:00", "outcome": "ok", "http": 200, "query": "y2k baby tee under $25", "error": null, "wait_s": 3.672, "run_s": 4.448, "model_calls": 2, "tokens": 972}
{"ts": "2026-10-26T00:05:35+00:00", "outcome": "ok", "http": 200, "query": "vintage graphic tee under $30", "error": null, "wait_s": 0.0, "run_s": 4.695, "model_calls": 2, "tokens": 782}
{"ts": "2026-10-26T00:05:40+00:00", "outcome": "ok", "http": 200, "query": "denim jacket under $40", "error": null, "wait_s": 0.0, "run_s": 3.621, "model_calls": 2, "tokens": 854}
{"ts": "2026-10-26T00:05:47+00:00", "outcome": "ok", "http": 200, "query": "y2k baby tee under $25", "error": null, "wait_s": 0.0, "run_s": 4.385, "model_calls": 2, "tokens": 949}
{"ts": "2026-10-26T00:05:52+00:00", "outcome": "ok", "http": 200, "query": "oversized flannel under $35", "error": null, "wait_s": 0.0, "run_s": 3.728, "model_calls": 2, "tokens": 983}
{"ts": "2026-10-26T00:05:59+00:00", "outcome": "ok", "http": 200, "query": "vintage graphic tee size M under $30", "error": null, "wait_s": 0.0, "run_s": 4.087, "model_calls": 2, "tokens": 990}
{"ts": "2026-10-26T00:06:10+00:00", "outcome": "ok", "http": 200, "query": "black leather jacket under $60", "error": null, "wait_s": 0.0, "run_s": 9.524, "model_calls": 2, "tokens": 937}
{"ts": "2026-10-26T00:06:17+00:00", "outcome": "ok", "http": 200, "query": "cargo pants under $40", "error": null, "wait_s": 0.0, "run_s": 4.544, "model_calls": 2, "tokens": 881}
{"ts": "2026-10-26T00:06:34+00:00", "outcome": "ok", "http": 200, "query": "floral sundress under $30", "error": null, "wait_s": 0.0, "run_s": 14.835, "model_calls": 2, "tokens": 862}
{"ts": "2026-10-26T00:06:40+00:00", "outcome": "ok", "http": 200, "query": "chunky sneakers under $50", "error": null, "wait_s": 0.0, "run_s": 4.483, "model_calls": 2, "tokens": 1044}
{"ts": "2026-10-26T00:06:46+00:00", "outcome": "ok", "http": 200, "query": "knit sweater under $35", "error": null, "wait_s": 0.0, "run_s": 3.697, "model_calls": 2, "tokens": 815}
```

What the log shows:

- **Failures leave records.** Five requests ran with a bad key and logged
  `agent_error` with the key message, `model_calls: 1` and `tokens: 0`. A
  failed model call still cost 1.1–4.0 s of `run_s`.
- **No-match queries are cheap.** `no_results` runs make no model calls and
  take about 1 s (`run_s` 0.97–1.15).
- **Queueing is visible.** In the two-at-once pair, the second request logged
  `wait_s: 3.672` behind a 3.687 s run. The wait matches the run ahead of it.

---

## What It Costs

**One successful run (a query that matches, through `search_listings`,
`suggest_outfit` and `create_fit_card`): about 910 tokens, 2 model calls and
5.8 s on average.** There is no dollar figure, because the model is on a free
tier with nothing billed.

**How I measured it.** `measure_cost.py` sent ten different queries that each
match a listing to a running `serve.py` (cache off, so every answer is a real
call), and averaged the last ten `ok` lines of the log. `tokens` is the
change in `generate.token_counts()["total"]` (prompt plus output tokens, as
reported by the service) across each request; `run_s` is wall-clock time
inside the request lock, via `time.perf_counter()`; `model_calls` is the change
in `generate.call_count()`.

| | mean | median | min | max |
|---|---|---|---|---|
| `run_s` (seconds) | 5.76 | 4.43 | 3.62 | 14.84 |
| `tokens` | 909.7 | 909.0 | 782 | 1044 |
| `model_calls` | 2 | 2 | 2 | 2 |

The mean of `run_s` is pulled up by two slow runs (9.52 s for the leather
jacket query and 14.84 s for the sundress); eight of the ten finished in
3.6–4.7 s, so the median of 4.43 s is the better figure for a typical run. I
haven't found what made those two slow. `tokens` is steady, so those runs
weren't longer answers. These are warm numbers with the server already
running, and they come from one machine and one session.

**For a hundred people a day.** I'm assuming each person makes 5 matching
requests a day; that's a guess about usage, not something I measured.

- Runs: 100 people × 5 runs = **500 runs a day**.
- Tokens: 500 runs × 909.7 tokens = **454,850 tokens a day** (about 13.6
  million over a 30-day month).
- Model calls: 500 runs × 2 calls = 1,000 calls a day, against a limit of
  15 per minute, which is 21,600 a day if spread out evenly.
- Compute: 500 runs × 5.76 s mean = 2,880 s, about **48 minutes of serial
  run time a day** (about 37 minutes at the 4.43 s median). The server runs
  one request at a time, so that's the time it would be busy.
- Dollars: the token counter logs prompt and output tokens as one total, so I
  can only bound the price. Third-party pricing sites list `gemini-3.5-flash-lite`
  at $0.30 per million input tokens and $2.50 per million output tokens
  ([example](https://www.getmaxim.ai/bifrost/llm-cost-calculator/provider/opencode-zen/model/gemini-3.5-flash-lite));
  I haven't checked Google's own page. If every token were input,
  0.45485 M × $0.30 = **$0.14 a day**; if every token were output,
  0.45485 M × $2.50 = **$1.14 a day**. The real figure sits between them,
  closer to the lower end if prompts dominate, so roughly **$4 to $34 a
  month**.

So the arithmetic says cost isn't the constraint at this size: about a dollar
a day at the most. The constraint is the 15-calls-per-minute limit, because
a burst of 8 people at once would trigger the pacing sleep I diagnosed
earlier, not the budget.

---

## Run Log — Unit 9

Three trials of each criterion, nothing changed between them, cache off
(`AI201_CACHE=0`). Each trial used a fresh `serve.py`: one with the real key
for criteria 1, 2, 3 and 5, and one started with `GEMINI_API_KEY=bad-key` for
criterion 4. Everything ran through `run_criteria.py`, which writes
`results/unit9_run<N>.txt` and `results/unit9_run<N>_badkey.txt`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Malformed input never causes a 500 | 9 of 10 | 6/10 | 6/10 | 6/10 | MISSED |
| 2. Every request leaves one log record with the same nine fields | 20 of 20 | 0/20 | 0/20 | 0/20 | MISSED |
| 3. A queued request's `wait_s` matches the run ahead of it | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. A bad-key run fails in 5.0 s or less | 5 of 5 | 4/5 | 5/5 | 4/5 | MISSED |
| 5. Matching requests: 8 of 10 at `run_s` ≤ 5.0 s, none above 20 s | 8 of 10 | 7/10 | 6/10 | 7/10 | MISSED |

How the scores were counted:

- **Criterion 2** scores 0/20 whenever the log doesn't gain exactly 20 lines.
  All three runs gained 16 lines, 11 of them with all nine fields. The 5
  `bad_request` lines were each missing five fields, and 4 requests left no
  line at all.
- **Criterion 5** counts runs with `outcome: ok` and `run_s` ≤ 5.0 s. Run 1's
  slowest run was 21.8 s, so it also breaks the 20 s cap; the other two stayed
  under it (12.2 s and 19.8 s).
- **Criterion 4**'s misses were all the first request on a fresh server (5.155
  s in run 1, 5.19 s in run 3). Run 2's first request took 4.97 s.
- **Criterion 3** passed with a difference of 0.018 s or less in all 15 pairs,
  including pairs where the first run took 19.5 s and 21.3 s.

Output from run 1, pasted from the saved files. The requests are sent by
`run_criteria.py`; the HTTP responses come from `serve.py::ask`, and the log
lines are written by `serve.py::_log`.

**Criterion 1** (`results/unit9_run1.txt`, from `serve.py::ask`):

```
== Criterion 1: malformed input never causes a 500 ==
  PASS  not JSON               status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  FAIL  JSON list              status=500  'None'
  FAIL  JSON string            status=500  'None'
  FAIL  query is a number      status=500  'None'
  PASS  query is null          status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is empty         status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is whitespace    status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  FAIL  query is a list        status=500  'None'
  PASS  wardrobe only          status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  5000-char query        status=200  'None'
  Criterion 1 score: 6/10  (target 9 of 10)
```

**Criterion 2** (`results/unit9_run1.txt`, from `serve.py::_log`):

```
== Criterion 2: one log record per request, same nine fields ==
  FAIL  line 0: outcome=bad_request fields differ: missing=['error', 'model_calls', 'run_s', 'tokens', 'wait_s'] extra=[]
  FAIL  line 1: outcome=bad_request fields differ: missing=['error', 'model_calls', 'run_s', 'tokens', 'wait_s'] extra=[]
  FAIL  line 2: outcome=bad_request fields differ: missing=['error', 'model_calls', 'run_s', 'tokens', 'wait_s'] extra=[]
  FAIL  line 3: outcome=bad_request fields differ: missing=['error', 'model_calls', 'run_s', 'tokens', 'wait_s'] extra=[]
  FAIL  line 4: outcome=bad_request fields differ: missing=['error', 'model_calls', 'run_s', 'tokens', 'wait_s'] extra=[]
  Log gained 16 lines (expected 20); 11 valid.
  Criterion 2 score: 0/20  (target 20 of 20, exactly 20 new lines)
```

**Criterion 3** (`results/unit9_run1.txt`, from `serve.py::ask`'s lock and `_log`):

```
== Criterion 3: queued request's wait_s matches the run ahead of it ==
  PASS  pair 1: first run_s=3.512  second wait_s=3.499  diff=0.013
  PASS  pair 2: first run_s=3.87  second wait_s=3.87  diff=0.000
  PASS  pair 3: first run_s=21.258  second wait_s=21.258  diff=0.000
  PASS  pair 4: first run_s=4.058  second wait_s=4.043  diff=0.015
  PASS  pair 5: first run_s=3.772  second wait_s=3.772  diff=0.000
  Criterion 3 score: 5/5  (target 5 of 5)
```

**Criterion 4** (`results/unit9_run1_badkey.txt`, from `serve.py::ask` and
`agent.py::run_agent`):

```
== Criterion 4: bad API key fails in 5 s or less (server started with a bad key) ==
  FAIL  'vintage graphic tee under $30'            outcome=agent_error  run_s=5.155
  PASS  'denim jacket under $40'                   outcome=agent_error  run_s=1.524
  PASS  'y2k baby tee under $25'                   outcome=agent_error  run_s=1.546
  PASS  'oversized flannel under $35'              outcome=agent_error  run_s=1.451
  PASS  'vintage graphic tee size M under $30'     outcome=agent_error  run_s=1.726
  Criterion 4 score: 4/5  (target 5 of 5, first request included)
```

**Criterion 5** (`results/unit9_run1.txt`, from `serve.py::_log`):

```
== Criterion 5: matching requests run_s <= 5.0 s, none > 20 s ==
  PASS  'vintage graphic tee under $30'            outcome=ok         run_s=3.426 model_calls=2
  PASS  'denim jacket under $40'                   outcome=ok         run_s=4.701 model_calls=2
  PASS  'y2k baby tee under $25'                   outcome=ok         run_s=3.434 model_calls=2
  PASS  'oversized flannel under $35'              outcome=ok         run_s=3.883 model_calls=2
  PASS  'vintage graphic tee size M under $30'     outcome=ok         run_s=3.574 model_calls=2
  PASS  'black leather jacket under $60'           outcome=ok         run_s=3.444 model_calls=2
  FAIL  'cargo pants under $40'                    outcome=ok         run_s=21.828 model_calls=2
  PASS  'floral sundress under $30'                outcome=ok         run_s=3.541 model_calls=2
  PASS  'chunky sneakers under $50'                outcome=ok         run_s=4.545 model_calls=2
  PASS  'knit sweater under $35'                   outcome=ok         run_s=3.666 model_calls=2
  Slowest run_s: 21.828
  Criterion 5 score: 7/10  (target 8 of 10, none above 20 s)
```

---

## Unit 9 — Verdicts and Diagnoses

| Criterion | Target | Runs | Verdict |
|---|---|---|---|
| 1. Malformed input never causes a 500 | 9 of 10 | 6/10, 6/10, 6/10 | MISSED |
| 2. One log record per request, same nine fields | 20 of 20 | 0/20, 0/20, 0/20 | MISSED |
| 3. Queued `wait_s` matches the run ahead | 5 of 5 | 5/5, 5/5, 5/5 | MET |
| 4. Bad-key run fails in 5.0 s or less | 5 of 5 | 4/5, 5/5, 4/5 | MISSED |
| 5. 8 of 10 matching runs at 5.0 s or less, none above 20 s | 8 of 10 | 7/10, 6/10, 7/10 | MISSED |

Criterion 4 reached 5/5 once, but the target is every run, so it's a miss.

Two notes on how this was scored:

- **Criterion 1.** `criteria.md` says a malformed request should return "a
  4xx or a normal 200 with `session["error"]` set". `run_criteria.py` counts
  any status below 500 as a pass, so a 5,000-character query that gets a
  normal answer isn't scored as a failure. Under the stricter reading that
  query might not count, but the four failures that decide the verdict are
  all 500s, so the verdict is the same either way.
- **Order of work.** The criteria were committed (`add capstone criteria`)
  after the instrumentation and cost measurement already existed, so I knew the
  baseline timings when I set the targets; criterion 5's reason says so. They
  were committed before any of the test results (`add unit 9 test results`).

**Criteria 1 and 2: one stage, two symptoms.** The stage is the input path at
the top of `serve.py::ask`, before the agent runs. It did
`payload = request.get_json(silent=True) or {{}}` and then
`(payload.get("query") or "").strip()`, which assumes the body is a dict and
`query` is a string. A JSON list, a JSON string, `{{"query": 123}}` and
`{{"query": ["a"]}}` are valid JSON of the wrong shape, so `.get` or `.strip()`
raised `AttributeError`. That happens outside the `try` that wraps
`run_agent`, so Flask returned a bare 500 (criterion 1: 4 of 10 failed, the
same four every trial). The same four then left no log line, because `_log`
is only called after the checks pass: the log gained 16 lines for 20 requests.
Criterion 2 also has a second cause in the same function: the `bad_request`
branch called `_log(outcome="bad_request", http=400, query=None)`, so its five
lines were missing `error`, `wait_s`, `run_s`, `model_calls` and `tokens`.
Both are `ask()` assuming well-formed input.

**Criterion 4: first-request cost in `generate.py::_get_client`.** The misses
were all the first request on a freshly started server (5.155 s and 5.19 s,
with 4.97 s in the run that passed); the other four took 1.4–2.9 s. `_get_client`
does `from google import genai` lazily, on the first call, and that import
alone took 3.48 s when I timed it separately. The gap between the first
request and the rest is about the same size. The mechanism is that the
five-second limit left almost no room for a one-time import, so the target
sat on the edge and the cold start decided it. I couldn't separate this from
the first MCP subprocess starting, which also happens in that request.

**Criterion 5: pacing in `generate.py::_wait_for_slot`.** A matching run makes
two model calls, and `_wait_for_slot` sleeps whenever 15 calls have been made
in the last 60 seconds (`config.REQUESTS_PER_MINUTE`). Ten matching requests
sent back to back are 20 calls in under a minute, so the later ones wait for
the window to clear, and that sleep is counted in `run_s`. The criterion
assumed a run's cost doesn't depend on the runs before it, and it does. In the
81 `ok` runs in the log, 33 took over 5 s. Counting model calls in the 60
seconds before each run started, all 12 runs that started with 16 calls in the
window were slow, and 26 of the 33 slow runs started with 14 or more. I'm
inferring this from timestamps rather than from a log field, because the sleep
isn't recorded: `ts` has one-second resolution, and runs starting with 14
calls were mixed (14 slow, 22 fast), so it's not clean. Seven slow runs
started with fewer than 14 calls in the window and I haven't explained them.

**Pattern.** Two problems, not four:

- `serve.py::ask`'s input handling explains criteria 1 and 2.
- Time spent inside `generate.py` that `run_s` lumps together with real work
  (a one-time import, a rate-limit sleep) explains criteria 4 and 5. The log
  can't tell them apart from model latency, which is why I had to infer both.

Criterion 3 held in all 15 pairs and needs no diagnosis.

## Unit 9 — The Improvement

**One change: make `serve.py::ask` validate its input and log every
request the same way.** It's aimed at the first pattern, which covers two
criteria. In `serve.py`:

- `ask()` now accepts the payload only if it's a dict and reads `query` only
  if it's a string; anything else takes the existing 400 path.
- `_log()` now fills in all nine fields for every record, with zeros for the
  timing and counts of a request that never reached the agent, and the
  `bad_request` record carries its error message.

I didn't touch `generate.py`, so criteria 4 and 5 are not expected to change.
Fixing them would mean changing the pacing or the client setup, and I chose
the problem that covers the most criteria with the smallest change. A local
check with Flask's test client sent nine of the malformed inputs and got nine
400s and nine log lines with nine fields each, before any real re-run.

### Unit 9 — Run Log — After

The same three trials, run the same way (`run_criteria.py --label after1`,
`after2`, `after3`, with a fresh server for each part and the cache off), after
the change to `serve.py::ask` and `_log`. Nothing else was changed between the
two sets.

| Criterion | Target | Before (1 / 2 / 3) | After (1 / 2 / 3) | Verdict before | Verdict after |
|---|---|---|---|---|---|
| 1. Malformed input never causes a 500 | 9 of 10 | 6/10, 6/10, 6/10 | 10/10, 10/10, 10/10 | MISSED | MET |
| 2. One log record per request, same nine fields | 20 of 20 | 0/20, 0/20, 0/20 | 20/20, 20/20, 20/20 | MISSED | MET |
| 3. Queued `wait_s` matches the run ahead | 5 of 5 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 | MET | MET |
| 4. Bad-key run fails in 5.0 s or less | 5 of 5 | 4/5, 5/5, 4/5 | 4/5, 4/5, 4/5 | MISSED | MISSED |
| 5. 8 of 10 matching runs at 5.0 s or less, none above 20 s | 8 of 10 | 7/10, 6/10, 7/10 | 7/10, 7/10, 9/10 | MISSED | MISSED |

Output from after-run 1 (`results/unit9_after1.txt` and
`results/unit9_after1_badkey.txt`). The responses come from `serve.py::ask`
and the log lines from `serve.py::_log`.

**Criterion 1:**

```
== Criterion 1: malformed input never causes a 500 ==
  PASS  not JSON               status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  JSON list              status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  JSON string            status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is a number      status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is null          status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is empty         status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is whitespace    status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  query is a list        status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  wardrobe only          status=400  'Send JSON with a \'query\' field, e.g. {"query": "vintage graphic tee under $30"}'
  PASS  5000-char query        status=200  'None'
  Criterion 1 score: 10/10  (target 9 of 10)
```

**Criterion 2:**

```
== Criterion 2: one log record per request, same nine fields ==
  Log gained 20 lines (expected 20); 20 valid.
  Criterion 2 score: 20/20  (target 20 of 20, exactly 20 new lines)
```

**Criterion 3:**

```
== Criterion 3: queued request's wait_s matches the run ahead of it ==
  PASS  pair 1: first run_s=3.22  second wait_s=3.205  diff=0.015
  PASS  pair 2: first run_s=3.864  second wait_s=3.863  diff=0.001
  PASS  pair 3: first run_s=21.634  second wait_s=21.619  diff=0.015
  PASS  pair 4: first run_s=3.594  second wait_s=3.594  diff=0.000
  PASS  pair 5: first run_s=3.106  second wait_s=3.106  diff=0.000
  Criterion 3 score: 5/5  (target 5 of 5)
```

**Criterion 4:**

```
== Criterion 4: bad API key fails in 5 s or less (server started with a bad key) ==
  FAIL  'vintage graphic tee under $30'            outcome=agent_error  run_s=5.304
  PASS  'denim jacket under $40'                   outcome=agent_error  run_s=1.241
  PASS  'y2k baby tee under $25'                   outcome=agent_error  run_s=1.379
  PASS  'oversized flannel under $35'              outcome=agent_error  run_s=1.28
  PASS  'vintage graphic tee size M under $30'     outcome=agent_error  run_s=1.335
  Criterion 4 score: 4/5  (target 5 of 5, first request included)
```

**Criterion 5:**

```
== Criterion 5: matching requests run_s <= 5.0 s, none > 20 s ==
  PASS  'vintage graphic tee under $30'            outcome=ok         run_s=3.236 model_calls=2
  PASS  'denim jacket under $40'                   outcome=ok         run_s=3.615 model_calls=2
  PASS  'y2k baby tee under $25'                   outcome=ok         run_s=3.201 model_calls=2
  PASS  'oversized flannel under $35'              outcome=ok         run_s=3.262 model_calls=2
  PASS  'vintage graphic tee size M under $30'     outcome=ok         run_s=3.941 model_calls=2
  FAIL  'black leather jacket under $60'           outcome=ok         run_s=5.531 model_calls=2
  FAIL  'cargo pants under $40'                    outcome=ok         run_s=21.667 model_calls=2
  PASS  'floral sundress under $30'                outcome=ok         run_s=2.96 model_calls=2
  PASS  'chunky sneakers under $50'                outcome=ok         run_s=3.45 model_calls=2
  PASS  'knit sweater under $35'                   outcome=ok         run_s=3.646 model_calls=2
  Slowest run_s: 21.667
  Criterion 5 score: 7/10  (target 8 of 10, none above 20 s)
```

**Did it help?** Yes, for the two criteria it was aimed at. The four inputs
that returned a 500 in every earlier trial now return a 400, and the 5,000
character query still answers normally, so criterion 1 went from 6/10 to
10/10 in all three trials. The log now gains exactly 20 lines for 20 requests
in all three trials, every one with the same nine fields, so criterion 2 went
from 0/20 to 20/20. Criterion 3 was unaffected.

Criteria 4 and 5 didn't change, as I expected, because I didn't touch
`generate.py`. Criterion 4's first request took 5.3, 6.8 and 5.9 s, a bit
higher than before (5.2, 5.0, 5.2 s), and I can't say whether that's noise or
a change; the other four requests stayed at 1.2–2.0 s. Criterion 5's 9/10 in
the third trial is one passing run among three, not a change: the target has to
hold in every trial and it didn't in the other two. I saw no trade-off, meaning
nothing got worse that I measured.

The strongest new evidence for the pacing diagnosis came from this
comparison. In both sets the seventh matching query ("cargo pants") was the
slow one: 21.8, 9.7 and 19.8 s before, and 21.7, 21.0 and 20.0 s after, so five
of six trials took about 20 s on the same request. It's the request where
the run crosses 15 calls in the last minute (two warm-up calls plus six runs
of two calls each, then this run's first and second call), which is where
`_wait_for_slot` would sleep.

---

## Unit 9 — What's Still Broken

Two criteria are still missed. Both come from time spent inside
`generate.py`, which this unit's one fix didn't touch.

**Criterion 4 (bad key fails in 5.0 s or less): missed, 4/5 in all three
after-trials.**
*What I'd do:* import `google.genai` and build the client when `serve.py`
starts, so the first request doesn't pay for it. That import took 3.48 s when I
timed it, and the first request after a restart took 5.0–6.8 s against 1.2–2.0
s for the rest.
*Why I stopped:* the unit allows one improvement, and I picked the problem
that covered two criteria. I also couldn't separate the import from the first
MCP subprocess starting, so I'd want to measure before claiming this fixes it.

**Criterion 5 (8 of 10 matching runs at 5.0 s or less, none above 20 s):
missed, 7/10, 7/10, 9/10.**
*What I'd do:* not remove the pacing wait, because `_wait_for_slot` exists to
stay under the free tier's 15-calls-per-minute limit and removing it would
turn a pause into a rate-limit error. I'd put a queue in front that spaces
requests out, or move to a paid tier whose limit is higher.
*Why I stopped:* the limit belongs to the service, so the fix is a deployment
decision and not a one-line change. The criterion isn't broken, so I didn't
revise it: a back-to-back stream of matching requests really does hit the
limit around the seventh one (the "cargo pants" request took about 20 s in
five of six trials).

**Not tied to a criterion:** seven slow runs in the earlier log started with
fewer than 14 calls in the preceding minute, and I haven't explained them.

**What I'd do next, if this were real and I had another unit.** I'd add a
`wait_for_slot_s` field to the log, recording how long `_wait_for_slot`
slept in each request. Both open misses come from time inside `generate.py`
that `run_s` lumps together with real work, I had to infer the pacing
diagnosis from timestamps, and no fix for either criterion is worth building
until the log can show which of them a slow run was.

---

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
