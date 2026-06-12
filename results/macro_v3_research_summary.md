# Macro Regime Trader v3 Research Summary

This file is a methodology placeholder. Running the v3 research backtest will
overwrite it with the realized metric tables.

## 1. Strategy objective

Test whether a long-only equity macro regime overlay improves exposure timing,
with Max Drawdown and Calmar ratio treated as the primary KPIs.

## Research hypothesis

SPY volume-confirmed Follow-Through Days identify durable risk-on transitions.

## Economic mechanism

Institutional buying after correction should appear as index-level price gains
on expanding volume.

## Signal definition

A Follow-Through Day occurs after a rally attempt when SPY rises at least 1.25%
on higher volume without undercutting the rally low.

## Expected improvement

The v3 model should improve Max Drawdown and Calmar versus the base price-only
model.

## Failure condition

If v3 does not improve drawdown metrics, or results disappear under
out-of-sample and sensitivity tests, the FTD layer is not robust.

## 2. Economic rationale

The base model estimates market regime from price, volatility, breadth, and
cross-sectional momentum. The v3 layer tests whether SPY volume confirmation
adds incremental information about accumulation and distribution.

## 3. Signal design

The control model is `base_price_only`. The test model is
`price_plus_spy_volume_confirmation`, which adds volume breakout,
Follow-Through Day, Distribution Day, and Heavy Distribution Day signals.

## Rule-based mathematical definitions

Let \(P_t\), \(L_t\), and \(V_t\) denote SPY close, low, and volume on trading
date \(t\). Let \(w_t\) denote portfolio weights set after observing date \(t\),
and applied to returns from \(t\) to \(t+1\). Parameters are hypothesis
definitions, not optimized values:

\[
\theta_{FTD}=1.25\%,\quad
\theta_{DD}=-0.25\%,\quad
\theta_{HDD}=-1.00\%,\quad
\theta_C=-8\%,\quad
\lambda=0.15.
\]

Sensitivity tests evaluate nearby values separately.

SPY daily return:

\[
r^{SPY}_t = \frac{P_t}{P_{t-1}} - 1.
\]

50-day drawdown:

\[
DD^{50}_t = \frac{P_t}{\max(P_{t-49}, \ldots, P_t)} - 1.
\]

Correction state:

\[
C_t = 1\{DD^{50}_t \le \theta_C\}.
\]

Optionally, the implementation may also require price weakness versus the
50-day moving average. Otherwise \(C_t=0\).

Rally attempt day count:

A rally attempt begins on date \(t\) if \(C_t=1\), \(r^{SPY}_t>0\), and no
rally attempt is already active. The rally attempt day count \(A_t\) is set to
1 on the first rally attempt day and increments by one while the rally remains
active.

Rally low:

\[
RL_t = \min(RL_{t-1}, L_t)
\]

while a rally attempt is active. To avoid a self-referential undercut test, the
failed-rally check uses the prior value \(RL_{t-1}\) before updating \(RL_t\).

Failed rally indicator:

\[
FR_t = 1\{A_{t-1}>0 \ \text{and}\ L_t < RL_{t-1}\}.
\]

If \(FR_t=1\), the rally attempt is reset before any Follow-Through Day can be
confirmed.

Follow-Through Day indicator:

\[
FTD_t = 1\{A_t \ge 4,\ r^{SPY}_t \ge \theta_{FTD},\ V_t>V_{t-1},\ FR_t=0\}.
\]

Distribution Day indicator:

\[
DIST_t = 1\{r^{SPY}_t \le \theta_{DD},\ V_t>V_{t-1}\}.
\]

Heavy Distribution Day indicator:

\[
HDIST_t = 1\{r^{SPY}_t \le \theta_{HDD},\ V_t/MA_{50}(V)_t \ge 1.20\}.
\]

Volume confirmation score:

\[
S^{VOL}_t =
clip(
0.25BRK_t + 1.00FTD_t - 0.35DIST_t - 0.75HDIST_t - 0.25CLUST_t,
-1, 1
),
\]

where

\[
BRK_t=1\{r^{SPY}_t>0,\ V_t/MA_{50}(V)_t \ge 1.10\}
\]

and

\[
CLUST_t=1\{\sum_{i=0}^{24} DIST_{t-i} \ge 4\}.
\]

Base regime score:

\[
S^{BASE}_t \in [-1,1]
\]

is the existing price-only composite averaging the VIX proxy, SPY trend, market
breadth, volatility regime, and cross-sectional momentum indicators.

Final v3 regime score:

\[
S^{V3}_t = clip((1-\lambda)S^{BASE}_t + \lambda S^{VOL}_t, -1, 1).
\]

Final exposure scale:

\[
x^{BASE}_t = clip((S^{BASE}_t+1)/2,0,1),
\quad
x^{V3}_t = clip((S^{V3}_t+1)/2,0,1).
\]

Execution lag and portfolio weights:

All indicators using \(P_t\), \(L_t\), or \(V_t\) are only applied to weights for
the next return period. Therefore \(w_t=f(x_t,\mathcal{I}_t)\) is computed
after date \(t\) information is observable and earns asset returns \(R_{t+1}\),
not \(R_t\).

Portfolio return:

\[
R^p_{t+1}=w_t^\top R_{t+1}-TC_{t+1},
\]

where transaction cost scenarios use

\[
TC_{t+1}=c\sum_i |w_{i,t}-w_{i,t-1}|,
\quad c \in \{0,5,10,20\}\text{ basis points}.
\]

Opportunity cost:

Because the FTD layer is low frequency, it is evaluated not only by whether it
reduces drawdowns, but also by whether its defensive exposure reductions miss
too much upside.

When v3 is more defensive than the base model:

\[
OC_{t+1}
= \max(x^{BASE}_t-x^{V3}_t,0)\max(R^{RP}_{t+1},0)
\]

and

\[
LA_{t+1}
= \max(x^{BASE}_t-x^{V3}_t,0)\max(-R^{RP}_{t+1},0).
\]

Here \(OC\) is opportunity cost, \(LA\) is loss avoided, and \(R^{RP}_{t+1}\)
is the next-period gross return of the risk-parity portfolio without a regime
overlay.

The primary defensive timing statistic is:

\[
NDTB = \sum LA_{t+1} - \sum OC_{t+1}.
\]

When v3 takes more risk than the base model:

\[
UC_{t+1}
= \max(x^{V3}_t-x^{BASE}_t,0)\max(R^{RP}_{t+1},0)
\]

and

\[
EL_{t+1}
= \max(x^{V3}_t-x^{BASE}_t,0)\max(-R^{RP}_{t+1},0).
\]

Here \(UC\) is upside captured and \(EL\) is extra loss. This separates the
benefit of additional risk-taking from the cost of being too aggressive.

Base vs v3 evaluation metrics:

Compare `base_price_only` and `price_plus_spy_volume_confirmation` on Sharpe,
Calmar, CAGR, total return, annual volatility, win rate, and Max Drawdown. The
primary validation criteria are Max Drawdown and Calmar, including full-sample,
in-sample, out-of-sample, transaction-cost sensitivity, and
parameter-sensitivity results.

## 4. Timing and look-ahead bias control

Signals are computed on `signal_date` and applied only to the next tradable
period. The generated diagnostics file records `signal_date`,
`next_return_date`, and `execution_lag_used`.

## 5. Base vs v3 comparison

Generated by the research backtest.

## 6. Benchmark comparison

Generated by the research backtest.

## 7. Transaction cost sensitivity

Generated by the research backtest.

## 8. Out-of-sample results

Generated by the research backtest.

## 8b. Opportunity cost and timing benefit

Generated by the research backtest and saved to
`results/macro_v3_opportunity_cost.csv`.

## 9. Parameter sensitivity

Generated by the research backtest.

## 10. Conclusion

The conclusion should be based on whether v3 improves Calmar and reduces Max
Drawdown relative to the base price-only model. If it does not, the correct
research conclusion is that the SPY volume-confirmation layer did not add clear
incremental value under the tested design.
