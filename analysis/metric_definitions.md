# Metric Definitions (Phase 8)

## Throughput

$$
\text{Throughput}_{\text{achieved}} = \frac{N_{\text{acknowledged}}}{\Delta t}
$$

Where:

- $N_{\text{acknowledged}}$: number of acknowledged events in the measurement interval.
- $\Delta t$: interval duration in seconds.

## Delivery Success Ratio

$$
\text{Delivery Success Ratio} = \frac{N_{\text{acknowledged}}}{N_{\text{offered}}}
$$

## Duplicate Ratio

$$
\text{Duplicate Ratio} = \frac{N_{\text{duplicates}}}{N_{\text{processed}}}
$$

## Latency Improvement

$$
\text{Latency Improvement}(\%) = 100 \times \frac{L_{\text{cloud}} - L_{\text{healthguard}}}{L_{\text{cloud}}}
$$

Important rule: compare matched statistics (median with median, p95 with p95) under matched load and seed pairing.

## Bandwidth Saving

$$
\text{Bandwidth Saving}(\%) = 100 \times \left(1 - \frac{B_{\text{healthguard}}}{B_{\text{cloud}}}\right)
$$

Where $B$ is measured WAN bytes over the same interval and workload condition.

## Evidence-Class Note

Metric values reported from Phase 4 system-level runs are SIMULATED in this repository state.
