#!/usr/bin/env bash
# Refresh data/kpi-snapshot.json — the offline fallback for the KPI panel.
# The page queries NYC Open Data live; this snapshot is only used when that fails.
set -euo pipefail
cd "$(dirname "$0")/.."

SELECT='date_trunc_ym(crash_date) as month'
for f in persons pedestrians cyclist motorist; do
  case $f in persons) k=killed i=injured ;; pedestrians) k=ped_killed i=ped_injured ;;
    cyclist) k=cyc_killed i=cyc_injured ;; motorist) k=mot_killed i=mot_injured ;; esac
  SELECT+=",sum(number_of_${f}_killed) as $k,sum(number_of_${f}_injured) as $i"
done

curl -sf -G "https://data.cityofnewyork.us/resource/h9gi-nx95.json" \
  --data-urlencode "\$select=$SELECT" \
  --data-urlencode "\$where=crash_date >= '2016-01-01'" \
  --data-urlencode "\$group=month" \
  --data-urlencode "\$order=month" \
  --data-urlencode "\$limit=200" \
  -o data/kpi-snapshot.json

echo "Wrote data/kpi-snapshot.json ($(python3 -c "import json;print(len(json.load(open('data/kpi-snapshot.json'))))") months)"
