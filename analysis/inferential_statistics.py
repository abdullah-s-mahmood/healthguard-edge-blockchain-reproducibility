import csv
import json
from pathlib import Path

from scipy import stats


def holm_correction(pvalues):
    indexed = sorted(enumerate(pvalues), key=lambda x: x[1])
    m = len(pvalues)
    adjusted = [0.0] * m
    running = 0.0
    for rank, (idx, p) in enumerate(indexed, start=1):
        adj = (m - rank + 1) * p
        running = max(running, adj)
        adjusted[idx] = min(1.0, running)
    return adjusted


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    latest_phase4 = root / "results" / "statistics" / "latest_phase4_run.json"
    if latest_phase4.exists():
        latest = json.loads(latest_phase4.read_text(encoding="utf-8"))
        rows = list(csv.DictReader((root / latest["primary_csv"]).open("r", encoding="utf-8")))

        out_csv = root / "results" / "statistics" / "inferential_phase4_paired.csv"
        out_note = root / "results" / "statistics" / "inferential_statistics_note.txt"

        pvals = []
        result_rows = []
        by_key = {}
        for r in rows:
            key = (int(r["device_count"]), int(r["seed_id"]))
            by_key.setdefault(key, {})[r["architecture"]] = r

        for dc in [100, 500, 1000, 5000, 10000]:
            diffs = []
            for seed in sorted({int(r["seed_id"]) for r in rows}):
                k = (dc, seed)
                if k not in by_key or "healthguard" not in by_key[k] or "cloud_only" not in by_key[k]:
                    continue
                hg = float(by_key[k]["healthguard"]["critical_latency_median_ms"])
                cl = float(by_key[k]["cloud_only"]["critical_latency_median_ms"])
                diffs.append(cl - hg)

            if len(diffs) < 3:
                continue

            shapiro_p = stats.shapiro(diffs).pvalue
            if shapiro_p >= 0.05:
                tstat, pval = stats.ttest_1samp(diffs, popmean=0.0)
                test_name = "paired_t_as_1sample_on_diff"
                effect = (sum(diffs) / len(diffs)) / (stats.tstd(diffs) if stats.tstd(diffs) > 0 else 1.0)
            else:
                stat, pval = stats.wilcoxon(diffs, zero_method="wilcox", correction=False)
                test_name = "wilcoxon_signed_rank"
                effect = sum(1 for d in diffs if d > 0) / len(diffs)

            pvals.append(pval)
            result_rows.append(
                {
                    "device_count": dc,
                    "n_pairs": len(diffs),
                    "test": test_name,
                    "normality_pvalue": round(shapiro_p, 6),
                    "raw_pvalue": round(float(pval), 8),
                    "mean_latency_reduction_ms": round(sum(diffs) / len(diffs), 6),
                    "effect_size": round(float(effect), 6),
                    "source_class": "SIMULATED",
                }
            )

        adjusted = holm_correction(pvals) if pvals else []
        for i, adj in enumerate(adjusted):
            result_rows[i]["holm_adjusted_pvalue"] = round(float(adj), 8)

        with out_csv.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "device_count",
                "n_pairs",
                "test",
                "normality_pvalue",
                "raw_pvalue",
                "holm_adjusted_pvalue",
                "mean_latency_reduction_ms",
                "effect_size",
                "source_class",
            ]
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(result_rows)

        out_note.write_text(
            "Phase 4 inferential statistics executed on paired SIMULATED runs. "
            "Do not promote as production deployment evidence.\n",
            encoding="utf-8",
        )
        print(f"Wrote {out_csv} and {out_note}, rows={len(result_rows)}")
        return 0

    latest = json.loads((root / "results" / "statistics" / "latest_component_run.json").read_text(encoding="utf-8"))
    summary = root / latest["summary_csv"]
    rows = list(csv.DictReader(summary.open("r", encoding="utf-8")))

    # Phase 3 note: one calibration run only; inferential tests deferred to repeated Phase 4 runs.
    out = root / "results" / "statistics" / "inferential_statistics_note.txt"
    out.write_text(
        "Inferential statistics not executed in Phase 3 because only a single calibration run is available.\n"
        "Full paired inference with Holm correction is preregistered for Phase 4/5.\n",
        encoding="utf-8",
    )
    print(f"Wrote {out}, rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
