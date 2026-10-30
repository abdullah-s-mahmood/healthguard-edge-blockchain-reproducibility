import csv
import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest_phase4 = root / "results" / "statistics" / "latest_phase4_run.json"
    if latest_phase4.exists():
        latest = json.loads(latest_phase4.read_text(encoding="utf-8"))
        rows = list(csv.DictReader((root / latest["primary_csv"]).open("r", encoding="utf-8")))

        out = root / "results" / "tables" / "phase4_primary_table.csv"
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "architecture",
                    "device_count",
                    "event_rate_per_device",
                    "seed_id",
                    "critical_latency_median_ms",
                    "critical_latency_p95_ms",
                    "delivery_success_ratio",
                    "wan_rate_mb_per_s",
                    "source_class",
                ],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "architecture": row["architecture"],
                        "device_count": row["device_count"],
                        "event_rate_per_device": row["event_rate_per_device"],
                        "seed_id": row["seed_id"],
                        "critical_latency_median_ms": row["critical_latency_median_ms"],
                        "critical_latency_p95_ms": row["critical_latency_p95_ms"],
                        "delivery_success_ratio": row["delivery_success_ratio"],
                        "wan_rate_mb_per_s": row["wan_rate_mb_per_s"],
                        "source_class": row.get("source_class", "SIMULATED"),
                    }
                )

        print(f"Wrote {out}")
        return 0

    latest = json.loads((root / "results" / "statistics" / "latest_component_run.json").read_text(encoding="utf-8"))
    summary = root / latest["summary_csv"]
    rows = list(csv.DictReader(summary.open("r", encoding="utf-8")))

    out = root / "results" / "tables" / "phase3_component_table.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["component", "metric", "value", "source_class"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
