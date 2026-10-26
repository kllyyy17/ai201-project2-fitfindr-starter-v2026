#!/usr/bin/env python3
"""
Run the five unit 9 criteria against a running serve.py and print each score.

Criteria 1, 2, 3 and 5 need a server with a good key; criterion 4 needs one
started with a bad key. Start a FRESH server for each (cache off):

    $env:AI201_CACHE = "0"; python serve.py                           # then:
    python run_criteria.py --label run1

    $env:AI201_CACHE = "0"; $env:GEMINI_API_KEY = "bad-key"; python serve.py   # then:
    python run_criteria.py --label run1 --bad-key

Output is printed and saved to results/unit9_<label>[_badkey].txt.
"""

import argparse
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://localhost:5000/ask"
LOG = Path(__file__).parent / "results" / "serve_log.jsonl"
FIELDS = {"ts", "outcome", "http", "query", "error", "wait_s", "run_s", "model_calls", "tokens"}

ORDINARY = [
    "vintage graphic tee under $30",
    "denim jacket under $40",
    "y2k baby tee under $25",
    "oversized flannel under $35",
    "vintage graphic tee size M under $30",
    "black leather jacket under $60",
    "cargo pants under $40",
    "floral sundress under $30",
    "chunky sneakers under $50",
    "knit sweater under $35",
]

# (description, raw request body). Criterion 1.
MALFORMED = [
    ("not JSON", b"this is not json"),
    ("JSON list", b"[1, 2, 3]"),
    ("JSON string", b'"hello"'),
    ("query is a number", b'{"query": 123}'),
    ("query is null", b'{"query": null}'),
    ("query is empty", b'{"query": ""}'),
    ("query is whitespace", b'{"query": "   "}'),
    ("query is a list", b'{"query": ["a"]}'),
    ("wardrobe only", b'{"wardrobe": "x"}'),
    ("5000-char query", json.dumps({"query": ("vintage graphic tee " * 300)[:5000]}).encode()),
]


def send(body: bytes):
    """POST raw bytes. Returns (http status or None if no response, parsed body or None)."""
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, _parse(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, _parse(exc.read())
    except Exception as exc:  # noqa: BLE001 — a dropped connection is a result here
        return None, {"transport_error": f"{type(exc).__name__}: {exc}"}


def _parse(raw: bytes):
    try:
        return json.loads(raw)
    except ValueError:
        return None


def ask(query: str):
    return send(json.dumps({"query": query}).encode())


def log_lines() -> list[str]:
    if not LOG.exists():
        return []
    return LOG.read_text(encoding="utf-8").splitlines()


def parse_records(lines: list[str]):
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except ValueError:
            out.append(None)
    return out


class Tee:
    def __init__(self, path: Path):
        self.f = path.open("w", encoding="utf-8")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


# ── criteria 1 + 2 + 5 ────────────────────────────────────────────────────────

def criteria_1_2_5() -> None:
    ask(ORDINARY[0])  # warm-up: the server has answered one request before we count
    before = len(log_lines())

    print("\n== Criterion 1: malformed input never causes a 500 ==")
    c1 = 0
    for name, body in MALFORMED:
        status, data = send(body)
        good = status is not None and status < 500
        c1 += good
        err = (data or {}).get("error") or (data or {}).get("transport_error")
        print(f"  {'PASS' if good else 'FAIL'}  {name:22s} status={status}  {str(err)[:90]!r}")
    print(f"  Criterion 1 score: {c1}/10  (target 9 of 10)")

    print("\n== Ordinary requests (feed criteria 2 and 5) ==")
    for q in ORDINARY:
        status, _ = ask(q)
        print(f"  {status}  {q!r}")

    new = log_lines()[before:]
    records = parse_records(new)

    print("\n== Criterion 2: one log record per request, same nine fields ==")
    valid = 0
    for i, rec in enumerate(records):
        if rec is None:
            print(f"  FAIL  line {i}: does not parse as JSON: {new[i][:80]!r}")
        elif set(rec) != FIELDS:
            print(f"  FAIL  line {i}: outcome={rec.get('outcome')} fields differ: "
                  f"missing={sorted(FIELDS - set(rec))} extra={sorted(set(rec) - FIELDS)}")
        else:
            valid += 1
    print(f"  Log gained {len(new)} lines (expected 20); {valid} valid.")
    print(f"  Criterion 2 score: {valid if len(new) == 20 else 0}/20  (target 20 of 20, "
          f"exactly 20 new lines)")

    print("\n== Criterion 5: matching requests run_s <= 5.0 s, none > 20 s ==")
    ordinary = [r for r in records[-len(ORDINARY):] if r is not None]
    fast = 0
    for r in ordinary:
        flag = r["outcome"] == "ok" and r.get("run_s", 99) <= 5.0
        fast += flag
        print(f"  {'PASS' if flag else 'FAIL'}  {r['query']!r:42s} outcome={r['outcome']:10s} "
              f"run_s={r.get('run_s')} model_calls={r.get('model_calls')}")
    slowest = max((r.get("run_s", 0) for r in ordinary), default=0)
    print(f"  Slowest run_s: {slowest}")
    if any(r.get("model_calls") == 0 and r["outcome"] == "ok" for r in ordinary):
        print("  WARNING: an ok run made 0 model calls. The cache is on; restart with AI201_CACHE=0.")
    c5 = fast if slowest <= 20 else min(fast, 7)
    print(f"  Criterion 5 score: {c5}/10  (target 8 of 10, none above 20 s)")


# ── criterion 3 ───────────────────────────────────────────────────────────────

def criterion_3() -> None:
    print("\n== Criterion 3: queued request's wait_s matches the run ahead of it ==")
    ok = 0
    for i in range(5):
        before = len(log_lines())
        gate = threading.Barrier(2)

        def go(q):
            gate.wait()
            ask(q)

        qs = [ORDINARY[(2 * i) % 10], ORDINARY[(2 * i + 1) % 10]]
        threads = [threading.Thread(target=go, args=(q,)) for q in qs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        recs = parse_records(log_lines()[before:])
        if len(recs) != 2 or None in recs:
            print(f"  FAIL  pair {i + 1}: expected 2 new records, got {len(recs)}")
            continue
        first, second = recs
        diff = abs(second["wait_s"] - first["run_s"])
        good = second["wait_s"] > 0 and diff <= 1.0
        ok += good
        print(f"  {'PASS' if good else 'FAIL'}  pair {i + 1}: first run_s={first['run_s']}  "
              f"second wait_s={second['wait_s']}  diff={diff:.3f}")
    print(f"  Criterion 3 score: {ok}/5  (target 5 of 5)")


# ── criterion 4 ───────────────────────────────────────────────────────────────

def criterion_4() -> None:
    print("\n== Criterion 4: bad API key fails in 5 s or less (server started with a bad key) ==")
    ok = 0
    for q in ORDINARY[:5]:
        before = len(log_lines())
        status, _ = ask(q)
        recs = parse_records(log_lines()[before:])
        rec = recs[-1] if recs and recs[-1] else None
        if rec is None:
            print(f"  FAIL  {q!r}: no log record (status={status})")
            continue
        good = rec["outcome"] == "agent_error" and rec.get("run_s", 99) <= 5.0
        ok += good
        print(f"  {'PASS' if good else 'FAIL'}  {q!r:42s} outcome={rec['outcome']:12s} "
              f"run_s={rec.get('run_s')}")
    print(f"  Criterion 4 score: {ok}/5  (target 5 of 5, first request included)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="e.g. run1")
    ap.add_argument("--bad-key", action="store_true", help="criterion 4 only; server has a bad key")
    args = ap.parse_args()

    out = Path(__file__).parent / "results" / f"unit9_{args.label}{'_badkey' if args.bad_key else ''}.txt"
    sys.stdout = Tee(out)
    print(f"unit 9 criteria — {args.label}{' (bad key)' if args.bad_key else ''}")

    if args.bad_key:
        criterion_4()
    else:
        criteria_1_2_5()
        criterion_3()
    print(f"\nSaved to {out}")
