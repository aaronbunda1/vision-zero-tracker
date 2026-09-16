# Vision Zero Reimagined Tracker

Personal tracker for the 100+ policy commitments in Mayor Mamdani's **Vision Zero
Reimagined** plan (announced September 15, 2026), in the spirit of
[project2025.observer](https://www.project2025.observer/). Not affiliated with the
City of New York.

## Run it

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

No build step. The page loads `data/*.json` and queries NYC Open Data live for the
KPI charts (falling back to `data/kpi-snapshot.json` when offline).

## What's here

| Path | Purpose |
|---|---|
| `data/commitments.json` | The 112 tracked commitments — **this is the file that changes over time** |
| `data/meta.json` | Goals, agencies, status labels, plan metadata |
| `data/kpi-snapshot.json` | Cached monthly deaths/injuries (offline fallback) — refresh with `scripts/fetch_kpi.sh` |
| `scripts/build_commitments.py` | One-time seed generator (transcribed from the plan PDF's Action Plan List, pp. 93–99). **Re-running it wipes status history.** |
| `scripts/validate.py` | Schema check — run after any data edit |
| `source/Vision-Zero-Reimagined-2026.pdf` | The official plan document |

## Updating a status

The workflow: when news breaks about a commitment, tell Claude
"update the Vision Zero tracker: <link>". Concretely, an update means:

1. Find the commitment in `data/commitments.json` (ids are `vz-g<goal>-<plan number>`,
   matching the plan's Action Plan List numbering).
2. Prepend an entry to its `updates` array (newest first):
   ```json
   { "date": "2027-01-10", "status": "in_progress",
     "note": "DOT announced the first 15 School Slow Zones",
     "source": "https://..." }
   ```
3. Set the top-level `status` to match the new entry.
4. Run `python3 scripts/validate.py` — every update **must** cite a source URL,
   and top-level status must equal the latest update's status.

Statuses: `not_started` · `in_progress` · `completed` · `stalled`.

## KPI data notes

- Source: [Motor Vehicle Collisions – Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)
  (Socrata `h9gi-nx95`), aggregated monthly by SoQL, charted as trailing-12-month totals
  by road user (pedestrian / cyclist / motorist).
- NYPD reporting lags ~2–3 months; the last months are shaded provisional and the
  trailing partial month is dropped.
- Injury counts are **all severities**. The city's official Vision Zero "serious
  injury" (KABCO A) metric is only published via Vision Zero View, which has no
  clean public API.
