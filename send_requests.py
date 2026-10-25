#!/usr/bin/env python3
"""
Send a fixed set of requests to a running serve.py, so the run record in
results/serve_log.jsonl comes from a reproducible session.

    python serve.py             (terminal 1; AI201_CACHE=0 for honest timings)
    python send_requests.py     (terminal 2)
"""

import json
import sys
import threading
import urllib.error
import urllib.request

URL = "http://localhost:5000/ask"

SEQUENTIAL = [
    {"query": "vintage graphic tee under $30"},
    {"query": "denim jacket under $40"},
    {"query": "vintage graphic tee size M under $30"},
    {"query": "black combat boots size 9"},
    {"query": "xyzzy plugh under $5"},
    {},  # no query: should come back 400
]

CONCURRENT = [
    {"query": "y2k baby tee under $25"},
    {"query": "oversized flannel under $35"},
]


def ask(body: dict) -> None:
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            session = json.load(resp)
            print(f"{resp.status}  {body.get('query')!r}  error={session.get('error')!r}")
    except urllib.error.HTTPError as exc:
        print(f"{exc.code}  {body.get('query')!r}")
    except urllib.error.URLError as exc:
        sys.exit(f"Can't reach {URL}: {exc.reason}. Is serve.py running?")


if __name__ == "__main__":
    for body in SEQUENTIAL:
        ask(body)

    print("\nTwo at once:")
    threads = [threading.Thread(target=ask, args=(b,)) for b in CONCURRENT]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
