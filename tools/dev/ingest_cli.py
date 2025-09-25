from __future__ import annotations

import argparse
import json
import sys

import requests


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", help="Base URL, e.g. http://localhost:8080")
    ap.add_argument("dataset_id", help="Dataset id")
    ap.add_argument("uris", nargs="+", help="URIs or file paths to ingest (PDFs)")
    args = ap.parse_args()

    payload = {"dataset_id": args.dataset_id, "uris": args.uris, "metadata": {"source": "cli"}}
    r = requests.post(f"{args.base}/v1/ingest", json=payload, timeout=60)
    print(r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    return 0 if r.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


