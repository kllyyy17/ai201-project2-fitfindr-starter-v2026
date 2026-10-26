# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->
My search is a plain keyword-overlap match with no synonym or fuzzy
matching, so a query that matches a listing in spirit can still score zero
on wording alone. That's an expected miss from how my search is built, not a
broken loop, so I leave room for it instead of promising 5 of 5.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->
Stopping here is just an `if not session["search_results"]` check in my own
loop, with no model or fuzzy-matching randomness involved. If this isn't 5
of 5, the loop has a bug, not a hard case.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->


Given a matching query, `session["selected_item"]["id"]` after `search_listings`
returns equals the `id` of the `new_item` dict that `suggest_outfit` actually
receives — in 5 of 5 tries, checked by trace, not by re-reading the code.

**Why this target:**
This one should be 5 of 5 or the loop is broken, not flaky, since there's no
randomness between picking `search_results[0]` and passing it along, so any
mismatch is a wiring bug. A weaker target would just be hiding a bug behind
a percentage.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->


Given the same item and outfit run 5 times, every one of the 5 fit cards
mentions the item's price and platform at least once each — 5 of 5, no
matter how the wording around them varies.

**Why this target:**
The words can and should change, since that's `TEMPERATURE = 0.9` doing its
job rather than a defect. Price and platform are instructions in my prompt,
not style, and a model follows them close to every time, so anything under
5 of 5 signals a prompt problem, not a rate to relax.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->


Given an empty wardrobe, `suggest_outfit` still returns a non-empty string
of general styling advice (not an error, not "") and the run completes
through to a fit card — in 5 of 5 tries.

**Why this target:**
This is a fixed branch I control, checking `wardrobe['items']` and taking
the general-advice prompt path when it's empty, so nothing about it should
vary. If it fails, it's because I forgot to handle the empty case, not
because the model or the search got unlucky.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->


---

# Unit 9 — extension criteria

Written before any unit 9 results were checked against them. These cover the
extension (`serve.py`'s run path and `results/serve_log.jsonl`), not the agent
itself. "Run" means one `POST /ask`. Timings are `run_s` from the log, on a
server that has already answered one request, with `AI201_CACHE=0`.

---

## 1. Malformed input never causes a 500

Send ten malformed requests: a body that isn't JSON, a JSON list, a JSON
string, `{"query": 123}`, `{"query": null}`, `{"query": ""}`, `{"query": "   "}`,
`{"query": ["a"]}`, `{"wardrobe": "x"}` with no query, and a 5,000-character
query. At least 9 of the 10 return a 4xx or a normal 200 with
`session["error"]` set — none of them a 500 or a dropped connection.

**Why this target:**
`ask()` calls `.get()` on whatever `get_json` returns and `.strip()` on
whatever `query` is, and neither is type-checked, so inputs that are valid JSON
but the wrong type are the likely failures. I allow one miss instead of zero
because a 5,000-character query goes through the regex parser and the model,
which I haven't tested and can't fully predict. A 500 here would mean a caller
gets a stack-trace-shaped error for a typo.

---

## 2. Every request leaves exactly one log record, with the same fields

After sending the ten requests from criterion 1 plus ten ordinary ones (twenty
total), `results/serve_log.jsonl` gains exactly 20 lines, every line parses as
JSON, and every line has the same nine fields: `ts`, `outcome`, `http`,
`query`, `error`, `wait_s`, `run_s`, `model_calls`, `tokens`. 20 of 20 lines,
no exceptions.

**Why this target:**
The log is the only evidence I'll have when something goes wrong, and a request that leaves no record or a record missing `run_s` can't be diagnosed or averaged. A
percentage would hide exactly the requests I most need to see. Today a bad
request logs fewer fields than the others, so this is a target I expect to
have to work for.

---

## 3. A queued request's `wait_s` matches the run ahead of it

Send two requests at once, five times. In each pair, the second request's
`wait_s` is within 1.0 s of the first request's `run_s`. 5 of 5 pairs.

**Why this target:**
The one-at-a-time lock means a queued request waits for exactly the run in
front of it, so if `wait_s` is off by more than a second the timing is
measuring something other than the queue and I can't trust the split between
waiting and running. One second is generous against runs of 3–5 s, and
stricter than that would just be measuring clock noise. 5 of 5, because this
is arithmetic about a lock, not model variance.

---

## 4. A run with a bad API key fails in 5 seconds or less

With an invalid `GEMINI_API_KEY`, send five requests that match a listing. All
five come back with `outcome: "agent_error"` and `run_s` of 5.0 s or less,
the first one included.

**Why this target:**
A rejected key can't succeed on retry, so the user should hear about it
quickly, and a five-second wait for a one-line error is the most I'd accept
before a person assumes the service hung. `generate.py` paces and retries
calls, and I've seen failed runs take anywhere from about 1 s to over 10 s,
so I don't know that the first request stays under five. I'm requiring 5 of 5
because a slow failure is the case where nobody finds out the key is wrong.

---

## 5. A typical matching request is fast enough to wait for

Ten matching queries, run one at a time: at least 8 of the 10 have `run_s` of
5.0 s or less, and none has `run_s` above 20 s.

**Why this target:**
Each run is two model calls plus an MCP subprocess. The cost measurement in
the README had a median of 4.4 s with two of ten runs well above that, so 5 s
should be reachable most of the time but not always. I picked it knowing that
baseline, which means it's close to the edge on purpose. I'm measuring a count
under a threshold rather than the mean, because a couple of slow runs would
swamp a mean without telling me anything about the typical case. The 20 s cap
covers the worst case a person would give up on.
