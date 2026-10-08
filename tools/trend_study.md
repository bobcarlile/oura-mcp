# Does a trend tool add an answer?

> **Decision, 8 October 2026: no `oura_trend`.** The gain below is real but
> small (4–7 points at 1 SD, 10–12 at 2 SD) and was only shown at 60–90
> days: at 180 every slope test passed the 6% ceiling somewhere (up to 7.4%),
> though `oura_compare` on halves reached 6.4% there too, so that difference
> is slight. A seventh tool in two languages for that gain was not worth it;
> the server tells the model to compare the two halves of the window instead.
> See the ROADMAP entry of the same date. The verdict paragraph further down is
> the study's own reading, kept as written.

Study run on 8 October 2026, using `tools/trend_study.py`. All percentages below
are simulated, not measurements of anyone's Oura data.

The null table gives the **range across 16 scenarios**, not uncertainty intervals.
Null false alarms are conditional on an answer; `cannot_tell` is always reported
as a fraction of all runs. Power cells are **detection % / cannot_tell %**, both
out of all runs. The averages weight the 16 scenarios equally; they are not an
estimate of the mix of real Oura users. The complete per-scenario tables follow.

### Null ranges across all stationary scenarios

| Days | OLS | OLS effective-n | HAC | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|---|
| 60 | 5.3–52.0 | 2.6–5.9 | 8.8–33.2 | 2.3–4.9 | 2.1–5.0 | 0.9–5.0 |
| 90 | 5.1–50.6 | 2.6–6.0 | 7.3–30.1 | 2.8–5.9 | 2.6–6.0 | 1.2–5.4 |
| 180 | 5.3–52.1 | 3.3–6.7 | 7.0–26.2 | 3.2–7.4 | 2.8–6.4 | 0.8–5.1 |

Power cells: outside_noise / cannot_tell among ALL simulations (%).

### Power average: 60 days, equal weight to 16 scenarios

| Days | Total drift (SD) | OLS effective-n | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|
| 60 | 0.5 | 9.2 / 1.1 | 8.7 / 1.1 | 8.0 / 0.0 | 5.1 / 1.5 |
| 60 | 1.0 | 24.6 / 1.1 | 23.1 / 1.1 | 19.1 / 0.0 | 11.3 / 1.5 |
| 60 | 2.0 | 63.3 / 1.1 | 60.9 / 1.1 | 51.0 / 0.0 | 33.6 / 1.5 |

### Power average: 90 days, equal weight to 16 scenarios

| Days | Total drift (SD) | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|
| 90 | 0.5 | 11.7 / 0.5 | 9.5 / 0.0 | 4.7 / 1.5 |
| 90 | 1.0 | 32.7 / 0.5 | 25.6 / 0.0 | 11.3 / 1.5 |
| 90 | 2.0 | 75.5 / 0.5 | 65.5 / 0.0 | 34.7 / 1.5 |

### Power average: 180 days, equal weight to 16 scenarios

| Days | Total drift (SD) | Compare halves | Compare last14 |
|---|---|---|---|
| 180 | 0.5 | 16.1 / 0.0 | 4.4 / 1.7 |
| 180 | 1.0 | 45.8 / 0.0 | 10.9 / 1.7 |
| 180 | 2.0 | 86.5 / 0.0 | 33.3 / 1.7 |

**Verdict.** A narrowly scoped trend tool is worth pursuing for **60–90 days**:
there is additional power at approximately the same false-alarm rate, especially
for a 2-SD total drift. The history-variance slope test improves on comparing
halves by **4.0 and 7.1 percentage points** for a 1-SD drift at 60 and 90 days,
and **9.9 and 10.0 points** for 2 SD. At 60 days, residual-variance OLS with
history-based effective-n does slightly better: **5.5 and 12.3 points** for 1 and
2 SD. Gains for 0.5 SD are only **0.7–2.2 points**. Against last14-vs-rest the
history-slope gains are much larger: **11.8/21.4 points** for 1 SD and
**27.3/40.8 points** for 2 SD at 60/90 days, though last14 is also more
conservative under the null. **No candidate qualifies at 180 days**; its trend
power is deliberately excluded. This supports a limited prototype, not a
calibrated general-purpose tool across all three lengths.

The improvement is not uniform. With rho=0.65 and no gaps, history slope detects
2-SD drifts **50.4% vs 38.7%** at 60 days and **69.8% vs 57.9%** at 90 days.
With rho=0.8 and 30% gaps, it detects only **15.2% vs 10.0%** and **26.2% vs
20.4%**, and returns `cannot_tell` **15.6% / 8.0%** of the time. An averaged
refusal rate hides that difficulty. A within-noise result still does not rule
out a gradual change.

## Choices made before the completed run

- **Generators:** unchanged function ASTs are loaded from `test_compare.py`
  (`_ar1`, `_days`) and `test_relate.py` (`_ar1`, `_days`, `_weekend`, `_null`).
  This executes the original functions without importing pytest. AR(1) starts
  in its stationary distribution, has innovation SD 1, and uses rho
  **0, .3, .4, .5, .65, .8**. Each is run complete and with 30% independent
  missing days. Weekday C reproduces compare's rho=.4 / weekend +1 pattern;
  Weekday R calls relate's weekly null directly (rho=.65 / weekend +1.5),
  discarding its second metric. Both also run with 30% gaps. No generator
  parameters or existing thresholds were edited.
- **Scope of the null:** a stationary metric with no secular drift. Relate's
  independent random walks and deterministic trends are nulls for *relation
  between metrics*, not stationary no-trend baselines; they are not included.
  These results make no promise for nonstationary wandering metrics.
- **History and alternatives:** generate one continuous series of 120 history
  days followed by N window days, with gaps applied to both. The history stays
  unchanged. Add `effect * sigma * day/(N-1)` only in the window, with effect
  .5, 1, or 2 and `sigma=1/sqrt(1-rho**2)`: stationary daily-level noise SD,
  not innovation SD or SD of first differences. Weekend offsets do not enter
  sigma. Drift therefore starts at zero and ends at the stated change, even
  when endpoints are missing. All methods share the same simulated draws.
- **Real compare:** call `M.compare_series` directly twice: first N/2 calendar
  days against the second half, and first N-14 against last 14. Each uses the
  preceding 120 calendar days as history. No artificial ten-day gap is inserted:
  the periods requested here are adjacent. They are two separate usages, not
  an OR rule that chooses whichever rejects.
- **OLS:** regress observed values on actual calendar days and an intercept.
  Missing days never compress time. With centered day sum of squares Sxx,
  residual variance is SSE/(observed_n-2), giving slope variance s²/Sxx.
  **OLS effective-n** multiplies that variance by `(1+rho)/(1-rho)` and uses
  `df=observed_n*(1-rho)/(1+rho)-2`. Rho is `M.lag1(history)`, including its
  existing [0,.95] clamp and calendar-pair normalization; it is not estimated
  from fitted window residuals.
- **HAC:** Newey–West slope sandwich from centered-day-times-residual scores,
  Bartlett weights `1-lag/(L+1)`, calendar lags, bandwidth
  `L=floor(4*(N/100)**(2/9))` (3, 3, 4 days), HC1 factor n/(n-2), t with n-2
  degrees of freedom. Missing scores contribute zero; no weekday effects are
  fitted. This particular fixed-bandwidth candidate fails; that is not a claim
  that every possible HAC method fails.
- **History slope:** the same OLS slope, with sample variance from history in
  place of residual variance, the same AR(1) inflation, and
  `df=min(observed_n, history_n)*(1-rho)/(1+rho)-2`. It assumes stable noise
  variance from history to window. Both history-based candidates require the
  existing 60 history observations and 20 consecutive pairs. All trend
  candidates require 7 observations, positive variance, and df >= 1; otherwise
  they return `cannot_tell`. All use the repository's unchanged two-sided
  95% `t_critical` table.
- **Screening:** a candidate must have <=6% false alarms among answered runs
  in **every** scenario at a window length to enter power comparisons there.
  This rule was set before inspecting completed results, and is stricter than
  the existing tests' 7%. At 2,000 null repetitions, Monte Carlo uncertainty
  near 5% is about ±1 percentage point (95%, pointwise), so this is a feasibility
  screen, not proof of exact 5% size. No critical values were tuned to results.
  Naive OLS and HAC fail at all lengths. Effective-n OLS fails at 90 days on
  **121/2,000 = 6.05%**, displayed as 6.0% after rounding, and fails at 180.
  History slope passes 60/90 and fails 180 (up to 7.4%). Compare-halves itself
  reaches 6.4% at 180; the earlier ROADMAP calibration covered different,
  shorter periods. Its baseline results remain visible and unmodified.
- **Simulation:** seed **20261008**, 2,000 null runs per scenario/window and
  1,000 independent-seed power runs per scenario/window/effect. Effects share
  draws, so they are not independent replications. A per-scenario power estimate
  has at most ±3.1 points of Monte Carlo uncertainty; the equally weighted
  16-scenario average has at most ±0.8 points (pointwise approximate 95%).
  Differences are computed from rounded tables; no exact size-matching between
  methods or simultaneous confidence guarantee is claimed. Borderline screening
  outcomes need independent confirmation before implementation.

## Reproduction and verification

```
.venv/bin/python tools/trend_study.py
```

**Measured wall-clock runtime: 90.421 seconds**, completed successfully, below
five minutes. The script prints all tables and its measured runtime. It uses
stdlib only; a separate `python -S` check verified generator identity,
calendar ordering, and verdict invariance to offsets and nonzero scaling.
No network access, package installation, production edits, commits, or pushes.

<details>
<summary>Complete null tables (false alarms / cannot_tell, %)</summary>

### Null: 60 days

| Noise | Missing | OLS | OLS effective-n | HAC | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|---|---|
| AR 0 | 0% | 6.2 / 0.0 | 5.5 / 0.0 | 8.8 / 0.0 | 4.9 / 0.0 | 5.0 / 0.0 | 4.9 / 0.0 |
| AR 0 | 30% | 5.3 / 0.0 | 4.2 / 0.0 | 9.2 / 0.0 | 4.0 / 0.0 | 3.8 / 0.0 | 4.4 / 3.2 |
| AR 0.3 | 0% | 14.4 / 0.0 | 5.9 / 0.0 | 12.1 / 0.0 | 4.6 / 0.0 | 4.8 / 0.0 | 4.2 / 0.0 |
| AR 0.3 | 30% | 10.9 / 0.0 | 3.6 / 0.0 | 11.0 / 0.0 | 3.5 / 0.0 | 3.9 / 0.0 | 3.4 / 3.3 |
| AR 0.4 | 0% | 20.4 / 0.0 | 5.7 / 0.0 | 15.1 / 0.0 | 4.7 / 0.0 | 5.0 / 0.0 | 5.0 / 0.0 |
| AR 0.4 | 30% | 14.2 / 0.0 | 3.1 / 0.0 | 12.7 / 0.0 | 3.2 / 0.0 | 3.5 / 0.0 | 3.4 / 3.5 |
| AR 0.5 | 0% | 26.5 / 0.0 | 4.8 / 0.0 | 17.1 / 0.0 | 4.9 / 0.0 | 4.8 / 0.0 | 3.5 / 0.0 |
| AR 0.5 | 30% | 20.4 / 0.0 | 2.9 / 0.1 | 15.9 / 0.0 | 3.2 / 0.1 | 3.2 / 0.0 | 2.7 / 2.5 |
| AR 0.65 | 0% | 36.5 / 0.0 | 4.5 / 0.0 | 21.8 / 0.0 | 3.9 / 0.0 | 4.8 / 0.0 | 3.2 / 0.0 |
| AR 0.65 | 30% | 30.9 / 0.0 | 3.2 / 1.1 | 23.1 / 0.0 | 2.7 / 1.1 | 2.6 / 0.0 | 1.9 / 2.8 |
| AR 0.8 | 0% | 52.0 / 0.0 | 4.0 / 0.1 | 33.2 / 0.0 | 3.2 / 0.1 | 4.0 / 0.0 | 1.6 / 0.0 |
| AR 0.8 | 30% | 44.1 / 0.0 | 3.0 / 17.6 | 30.4 / 0.0 | 2.5 / 17.6 | 2.1 / 0.0 | 0.9 / 2.9 |
| Weekday C | 0% | 16.6 / 0.0 | 3.8 / 0.0 | 12.4 / 0.0 | 3.5 / 0.0 | 3.5 / 0.0 | 2.8 / 0.0 |
| Weekday C | 30% | 14.1 / 0.0 | 2.6 / 0.0 | 12.6 / 0.0 | 2.9 / 0.0 | 2.8 / 0.0 | 2.5 / 3.5 |
| Weekday R | 0% | 30.7 / 0.0 | 5.0 / 0.0 | 19.1 / 0.0 | 4.5 / 0.0 | 4.4 / 0.0 | 3.5 / 0.0 |
| Weekday R | 30% | 23.1 / 0.0 | 2.7 / 0.5 | 17.7 / 0.0 | 2.3 / 0.5 | 3.0 / 0.0 | 1.4 / 3.3 |

### Null: 90 days

| Noise | Missing | OLS | OLS effective-n | HAC | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|---|---|
| AR 0 | 0% | 5.8 / 0.0 | 5.3 / 0.0 | 8.2 / 0.0 | 5.0 / 0.0 | 4.3 / 0.0 | 4.5 / 0.0 |
| AR 0 | 30% | 5.2 / 0.0 | 3.9 / 0.0 | 7.3 / 0.0 | 4.6 / 0.0 | 4.4 / 0.0 | 4.0 / 2.9 |
| AR 0.3 | 0% | 14.8 / 0.0 | 6.0 / 0.0 | 11.8 / 0.0 | 5.9 / 0.0 | 5.7 / 0.0 | 5.4 / 0.0 |
| AR 0.3 | 30% | 13.4 / 0.0 | 4.3 / 0.0 | 10.8 / 0.0 | 4.7 / 0.0 | 4.7 / 0.0 | 3.4 / 3.0 |
| AR 0.4 | 0% | 21.4 / 0.0 | 6.0 / 0.0 | 12.5 / 0.0 | 5.6 / 0.0 | 6.0 / 0.0 | 4.3 / 0.0 |
| AR 0.4 | 30% | 16.5 / 0.0 | 4.3 / 0.0 | 11.1 / 0.0 | 4.4 / 0.0 | 4.2 / 0.0 | 2.8 / 2.6 |
| AR 0.5 | 0% | 24.8 / 0.0 | 5.0 / 0.0 | 13.5 / 0.0 | 4.8 / 0.0 | 5.0 / 0.0 | 3.9 / 0.0 |
| AR 0.5 | 30% | 19.9 / 0.0 | 3.7 / 0.1 | 12.6 / 0.0 | 4.0 / 0.1 | 3.5 / 0.0 | 2.9 / 2.9 |
| AR 0.65 | 0% | 34.1 / 0.0 | 5.2 / 0.0 | 19.2 / 0.0 | 5.5 / 0.0 | 4.5 / 0.0 | 3.2 / 0.0 |
| AR 0.65 | 30% | 30.9 / 0.0 | 3.3 / 0.5 | 19.7 / 0.0 | 3.2 / 0.5 | 3.1 / 0.0 | 1.6 / 2.9 |
| AR 0.8 | 0% | 50.6 / 0.0 | 5.0 / 0.0 | 30.1 / 0.0 | 4.6 / 0.0 | 4.8 / 0.0 | 1.6 / 0.0 |
| AR 0.8 | 30% | 43.6 / 0.0 | 3.9 / 8.3 | 28.3 / 0.0 | 4.0 / 8.3 | 3.2 / 0.0 | 1.2 / 3.4 |
| Weekday C | 0% | 16.7 / 0.0 | 4.2 / 0.0 | 10.8 / 0.0 | 4.1 / 0.0 | 4.0 / 0.0 | 3.6 / 0.0 |
| Weekday C | 30% | 13.5 / 0.0 | 2.6 / 0.0 | 10.4 / 0.0 | 2.8 / 0.0 | 2.6 / 0.0 | 1.8 / 3.2 |
| Weekday R | 0% | 30.8 / 0.0 | 4.5 / 0.0 | 17.4 / 0.0 | 4.3 / 0.0 | 4.5 / 0.0 | 2.5 / 0.0 |
| Weekday R | 30% | 23.0 / 0.0 | 3.3 / 0.2 | 15.5 / 0.0 | 3.2 / 0.2 | 2.9 / 0.0 | 1.8 / 3.0 |

### Null: 180 days

| Noise | Missing | OLS | OLS effective-n | HAC | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|---|---|
| AR 0 | 0% | 5.3 / 0.0 | 4.8 / 0.0 | 7.1 / 0.0 | 4.7 / 0.0 | 5.3 / 0.0 | 5.2 / 0.0 |
| AR 0 | 30% | 5.7 / 0.0 | 5.0 / 0.0 | 7.0 / 0.0 | 4.8 / 0.0 | 4.5 / 0.0 | 3.9 / 3.3 |
| AR 0.3 | 0% | 15.7 / 0.0 | 5.7 / 0.0 | 8.9 / 0.0 | 5.8 / 0.0 | 6.4 / 0.0 | 4.5 / 0.0 |
| AR 0.3 | 30% | 13.1 / 0.0 | 4.7 / 0.0 | 9.3 / 0.0 | 5.2 / 0.0 | 4.5 / 0.0 | 3.4 / 2.9 |
| AR 0.4 | 0% | 20.6 / 0.0 | 6.7 / 0.0 | 10.9 / 0.0 | 6.7 / 0.0 | 6.3 / 0.0 | 3.9 / 0.0 |
| AR 0.4 | 30% | 15.3 / 0.0 | 3.6 / 0.0 | 9.0 / 0.0 | 3.9 / 0.0 | 4.2 / 0.0 | 2.8 / 2.8 |
| AR 0.5 | 0% | 26.2 / 0.0 | 6.0 / 0.0 | 11.8 / 0.0 | 6.2 / 0.0 | 5.5 / 0.0 | 3.8 / 0.0 |
| AR 0.5 | 30% | 21.1 / 0.0 | 4.0 / 0.0 | 11.5 / 0.0 | 4.2 / 0.0 | 3.7 / 0.0 | 2.5 / 3.0 |
| AR 0.65 | 0% | 35.8 / 0.0 | 6.1 / 0.0 | 15.3 / 0.0 | 6.0 / 0.0 | 5.3 / 0.0 | 2.2 / 0.0 |
| AR 0.65 | 30% | 30.0 / 0.0 | 4.1 / 0.0 | 15.1 / 0.0 | 4.2 / 0.1 | 4.0 / 0.0 | 1.3 / 2.4 |
| AR 0.8 | 0% | 52.1 / 0.0 | 6.2 / 0.0 | 26.1 / 0.0 | 7.4 / 0.0 | 6.1 / 0.0 | 0.8 / 0.0 |
| AR 0.8 | 30% | 44.7 / 0.0 | 4.5 / 0.3 | 24.2 / 0.0 | 5.7 / 6.4 | 4.1 / 0.0 | 0.8 / 2.9 |
| Weekday C | 0% | 17.4 / 0.0 | 4.6 / 0.0 | 10.2 / 0.0 | 4.7 / 0.0 | 4.0 / 0.0 | 2.9 / 0.0 |
| Weekday C | 30% | 12.3 / 0.0 | 3.3 / 0.0 | 8.4 / 0.0 | 3.2 / 0.0 | 2.8 / 0.0 | 2.5 / 2.9 |
| Weekday R | 0% | 31.2 / 0.0 | 6.0 / 0.0 | 15.6 / 0.0 | 5.8 / 0.0 | 5.2 / 0.0 | 1.9 / 0.0 |
| Weekday R | 30% | 26.4 / 0.0 | 4.5 / 0.0 | 15.2 / 0.0 | 4.8 / 0.1 | 4.0 / 0.0 | 1.0 / 3.4 |

</details>

<details>
<summary>Complete power tables (detection / cannot_tell, %)</summary>

### Power detail: 60 days

| Noise | Missing | Drift (SD) | OLS effective-n | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|---|
| AR 0 | 0% | 0.5 | 18.9 / 0.0 | 18.5 / 0.0 | 13.6 / 0.0 | 10.8 / 0.0 |
| AR 0 | 0% | 1.0 | 58.6 / 0.0 | 58.8 / 0.0 | 46.0 / 0.0 | 32.3 / 0.0 |
| AR 0 | 0% | 2.0 | 99.6 / 0.0 | 99.2 / 0.0 | 96.2 / 0.0 | 84.9 / 0.0 |
| AR 0 | 30% | 0.5 | 13.5 / 0.0 | 13.6 / 0.0 | 12.0 / 0.0 | 8.5 / 2.7 |
| AR 0 | 30% | 1.0 | 42.4 / 0.0 | 41.5 / 0.0 | 31.4 / 0.0 | 20.2 / 2.7 |
| AR 0 | 30% | 2.0 | 93.6 / 0.0 | 94.0 / 0.0 | 83.4 / 0.0 | 61.3 / 2.7 |
| AR 0.3 | 0% | 0.5 | 13.7 / 0.0 | 13.6 / 0.0 | 11.3 / 0.0 | 10.3 / 0.0 |
| AR 0.3 | 0% | 1.0 | 41.1 / 0.0 | 39.9 / 0.0 | 31.8 / 0.0 | 21.9 / 0.0 |
| AR 0.3 | 0% | 2.0 | 92.0 / 0.0 | 91.3 / 0.0 | 79.2 / 0.0 | 63.7 / 0.0 |
| AR 0.3 | 30% | 0.5 | 9.6 / 0.0 | 9.9 / 0.0 | 8.3 / 0.0 | 5.2 / 3.3 |
| AR 0.3 | 30% | 1.0 | 27.3 / 0.0 | 26.8 / 0.0 | 20.3 / 0.0 | 12.7 / 3.3 |
| AR 0.3 | 30% | 2.0 | 76.9 / 0.0 | 77.9 / 0.0 | 62.3 / 0.0 | 43.2 / 3.3 |
| AR 0.4 | 0% | 0.5 | 13.9 / 0.0 | 12.8 / 0.0 | 12.0 / 0.0 | 8.1 / 0.0 |
| AR 0.4 | 0% | 1.0 | 34.1 / 0.0 | 31.7 / 0.0 | 26.7 / 0.0 | 17.4 / 0.0 |
| AR 0.4 | 0% | 2.0 | 82.1 / 0.0 | 80.6 / 0.0 | 69.5 / 0.0 | 50.2 / 0.0 |
| AR 0.4 | 30% | 0.5 | 6.6 / 0.0 | 6.3 / 0.0 | 6.7 / 0.0 | 4.0 / 2.9 |
| AR 0.4 | 30% | 1.0 | 20.4 / 0.0 | 18.8 / 0.0 | 14.7 / 0.0 | 9.5 / 2.9 |
| AR 0.4 | 30% | 2.0 | 67.7 / 0.0 | 64.5 / 0.0 | 50.6 / 0.0 | 32.0 / 2.9 |
| AR 0.5 | 0% | 0.5 | 10.3 / 0.0 | 8.9 / 0.0 | 6.8 / 0.0 | 5.9 / 0.0 |
| AR 0.5 | 0% | 1.0 | 24.6 / 0.0 | 22.7 / 0.0 | 18.3 / 0.0 | 12.8 / 0.0 |
| AR 0.5 | 0% | 2.0 | 74.2 / 0.0 | 70.9 / 0.0 | 57.5 / 0.0 | 39.8 / 0.0 |
| AR 0.5 | 30% | 0.5 | 7.1 / 0.2 | 5.9 / 0.2 | 5.4 / 0.0 | 3.8 / 2.9 |
| AR 0.5 | 30% | 1.0 | 14.6 / 0.2 | 14.1 / 0.2 | 10.8 / 0.0 | 6.9 / 2.9 |
| AR 0.5 | 30% | 2.0 | 51.9 / 0.2 | 47.8 / 0.2 | 36.7 / 0.0 | 20.2 / 2.9 |
| AR 0.65 | 0% | 0.5 | 7.4 / 0.0 | 6.0 / 0.0 | 7.1 / 0.0 | 4.2 / 0.0 |
| AR 0.65 | 0% | 1.0 | 18.3 / 0.0 | 15.7 / 0.0 | 12.8 / 0.0 | 7.1 / 0.0 |
| AR 0.65 | 0% | 2.0 | 54.1 / 0.0 | 50.4 / 0.0 | 38.7 / 0.0 | 19.7 / 0.0 |
| AR 0.65 | 30% | 0.5 | 4.7 / 1.5 | 4.6 / 1.5 | 3.9 / 0.0 | 2.6 / 3.0 |
| AR 0.65 | 30% | 1.0 | 11.6 / 1.5 | 9.1 / 1.5 | 8.3 / 0.0 | 4.2 / 3.0 |
| AR 0.65 | 30% | 2.0 | 34.5 / 1.5 | 32.3 / 1.5 | 23.2 / 0.0 | 11.9 / 3.0 |
| AR 0.8 | 0% | 0.5 | 5.8 / 0.0 | 4.8 / 0.0 | 4.6 / 0.0 | 2.1 / 0.0 |
| AR 0.8 | 0% | 1.0 | 10.9 / 0.0 | 9.1 / 0.0 | 7.8 / 0.0 | 3.3 / 0.0 |
| AR 0.8 | 0% | 2.0 | 31.0 / 0.0 | 25.9 / 0.0 | 18.5 / 0.0 | 7.9 / 0.0 |
| AR 0.8 | 30% | 0.5 | 4.0 / 15.6 | 3.6 / 15.6 | 2.9 / 0.0 | 1.8 / 2.9 |
| AR 0.8 | 30% | 1.0 | 6.0 / 15.6 | 6.5 / 15.6 | 4.4 / 0.0 | 2.2 / 2.9 |
| AR 0.8 | 30% | 2.0 | 18.2 / 15.6 | 15.2 / 15.6 | 10.0 / 0.0 | 4.9 / 2.9 |
| Weekday C | 0% | 0.5 | 9.3 / 0.0 | 8.8 / 0.0 | 9.7 / 0.0 | 4.7 / 0.0 |
| Weekday C | 0% | 1.0 | 30.1 / 0.0 | 27.8 / 0.0 | 24.7 / 0.0 | 11.1 / 0.0 |
| Weekday C | 0% | 2.0 | 80.1 / 0.0 | 78.0 / 0.0 | 70.2 / 0.0 | 41.0 / 0.0 |
| Weekday C | 30% | 0.5 | 7.6 / 0.0 | 6.7 / 0.0 | 8.0 / 0.0 | 3.3 / 2.9 |
| Weekday C | 30% | 1.0 | 20.1 / 0.0 | 18.1 / 0.0 | 16.5 / 0.0 | 7.6 / 2.9 |
| Weekday C | 30% | 2.0 | 64.5 / 0.0 | 61.6 / 0.0 | 50.3 / 0.0 | 25.0 / 2.9 |
| Weekday R | 0% | 0.5 | 10.1 / 0.0 | 10.5 / 0.0 | 10.0 / 0.0 | 4.2 / 0.0 |
| Weekday R | 0% | 1.0 | 21.9 / 0.0 | 19.8 / 0.0 | 20.1 / 0.0 | 8.9 / 0.0 |
| Weekday R | 0% | 2.0 | 55.9 / 0.0 | 53.3 / 0.0 | 43.2 / 0.0 | 23.7 / 0.0 |
| Weekday R | 30% | 0.5 | 4.9 / 0.0 | 4.3 / 0.0 | 5.3 / 0.0 | 1.8 / 3.0 |
| Weekday R | 30% | 1.0 | 10.8 / 0.0 | 9.7 / 0.0 | 10.4 / 0.0 | 2.7 / 3.0 |
| Weekday R | 30% | 2.0 | 36.6 / 0.0 | 32.1 / 0.0 | 26.7 / 0.0 | 8.2 / 3.0 |

### Power detail: 90 days

| Noise | Missing | Drift (SD) | History slope | Compare halves | Compare last14 |
|---|---|---|---|---|---|
| AR 0 | 0% | 0.5 | 25.7 / 0.0 | 19.4 / 0.0 | 11.3 / 0.0 |
| AR 0 | 0% | 1.0 | 74.8 / 0.0 | 61.3 / 0.0 | 33.3 / 0.0 |
| AR 0 | 0% | 2.0 | 100.0 / 0.0 | 99.5 / 0.0 | 88.2 / 0.0 |
| AR 0 | 30% | 0.5 | 18.9 / 0.0 | 15.3 / 0.0 | 7.5 / 3.5 |
| AR 0 | 30% | 1.0 | 60.0 / 0.0 | 47.7 / 0.0 | 22.6 / 3.5 |
| AR 0 | 30% | 2.0 | 99.2 / 0.0 | 94.5 / 0.0 | 68.8 / 3.5 |
| AR 0.3 | 0% | 0.5 | 18.2 / 0.0 | 14.2 / 0.0 | 8.4 / 0.0 |
| AR 0.3 | 0% | 1.0 | 51.6 / 0.0 | 43.0 / 0.0 | 22.8 / 0.0 |
| AR 0.3 | 0% | 2.0 | 98.2 / 0.0 | 92.9 / 0.0 | 63.1 / 0.0 |
| AR 0.3 | 30% | 0.5 | 11.5 / 0.0 | 8.7 / 0.0 | 5.0 / 3.1 |
| AR 0.3 | 30% | 1.0 | 36.2 / 0.0 | 27.9 / 0.0 | 11.6 / 3.1 |
| AR 0.3 | 30% | 2.0 | 90.1 / 0.0 | 80.5 / 0.0 | 40.8 / 3.1 |
| AR 0.4 | 0% | 0.5 | 13.1 / 0.0 | 11.1 / 0.0 | 6.5 / 0.0 |
| AR 0.4 | 0% | 1.0 | 42.7 / 0.0 | 33.2 / 0.0 | 15.2 / 0.0 |
| AR 0.4 | 0% | 2.0 | 94.5 / 0.0 | 86.3 / 0.0 | 51.9 / 0.0 |
| AR 0.4 | 30% | 0.5 | 10.3 / 0.0 | 8.5 / 0.0 | 5.1 / 3.2 |
| AR 0.4 | 30% | 1.0 | 28.9 / 0.0 | 21.7 / 0.0 | 10.2 / 3.2 |
| AR 0.4 | 30% | 2.0 | 82.4 / 0.0 | 69.6 / 0.0 | 32.7 / 3.2 |
| AR 0.5 | 0% | 0.5 | 12.5 / 0.0 | 11.1 / 0.0 | 5.9 / 0.0 |
| AR 0.5 | 0% | 1.0 | 36.9 / 0.0 | 26.6 / 0.0 | 13.1 / 0.0 |
| AR 0.5 | 0% | 2.0 | 87.7 / 0.0 | 76.9 / 0.0 | 41.6 / 0.0 |
| AR 0.5 | 30% | 0.5 | 7.4 / 0.0 | 6.4 / 0.0 | 2.9 / 3.4 |
| AR 0.5 | 30% | 1.0 | 23.6 / 0.0 | 19.5 / 0.0 | 6.2 / 3.4 |
| AR 0.5 | 30% | 2.0 | 72.8 / 0.0 | 58.9 / 0.0 | 20.8 / 3.4 |
| AR 0.65 | 0% | 0.5 | 11.2 / 0.0 | 8.8 / 0.0 | 3.2 / 0.0 |
| AR 0.65 | 0% | 1.0 | 24.8 / 0.0 | 20.1 / 0.0 | 6.1 / 0.0 |
| AR 0.65 | 0% | 2.0 | 69.8 / 0.0 | 57.9 / 0.0 | 20.1 / 0.0 |
| AR 0.65 | 30% | 0.5 | 6.8 / 0.1 | 5.3 / 0.0 | 1.6 / 2.1 |
| AR 0.65 | 30% | 1.0 | 15.6 / 0.1 | 9.7 / 0.0 | 3.7 / 2.1 |
| AR 0.65 | 30% | 2.0 | 48.6 / 0.1 | 35.9 / 0.0 | 11.5 / 2.1 |
| AR 0.8 | 0% | 0.5 | 7.6 / 0.0 | 6.2 / 0.0 | 1.5 / 0.0 |
| AR 0.8 | 0% | 1.0 | 14.5 / 0.0 | 11.6 / 0.0 | 2.8 / 0.0 |
| AR 0.8 | 0% | 2.0 | 41.0 / 0.0 | 31.3 / 0.0 | 7.0 / 0.0 |
| AR 0.8 | 30% | 0.5 | 5.6 / 8.0 | 5.3 / 0.0 | 1.5 / 3.2 |
| AR 0.8 | 30% | 1.0 | 10.2 / 8.0 | 8.1 / 0.0 | 2.8 / 3.2 |
| AR 0.8 | 30% | 2.0 | 26.2 / 8.0 | 20.4 / 0.0 | 5.5 / 3.2 |
| Weekday C | 0% | 0.5 | 13.8 / 0.0 | 11.1 / 0.0 | 6.7 / 0.0 |
| Weekday C | 0% | 1.0 | 38.7 / 0.0 | 29.4 / 0.0 | 13.2 / 0.0 |
| Weekday C | 0% | 2.0 | 93.2 / 0.0 | 84.0 / 0.0 | 46.9 / 0.0 |
| Weekday C | 30% | 0.5 | 7.3 / 0.0 | 6.3 / 0.0 | 3.5 / 2.2 |
| Weekday C | 30% | 1.0 | 25.6 / 0.0 | 18.5 / 0.0 | 7.4 / 2.2 |
| Weekday C | 30% | 2.0 | 80.6 / 0.0 | 65.0 / 0.0 | 27.3 / 2.2 |
| Weekday R | 0% | 0.5 | 11.2 / 0.0 | 9.4 / 0.0 | 3.7 / 0.0 |
| Weekday R | 0% | 1.0 | 24.8 / 0.0 | 20.9 / 0.0 | 6.8 / 0.0 |
| Weekday R | 0% | 2.0 | 70.8 / 0.0 | 56.3 / 0.0 | 19.6 / 0.0 |
| Weekday R | 30% | 0.5 | 5.9 / 0.0 | 4.9 / 0.0 | 1.6 / 3.5 |
| Weekday R | 30% | 1.0 | 14.5 / 0.0 | 10.9 / 0.0 | 2.6 / 3.5 |
| Weekday R | 30% | 2.0 | 52.2 / 0.0 | 37.5 / 0.0 | 9.5 / 3.5 |

### Power detail: 180 days

| Noise | Missing | Drift (SD) | Compare halves | Compare last14 |
|---|---|---|---|---|
| AR 0 | 0% | 0.5 | 36.8 / 0.0 | 13.8 / 0.0 |
| AR 0 | 0% | 1.0 | 90.3 / 0.0 | 37.2 / 0.0 |
| AR 0 | 0% | 2.0 | 100.0 / 0.0 | 88.9 / 0.0 |
| AR 0 | 30% | 0.5 | 25.7 / 0.0 | 7.7 / 3.3 |
| AR 0 | 30% | 1.0 | 78.5 / 0.0 | 23.1 / 3.3 |
| AR 0 | 30% | 2.0 | 99.9 / 0.0 | 66.8 / 3.3 |
| AR 0.3 | 0% | 0.5 | 23.7 / 0.0 | 8.2 / 0.0 |
| AR 0.3 | 0% | 1.0 | 70.7 / 0.0 | 18.0 / 0.0 |
| AR 0.3 | 0% | 2.0 | 99.7 / 0.0 | 63.3 / 0.0 |
| AR 0.3 | 30% | 0.5 | 18.6 / 0.0 | 5.5 / 3.6 |
| AR 0.3 | 30% | 1.0 | 54.1 / 0.0 | 13.6 / 3.6 |
| AR 0.3 | 30% | 2.0 | 98.3 / 0.0 | 41.8 / 3.6 |
| AR 0.4 | 0% | 0.5 | 21.5 / 0.0 | 5.8 / 0.0 |
| AR 0.4 | 0% | 1.0 | 59.9 / 0.0 | 16.7 / 0.0 |
| AR 0.4 | 0% | 2.0 | 99.1 / 0.0 | 53.5 / 0.0 |
| AR 0.4 | 30% | 0.5 | 14.7 / 0.0 | 4.0 / 2.7 |
| AR 0.4 | 30% | 1.0 | 44.5 / 0.0 | 9.2 / 2.7 |
| AR 0.4 | 30% | 2.0 | 95.2 / 0.0 | 30.3 / 2.7 |
| AR 0.5 | 0% | 0.5 | 19.5 / 0.0 | 5.2 / 0.0 |
| AR 0.5 | 0% | 1.0 | 51.8 / 0.0 | 11.4 / 0.0 |
| AR 0.5 | 0% | 2.0 | 97.0 / 0.0 | 38.9 / 0.0 |
| AR 0.5 | 30% | 0.5 | 10.4 / 0.0 | 1.9 / 3.8 |
| AR 0.5 | 30% | 1.0 | 34.2 / 0.0 | 4.3 / 3.8 |
| AR 0.5 | 30% | 2.0 | 88.2 / 0.0 | 17.8 / 3.8 |
| AR 0.65 | 0% | 0.5 | 12.1 / 0.0 | 1.6 / 0.0 |
| AR 0.65 | 0% | 1.0 | 36.7 / 0.0 | 5.5 / 0.0 |
| AR 0.65 | 0% | 2.0 | 85.8 / 0.0 | 18.0 / 0.0 |
| AR 0.65 | 30% | 0.5 | 7.7 / 0.0 | 1.5 / 3.3 |
| AR 0.65 | 30% | 1.0 | 23.8 / 0.0 | 3.0 / 3.3 |
| AR 0.65 | 30% | 2.0 | 68.9 / 0.0 | 8.6 / 3.3 |
| AR 0.8 | 0% | 0.5 | 10.2 / 0.0 | 1.1 / 0.0 |
| AR 0.8 | 0% | 1.0 | 23.5 / 0.0 | 1.7 / 0.0 |
| AR 0.8 | 0% | 2.0 | 60.0 / 0.0 | 4.1 / 0.0 |
| AR 0.8 | 30% | 0.5 | 7.6 / 0.0 | 1.3 / 3.7 |
| AR 0.8 | 30% | 1.0 | 15.4 / 0.0 | 2.0 / 3.7 |
| AR 0.8 | 30% | 2.0 | 43.3 / 0.0 | 4.7 / 3.7 |
| Weekday C | 0% | 0.5 | 17.4 / 0.0 | 5.3 / 0.0 |
| Weekday C | 0% | 1.0 | 52.4 / 0.0 | 12.8 / 0.0 |
| Weekday C | 0% | 2.0 | 98.7 / 0.0 | 42.1 / 0.0 |
| Weekday C | 30% | 0.5 | 11.6 / 0.0 | 4.3 / 3.7 |
| Weekday C | 30% | 1.0 | 38.9 / 0.0 | 8.3 / 3.7 |
| Weekday C | 30% | 2.0 | 93.3 / 0.0 | 26.7 / 3.7 |
| Weekday R | 0% | 0.5 | 12.7 / 0.0 | 2.7 / 0.0 |
| Weekday R | 0% | 1.0 | 35.4 / 0.0 | 5.6 / 0.0 |
| Weekday R | 0% | 2.0 | 85.1 / 0.0 | 19.6 / 0.0 |
| Weekday R | 30% | 0.5 | 7.6 / 0.0 | 0.9 / 3.1 |
| Weekday R | 30% | 1.0 | 22.6 / 0.0 | 1.8 / 3.1 |
| Weekday R | 30% | 2.0 | 71.8 / 0.0 | 7.5 / 3.1 |

</details>
