#!/usr/bin/env python3
"""
Measure what one successful run costs: send ten matching queries to a running
serve.py (started with AI201_CACHE=0), then average the last ten `ok` lines of
results/serve_log.jsonl.

    python serve.py             (terminal 1, AI201_CACHE=0)
    python measure_cost.py      (terminal 2)
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://localhost:5000/ask"
LOG = Path(__file__).parent / "results" / "serve_log.jsonl"

QUERIES = [
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


def ask(query: str) -> None:
    req = urllib.request.Request(
        URL,
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            print(f"{resp.status}  {query!r}")
    except urllib.error.URLError as exc:
        sys.exit(f"Can't reach {URL}: {exc}. Is serve.py running?")


if __name__ == "__main__":
    for q in QUERIES:
        ask(q)

    records = [json.loads(line) for line in LOG.open(encoding="utf-8")]
    ok = [r for r in records if r["outcome"] == "ok"][-len(QUERIES):]
    n = len(ok)
    print(f"\nLast {n} 'ok' runs from {LOG.name}:")
    if n < len(QUERIES):
        print(f"  (only {n} ok runs — some queries matched nothing; swap them for ones that match)")
    for key in ("run_s", "model_calls", "tokens"):
        vals = [r[key] for r in ok]
        print(f"  mean {key:12s} {sum(vals) / n:.2f}   (min {min(vals)}, max {max(vals)})")
