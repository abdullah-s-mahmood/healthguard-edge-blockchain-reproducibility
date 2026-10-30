import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def percentile(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    idx = int((len(s) - 1) * p)
    return s[idx]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest_phase4 = root / "results" / "statistics" / "latest_phase4_run.json"
    if latest_phase4.exists():
        latest = json.loads(latest_phase4.read_text(encoding="utf-8"))
        rows = list(csv.DictReader((root / latest["primary_csv"]).open("r", encoding="utf-8")))

        device_counts = [100, 500, 1000, 5000, 10000]
        hg_med, hg_p95 = [], []
        cl_med, cl_p95 = [], []
        for dc in device_counts:
            hg = [float(r["critical_latency_median_ms"]) for r in rows if r["architecture"] == "healthguard" and int(r["device_count"]) == dc]
            cl = [float(r["critical_latency_median_ms"]) for r in rows if r["architecture"] == "cloud_only" and int(r["device_count"]) == dc]
            hg_med.append(sum(hg) / len(hg))
            cl_med.append(sum(cl) / len(cl))
            hg_p95.append(percentile(hg, 0.95))
            cl_p95.append(percentile(cl, 0.95))

        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.plot(device_counts, hg_med, marker="o", label="healthguard")
        ax.plot(device_counts, cl_med, marker="o", label="cloud_only")
        ax.fill_between(device_counts, hg_med, hg_p95, alpha=0.15)
        ax.fill_between(device_counts, cl_med, cl_p95, alpha=0.15)
        ax.set_xlabel("Device count")
        ax.set_ylabel("Critical latency median/p95 (ms)")
        ax.set_title("Phase 4 Simulated Latency vs Load")
        ax.legend()
        fig.tight_layout()

        out_png = root / "results" / "figures" / "supplementary" / "phase4_latency_vs_load.png"
        out_pdf = root / "results" / "figures" / "supplementary" / "phase4_latency_vs_load.pdf"
        fig.savefig(out_png, dpi=300)
        fig.savefig(out_pdf)
        print(f"Wrote {out_png} and {out_pdf}")
        return 0

    latest = json.loads((root / "results" / "statistics" / "latest_component_run.json").read_text(encoding="utf-8"))
    summary = root / latest["summary_csv"]

    rows = list(csv.DictReader(summary.open("r", encoding="utf-8")))
    xs, ys = [], []
    for r in rows:
        if r["metric"].endswith("median_ms"):
            xs.append(r["component"])
            ys.append(float(r["value"]))

    if not xs:
        print("No median_ms values found for plotting")
        return 1

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(xs, ys)
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Phase 3 Component Median Latency Snapshot")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()

    out_png = root / "results" / "figures" / "supplementary" / "phase3_component_latency_snapshot.png"
    out_pdf = root / "results" / "figures" / "supplementary" / "phase3_component_latency_snapshot.pdf"
    fig.savefig(out_png, dpi=300)
    fig.savefig(out_pdf)
    print(f"Wrote {out_png} and {out_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
