import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest_phase4 = root / "results" / "statistics" / "latest_phase4_run.json"
    if latest_phase4.exists():
        latest = json.loads(latest_phase4.read_text(encoding="utf-8"))
        primary = root / latest["primary_csv"]
        blockchain = root / latest["blockchain_csv"]
        sensitivity = root / latest["sensitivity_csv"]

        for path in [primary, blockchain, sensitivity]:
            if not path.exists():
                print("Missing raw path", path)
                return 2

        import csv

        seen = set()
        rows = list(csv.DictReader(primary.open("r", encoding="utf-8")))
        for row in rows:
            key = (row["architecture"], row["device_count"], row["seed_id"])
            if key in seen:
                print("Duplicate primary key", key)
                return 3
            seen.add(key)

            if float(row["critical_latency_median_ms"]) <= 0:
                print("Non-positive latency", key)
                return 4
            if float(row["delivery_success_ratio"]) < 0 or float(row["delivery_success_ratio"]) > 1:
                print("Invalid success ratio", key)
                return 5

        print("Raw data validation passed for phase4. rows=", len(rows))
        return 0

    latest_path = root / "results" / "statistics" / "latest_component_run.json"
    if not latest_path.exists():
        print("No component benchmark run found")
        return 1

    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    raw_path = root / latest["raw_jsonl"]
    if not raw_path.exists():
        print("Missing raw path", raw_path)
        return 2

    seen = set()
    for line in raw_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        eid = row.get("event_id")
        if eid and eid in seen:
            print("Duplicate event id", eid)
            return 3
        if eid:
            seen.add(eid)

    print("Raw data validation passed. rows=", len(raw_path.read_text(encoding="utf-8").splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
