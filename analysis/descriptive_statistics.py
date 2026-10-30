import csv
import json
from statistics import mean, median, stdev
from pathlib import Path


def percentile(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    idx = int((len(s) - 1) * p)
    return s[idx]


def summarize(values):
    s = sorted(values)
    q1 = percentile(s, 0.25)
    q3 = percentile(s, 0.75)
    return {
        "n": len(s),
        "mean": mean(s),
        "sd": stdev(s) if len(s) > 1 else 0.0,
        "median": median(s),
        "iqr": q3 - q1,
        "p95": percentile(s, 0.95),
        "p99": percentile(s, 0.99),
        "min": min(s),
        "max": max(s),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest_phase4 = root / "results" / "statistics" / "latest_phase4_run.json"
    if latest_phase4.exists():
        latest = json.loads(latest_phase4.read_text(encoding="utf-8"))
        primary = root / latest["primary_csv"]
        rows = list(csv.DictReader(primary.open("r", encoding="utf-8")))

        out = root / "results" / "statistics" / "descriptive_phase4_primary.csv"
        with out.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "architecture",
                "device_count",
                "metric",
                "n",
                "mean",
                "sd",
                "median",
                "iqr",
                "p95",
                "p99",
                "min",
                "max",
                "source_class",
            ]
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for arch in ["healthguard", "cloud_only"]:
                for dc in [100, 500, 1000, 5000, 10000]:
                    subset = [r for r in rows if r["architecture"] == arch and int(r["device_count"]) == dc]
                    for metric in ["critical_latency_median_ms", "delivery_success_ratio", "wan_rate_mb_per_s"]:
                        values = [float(r[metric]) for r in subset]
                        s = summarize(values)
                        writer.writerow(
                            {
                                "architecture": arch,
                                "device_count": dc,
                                "metric": metric,
                                "n": s["n"],
                                "mean": round(s["mean"], 6),
                                "sd": round(s["sd"], 6),
                                "median": round(s["median"], 6),
                                "iqr": round(s["iqr"], 6),
                                "p95": round(s["p95"], 6),
                                "p99": round(s["p99"], 6),
                                "min": round(s["min"], 6),
                                "max": round(s["max"], 6),
                                "source_class": "SIMULATED",
                            }
                        )

        print(f"Wrote {out}")
        return 0

    latest = json.loads((root / "results" / "statistics" / "latest_component_run.json").read_text(encoding="utf-8"))
    summary = root / latest["summary_csv"]
    rows = list(csv.DictReader(summary.open("r", encoding="utf-8")))
    out = root / "results" / "statistics" / "descriptive_component_snapshot.csv"

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["component", "metric", "value", "source_class"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
