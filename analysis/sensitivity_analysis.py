import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest_phase4 = root / "results" / "statistics" / "latest_phase4_run.json"
    if latest_phase4.exists():
        import csv

        latest = json.loads(latest_phase4.read_text(encoding="utf-8"))
        rows = list(csv.DictReader((root / latest["sensitivity_csv"]).open("r", encoding="utf-8")))

        grouped = {}
        for row in rows:
            key = (row["sensitivity_id"], row["target_metric"])
            grouped.setdefault(key, []).append(float(row["target_value"]))

        out_csv = root / "results" / "statistics" / "sensitivity_phase4_summary.csv"
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["sensitivity_id", "target_metric", "n", "mean_value", "min_value", "max_value", "source_class"],
            )
            writer.writeheader()
            for (sid, metric), values in sorted(grouped.items()):
                writer.writerow(
                    {
                        "sensitivity_id": sid,
                        "target_metric": metric,
                        "n": len(values),
                        "mean_value": round(sum(values) / len(values), 6),
                        "min_value": round(min(values), 6),
                        "max_value": round(max(values), 6),
                        "source_class": "SIMULATED",
                    }
                )

        out_note = root / "results" / "statistics" / "sensitivity_phase4_note.txt"
        out_note.write_text(
            "Phase 4 sensitivity sweep executed on SIMULATED surrogate model across preregistered factor grids.\n",
            encoding="utf-8",
        )
        print(f"Wrote {out_csv} and {out_note}")
        return 0

    latest = root / "results" / "statistics" / "latest_component_run.json"
    if not latest.exists():
        print("No latest component run found")
        return 1

    out = root / "results" / "statistics" / "sensitivity_phase3_note.txt"
    out.write_text(
        "Sensitivity experiments are preregistered in configs/experiment_matrix.yaml and are deferred to Phase 4 execution.\n",
        encoding="utf-8",
    )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
