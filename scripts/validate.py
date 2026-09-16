#!/usr/bin/env python3
"""Validate data/commitments.json against the tracker's schema rules."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATUSES = {"not_started", "in_progress", "completed", "stalled"}


def main() -> int:
    meta = json.loads((ROOT / "data" / "meta.json").read_text())
    commitments = json.loads((ROOT / "data" / "commitments.json").read_text())
    agencies = set(meta["agencies"])
    goals = {int(g) for g in meta["goals"]}
    errors = []
    ids = set()

    for c in commitments:
        cid = c.get("id", "<missing id>")
        if cid in ids:
            errors.append(f"{cid}: duplicate id")
        ids.add(cid)
        for field in ("id", "title", "goal", "agencies", "status", "updates"):
            if field not in c:
                errors.append(f"{cid}: missing field {field!r}")
        if c.get("goal") not in goals:
            errors.append(f"{cid}: goal {c.get('goal')!r} not in meta.goals")
        for a in c.get("agencies", []):
            if a not in agencies:
                errors.append(f"{cid}: unknown agency {a!r}")
        if c.get("status") not in STATUSES:
            errors.append(f"{cid}: bad status {c.get('status')!r}")
        updates = c.get("updates", [])
        if not updates:
            errors.append(f"{cid}: needs at least one update entry")
        for u in updates:
            if not u.get("source"):
                errors.append(f"{cid}: update {u.get('date')} has no source URL")
            if u.get("status") not in STATUSES:
                errors.append(f"{cid}: update {u.get('date')} bad status")
        if updates and c.get("status") != updates[0]["status"]:
            errors.append(f"{cid}: top-level status {c['status']!r} != latest update {updates[0]['status']!r}")

    for e in errors:
        print(f"FAIL {e}")
    print(f"{'FAIL' if errors else 'OK'}: {len(commitments)} commitments, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
