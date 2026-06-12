# Macro Regime Trader v3 Research Summary

## 1. Strategy objective
Test whether a long-only equity macro regime overlay can improve exposure timing, with drawdown control and Calmar ratio as the main KPIs.

## Research hypothesis
SPY volume-confirmed Follow-Through Days identify durable risk-on transitions.

## Economic mechanism
Institutional buying after a correction should appear as index-level price gains on expanding volume. The volume-confirmation layer is therefore designed to test whether accumulation and distribution evidence improves exposure scaling beyond the base price-only macro regime model.

## Expected improvement
The v3 model should improve Max Drawdown and Calmar versus the base price-only model.

## Failure condition
If v3 does not improve drawdown metrics, or if the results disappear under out-of-sample and sensitivity tests, the Follow-Through Day layer is not robust.

## Hypothesis evolution
The v3 model tested whether FTD and SPY volume confirmation improve risk-on timing. Empirically, v3 slightly reduced volatility and Max Drawdown, but worsened Calmar because opportunity cost exceeded loss avoided. This suggests that unconditional daily volume penalties are too noisy and too costly. Therefore, the final strategy candidate returns to the simpler `base_price_only` macro regime overlay, and robustness tests focus on whether the base model is stable across signal ablations, parameter choices, subperiods, and opportunity-cost diagnostics.

## 2. Economic rationale
The base model estimates broad equity risk appetite from SPY volatility, trend, market breadth, volatility regime, and cross-sectional momentum. The v3 layer asks whether SPY volume confirmation adds information about institutional accumulation or distribution.

## 3. Signal design
The control strategy is `base_price_only`. The tested strategy is `price_plus_spy_volume_confirmation`, which blends the base price composite with volume breakout, Follow-Through Day, Distribution Day, and Heavy Distribution Day evidence. A Follow-Through Day occurs after a rally attempt when SPY rises at least 1.25% on higher volume without undercutting the rally low.

## Rule-based mathematical definitions

Let \(P_t\), \(L_t\), and \(V_t\) denote SPY close, low, and volume on trading date \(t\). Let \(w_t\) denote portfolio weights set after observing date \(t\), and applied to returns from \(t\) to \(t+1\). Parameters are hypothesis definitions, not optimized values: \(\theta_{FTD}=1.25\%\), \(\theta_{DD}=-0.25\%\), \(\theta_{HDD}=-1.00\%\), \(\theta_C=-8\%\), and \(\lambda=0.15\). Sensitivity tests evaluate nearby values separately.

SPY daily return: \(r^{SPY}_t=P_t/P_{t-1}-1\).

50-day drawdown: \(DD^{50}_t=P_t / \max(P_{t-49},...,P_t)-1\).

Correction indicator: \(C_t=1\{DD^{50}_t \le \theta_C\}\), optionally also requiring price weakness versus the 50-day moving average. Otherwise \(C_t=0\).

Rally attempt state: a rally attempt begins on date \(t\) if \(C_t=1\), \(r^{SPY}_t>0\), and no rally attempt is already active. The rally attempt day count \(A_t\) is set to 1 on the first rally attempt day and increments by one while the rally remains active.

Rally low: \(RL_t\) is the minimum SPY low observed during the active rally attempt through date \(t\). To avoid a self-referential undercut test, the failed-rally check uses the prior value \(RL_{t-1}\) before updating \(RL_t=\min(RL_{t-1},L_t)\).

Failed rally indicator: \(FR_t=1\{A_{t-1}>0 \text{ and } L_t < RL_{t-1}\}\). If \(FR_t=1\), the rally attempt is reset before any Follow-Through Day can be confirmed.

Follow-Through Day indicator: \(FTD_t=1\{A_t \ge 4,\ r^{SPY}_t \ge \theta_{FTD},\ V_t>V_{t-1},\ FR_t=0\}\). Otherwise \(FTD_t=0\).

Distribution Day indicator: \(DIST_t=1\{r^{SPY}_t \le \theta_{DD},\ V_t>V_{t-1}\}\).

Heavy Distribution Day indicator: \(HDIST_t=1\{r^{SPY}_t \le \theta_{HDD},\ V_t/MA_{50}(V)_t \ge 1.20\}\).

Volume confirmation score: \(S^{VOL}_t=clip(0.25\,BRK_t+1.00\,FTD_t-0.35\,DIST_t-0.75\,HDIST_t-0.25\,CLUST_t,-1,1)\), where \(BRK_t=1\{r^{SPY}_t>0, V_t/MA_{50}(V)_t \ge 1.10\}\) and \(CLUST_t=1\{\sum_{i=0}^{24}DIST_{t-i}\ge4\}\).

Base regime score: \(S^{BASE}_t\) is the existing price-only composite in \([-1,1]\), averaging the VIX proxy, SPY trend, market breadth, volatility regime, and cross-sectional momentum indicators.

Final v3 regime score: \(S^{V3}_t=clip((1-\lambda)S^{BASE}_t+\lambda S^{VOL}_t,-1,1)\).

Final exposure scale: \(x^{BASE}_t=clip((S^{BASE}_t+1)/2,0,1)\) and \(x^{V3}_t=clip((S^{V3}_t+1)/2,0,1)\).

Execution lag and portfolio weights: all indicators using \(P_t\), \(L_t\), or \(V_t\) are only applied to weights for the next return period. Thus \(w_t=f(x_t,\mathcal{I}_t)\) is computed after date \(t\) information is observable, and earns asset returns \(R_{t+1}\), not \(R_t\).

Portfolio return: \(R^{p}_{t+1}=w_t^\top R_{t+1}-TC_{t+1}\), where transaction cost scenarios use \(TC_{t+1}=c\sum_i |w_{i,t}-w_{i,t-1}|\) for \(c\in\{0,5,10,20\}\) basis points.

Opportunity cost: because the FTD layer is low frequency, it is evaluated not only by drawdown reduction but also by missed upside. When v3 is more defensive than base, \(OC_{t+1}=\max(x^{BASE}_t-x^{V3}_t,0)\max(R^{RP}_{t+1},0)\) and \(LA_{t+1}=\max(x^{BASE}_t-x^{V3}_t,0)\max(-R^{RP}_{t+1},0)\). The net defensive timing benefit is \(\sum LA-\sum OC\).

When v3 takes more risk than base, \(UC_{t+1}=\max(x^{V3}_t-x^{BASE}_t,0)\max(R^{RP}_{t+1},0)\) and \(EL_{t+1}=\max(x^{V3}_t-x^{BASE}_t,0)\max(-R^{RP}_{t+1},0)\). These terms separate additional upside captured from extra downside loss.

Base vs v3 evaluation metrics: compare `base_price_only` and `price_plus_spy_volume_confirmation` on Sharpe, Calmar, CAGR, total return, annual volatility, win rate, and Max Drawdown. The primary validation criteria are Max Drawdown and Calmar, including full-sample, in-sample, out-of-sample, transaction-cost sensitivity, and parameter-sensitivity results.

## 4. Timing and look-ahead bias control
Signals are computed on `signal_date` from close and volume data observable at that date. Portfolio returns use the next tradable period, recorded as `next_return_date` in `macro_v3_diagnostics.csv`; same-day signals are never applied to same-day returns.

## 5. Base vs v3 comparison
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_price_only | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 |
| price_plus_spy_volume_confirmation | 0.8960 | 0.6550 | 0.0868 | 1.3917 | -0.1345 | 0.0983 | 0.5187 | 0.0581 | 239166.5400 | 2641 |

## 6. Benchmark comparison
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| spy_buy_hold | 0.6960 | 0.3310 | 0.1105 | 1.9978 | -0.3614 | 0.1721 | 0.5515 | 0.0000 | 299782.3200 | 2640 |
| equal_weight_10_stock | 0.8910 | 0.4960 | 0.1664 | 4.0164 | -0.3483 | 0.1940 | 0.5282 | 0.0004 | 501642.6200 | 2641 |
| risk_parity_no_overlay | 0.8580 | 0.4620 | 0.1509 | 3.3621 | -0.3410 | 0.1836 | 0.5271 | 0.0058 | 436205.1800 | 2641 |
| base_price_only | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 |
| price_plus_spy_volume_confirmation | 0.8960 | 0.6550 | 0.0868 | 1.3917 | -0.1345 | 0.0983 | 0.5187 | 0.0581 | 239166.5400 | 2641 |

## 7. Transaction cost sensitivity
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days | cost_bps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| spy_buy_hold | 0.6960 | 0.3310 | 0.1105 | 1.9978 | -0.3614 | 0.1721 | 0.5515 | 0.0000 | 299782.3200 | 2640 | 0.0000 |
| equal_weight_10_stock | 0.8910 | 0.4960 | 0.1664 | 4.0189 | -0.3483 | 0.1940 | 0.5282 | 0.0004 | 501893.5700 | 2641 | 0.0000 |
| risk_parity_no_overlay | 0.8620 | 0.4640 | 0.1517 | 3.3958 | -0.3408 | 0.1836 | 0.5275 | 0.0058 | 439575.4500 | 2641 | 0.0000 |
| base_price_only | 0.9980 | 0.7550 | 0.1055 | 1.8622 | -0.1404 | 0.1062 | 0.5176 | 0.0506 | 286223.6500 | 2641 | 0.0000 |
| price_plus_spy_volume_confirmation | 0.9710 | 0.7220 | 0.0947 | 1.5824 | -0.1321 | 0.0982 | 0.5233 | 0.0581 | 258236.3500 | 2641 | 0.0000 |
| spy_buy_hold | 0.6960 | 0.3310 | 0.1105 | 1.9978 | -0.3614 | 0.1721 | 0.5515 | 0.0000 | 299782.3200 | 2640 | 5.0000 |
| equal_weight_10_stock | 0.8910 | 0.4960 | 0.1664 | 4.0164 | -0.3483 | 0.1940 | 0.5282 | 0.0004 | 501642.6200 | 2641 | 5.0000 |
| risk_parity_no_overlay | 0.8580 | 0.4620 | 0.1509 | 3.3621 | -0.3410 | 0.1836 | 0.5271 | 0.0058 | 436205.1800 | 2641 | 5.0000 |
| base_price_only | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 | 5.0000 |
| price_plus_spy_volume_confirmation | 0.8960 | 0.6550 | 0.0868 | 1.3917 | -0.1345 | 0.0983 | 0.5187 | 0.0581 | 239166.5400 | 2641 | 5.0000 |
| spy_buy_hold | 0.6960 | 0.3310 | 0.1105 | 1.9978 | -0.3614 | 0.1721 | 0.5515 | 0.0000 | 299782.3200 | 2640 | 10.0000 |
| equal_weight_10_stock | 0.8910 | 0.4960 | 0.1663 | 4.0139 | -0.3483 | 0.1940 | 0.5282 | 0.0004 | 501391.6700 | 2641 | 10.0000 |
| risk_parity_no_overlay | 0.8540 | 0.4600 | 0.1501 | 3.3286 | -0.3411 | 0.1836 | 0.5271 | 0.0058 | 432860.5900 | 2641 | 10.0000 |
| base_price_only | 0.8780 | 0.6460 | 0.0915 | 1.5040 | -0.1445 | 0.1063 | 0.5115 | 0.0506 | 250395.3800 | 2641 | 10.0000 |
| price_plus_spy_volume_confirmation | 0.8210 | 0.5900 | 0.0788 | 1.2150 | -0.1369 | 0.0983 | 0.5157 | 0.0581 | 221503.4600 | 2641 | 10.0000 |
| spy_buy_hold | 0.6960 | 0.3310 | 0.1105 | 1.9978 | -0.3614 | 0.1721 | 0.5515 | 0.0000 | 299782.3200 | 2640 | 20.0000 |
| equal_weight_10_stock | 0.8900 | 0.4960 | 0.1662 | 4.0089 | -0.3483 | 0.1940 | 0.5282 | 0.0004 | 500889.7800 | 2641 | 20.0000 |
| risk_parity_no_overlay | 0.8460 | 0.4550 | 0.1484 | 3.2625 | -0.3414 | 0.1836 | 0.5267 | 0.0058 | 426247.6900 | 2641 | 20.0000 |
| base_price_only | 0.7570 | 0.5420 | 0.0777 | 1.1905 | -0.1485 | 0.1064 | 0.5066 | 0.0506 | 219045.5500 | 2641 | 20.0000 |
| price_plus_spy_volume_confirmation | 0.6720 | 0.4660 | 0.0632 | 0.8999 | -0.1418 | 0.0984 | 0.5097 | 0.0581 | 189990.5200 | 2641 | 20.0000 |

## 8. Out-of-sample results
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days | sample |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| spy_buy_hold | 0.6960 | 0.3310 | 0.1105 | 1.9978 | -0.3614 | 0.1721 | 0.5515 | 0.0000 | 299782.3200 | 2640 | full_sample |
| equal_weight_10_stock | 0.8910 | 0.4960 | 0.1664 | 4.0164 | -0.3483 | 0.1940 | 0.5282 | 0.0004 | 501642.6200 | 2641 | full_sample |
| risk_parity_no_overlay | 0.8580 | 0.4620 | 0.1509 | 3.3621 | -0.3410 | 0.1836 | 0.5271 | 0.0058 | 436205.1800 | 2641 | full_sample |
| base_price_only | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 | full_sample |
| price_plus_spy_volume_confirmation | 0.8960 | 0.6550 | 0.0868 | 1.3917 | -0.1345 | 0.0983 | 0.5187 | 0.0581 | 239166.5400 | 2641 | full_sample |
| spy_buy_hold | 0.8470 | 0.5870 | 0.1175 | 1.2581 | -0.2071 | 0.1434 | 0.5474 | 0.0000 | 225812.6000 | 1847 | in_sample |
| equal_weight_10_stock | 1.1320 | 0.9830 | 0.1793 | 2.3516 | -0.1803 | 0.1566 | 0.5097 | 0.0005 | 335163.6000 | 1848 | in_sample |
| risk_parity_no_overlay | 1.0930 | 1.0170 | 0.1621 | 2.0099 | -0.1585 | 0.1475 | 0.5119 | 0.0061 | 300989.3500 | 1848 | in_sample |
| base_price_only | 1.1200 | 0.8810 | 0.1066 | 1.1014 | -0.1200 | 0.0944 | 0.5000 | 0.0512 | 210142.4100 | 1848 | in_sample |
| price_plus_spy_volume_confirmation | 1.0920 | 0.8280 | 0.0960 | 0.9580 | -0.1153 | 0.0874 | 0.5049 | 0.0580 | 195801.3800 | 1848 | in_sample |
| spy_buy_hold | 0.5130 | 0.3200 | 0.0942 | 0.3276 | -0.3614 | 0.2254 | 0.5612 | 0.0000 | 132757.1300 | 793 | out_of_sample |
| equal_weight_10_stock | 0.6220 | 0.4670 | 0.1367 | 0.4967 | -0.3483 | 0.2612 | 0.5712 | 0.0000 | 149670.9700 | 793 | out_of_sample |
| risk_parity_no_overlay | 0.6000 | 0.4370 | 0.1251 | 0.4492 | -0.3410 | 0.2481 | 0.5624 | 0.0052 | 144923.7900 | 793 | out_of_sample |
| base_price_only | 0.6580 | 0.6000 | 0.0800 | 0.2740 | -0.1425 | 0.1298 | 0.5435 | 0.0492 | 127395.4200 | 793 | out_of_sample |
| price_plus_spy_volume_confirmation | 0.5910 | 0.5260 | 0.0656 | 0.2215 | -0.1345 | 0.1198 | 0.5511 | 0.0584 | 122147.5200 | 793 | out_of_sample |

## 8b. Opportunity cost and timing benefit
This section tests whether defensive exposure reductions create excessive missed upside. A useful low-frequency confirmation layer should avoid more loss than the upside it misses, especially out-of-sample.

| sample | strategy | n_days | derisked_day_count | added_risk_day_count | total_opportunity_cost | total_loss_avoided | net_defensive_timing_benefit | opportunity_cost_ratio | total_upside_captured | total_extra_loss | net_total_timing_benefit | actual_strategy_minus_base_return | derisked_positive_return_hit_rate | derisked_negative_return_hit_rate | added_risk_positive_return_hit_rate | added_risk_negative_return_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_sample | price_plus_spy_volume_confirmation | 2641 | 2322 | 185 | 0.5191 | 0.4338 | -0.0854 | 1.1968 | 0.0429 | 0.0691 | -0.1116 | -0.1214 | 0.5327 | 0.4272 | 0.4865 | 0.4216 |
| in_sample | price_plus_spy_volume_confirmation | 1848 | 1657 | 107 | 0.3365 | 0.2720 | -0.0646 | 1.2374 | 0.0241 | 0.0287 | -0.0692 | -0.0754 | 0.5160 | 0.4303 | 0.4673 | 0.3738 |
| out_of_sample | price_plus_spy_volume_confirmation | 793 | 665 | 78 | 0.1826 | 0.1618 | -0.0208 | 1.1286 | 0.0188 | 0.0404 | -0.0424 | -0.0460 | 0.5744 | 0.4195 | 0.5128 | 0.4872 |

## 9. Parameter sensitivity
| SPY_FTD_MIN_RETURN | SPY_VOLUME_STRONG_BREAKOUT | VOLUME_CONFIRMATION_WEIGHT | sharpe | calmar | max_drawdown | total_return | follow_through_day_count | distribution_day_count | average_final_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0100 | 1.1000 | 0.1000 | 0.9120 | 0.6710 | -0.1371 | 1.4854 | 59 | 566 | 0.6939 |
| 0.0100 | 1.1000 | 0.1500 | 0.8970 | 0.6550 | -0.1345 | 1.3929 | 59 | 566 | 0.6763 |
| 0.0100 | 1.1000 | 0.2000 | 0.8800 | 0.6260 | -0.1345 | 1.3028 | 59 | 566 | 0.6588 |
| 0.0100 | 1.2000 | 0.1000 | 0.9130 | 0.6720 | -0.1371 | 1.4886 | 59 | 566 | 0.6941 |
| 0.0100 | 1.2000 | 0.1500 | 0.8980 | 0.6570 | -0.1345 | 1.3974 | 59 | 566 | 0.6766 |
| 0.0100 | 1.2000 | 0.2000 | 0.8820 | 0.6210 | -0.1359 | 1.3086 | 59 | 566 | 0.6592 |
| 0.0100 | 1.3000 | 0.1000 | 0.9150 | 0.6740 | -0.1372 | 1.4958 | 59 | 566 | 0.6943 |
| 0.0100 | 1.3000 | 0.1500 | 0.9020 | 0.6590 | -0.1345 | 1.4078 | 59 | 566 | 0.6770 |
| 0.0100 | 1.3000 | 0.2000 | 0.8870 | 0.6250 | -0.1359 | 1.3221 | 59 | 566 | 0.6596 |
| 0.0125 | 1.1000 | 0.1000 | 0.9110 | 0.6700 | -0.1371 | 1.4815 | 43 | 566 | 0.6936 |
| 0.0125 | 1.1000 | 0.1500 | 0.8950 | 0.6530 | -0.1345 | 1.3872 | 43 | 566 | 0.6759 |
| 0.0125 | 1.1000 | 0.2000 | 0.8780 | 0.6240 | -0.1345 | 1.2956 | 43 | 566 | 0.6582 |
| 0.0125 | 1.2000 | 0.1000 | 0.9120 | 0.6710 | -0.1371 | 1.4846 | 43 | 566 | 0.6938 |
| 0.0125 | 1.2000 | 0.1500 | 0.8960 | 0.6550 | -0.1345 | 1.3917 | 43 | 566 | 0.6762 |
| 0.0125 | 1.2000 | 0.2000 | 0.8790 | 0.6190 | -0.1359 | 1.3014 | 43 | 566 | 0.6586 |
| 0.0125 | 1.3000 | 0.1000 | 0.9140 | 0.6720 | -0.1372 | 1.4918 | 43 | 566 | 0.6940 |
| 0.0125 | 1.3000 | 0.1500 | 0.9000 | 0.6580 | -0.1345 | 1.4021 | 43 | 566 | 0.6765 |
| 0.0125 | 1.3000 | 0.2000 | 0.8840 | 0.6230 | -0.1359 | 1.3148 | 43 | 566 | 0.6591 |
| 0.0150 | 1.1000 | 0.1000 | 0.9170 | 0.6810 | -0.1355 | 1.4938 | 29 | 566 | 0.6933 |
| 0.0150 | 1.1000 | 0.1500 | 0.9040 | 0.6680 | -0.1325 | 1.4050 | 29 | 566 | 0.6755 |
| 0.0150 | 1.1000 | 0.2000 | 0.8900 | 0.6300 | -0.1345 | 1.3186 | 29 | 566 | 0.6577 |
| 0.0150 | 1.2000 | 0.1000 | 0.9170 | 0.6820 | -0.1355 | 1.4969 | 29 | 566 | 0.6935 |
| 0.0150 | 1.2000 | 0.1500 | 0.9050 | 0.6640 | -0.1336 | 1.4095 | 29 | 566 | 0.6758 |
| 0.0150 | 1.2000 | 0.2000 | 0.8910 | 0.6260 | -0.1359 | 1.3245 | 29 | 566 | 0.6581 |
| 0.0150 | 1.3000 | 0.1000 | 0.9200 | 0.6840 | -0.1356 | 1.5041 | 29 | 566 | 0.6938 |
| 0.0150 | 1.3000 | 0.1500 | 0.9090 | 0.6680 | -0.1336 | 1.4200 | 29 | 566 | 0.6762 |
| 0.0150 | 1.3000 | 0.2000 | 0.8960 | 0.6300 | -0.1359 | 1.3380 | 29 | 566 | 0.6586 |

## 9b. Base model robustness
Because the volume layer did not add robust incremental value, the final strategy candidate is the simpler price-only macro regime overlay. The following tests evaluate whether the base model itself is robust.

### Base signal ablation
| specification | included_signals | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days | average_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| defensive_4_signal_base | vix_proxy,equity_mom,breadth,vol_regime | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 | 0.7444 |
| without_vix_proxy | equity_mom,breadth,vol_regime | 0.9030 | 0.6770 | 0.0900 | 1.4674 | -0.1348 | 0.1011 | 0.4960 | 0.0625 | 246744.3700 | 2641 | 0.6946 |
| without_equity_mom | vix_proxy,breadth,vol_regime | 0.9430 | 0.7190 | 0.0975 | 1.6506 | -0.1370 | 0.1045 | 0.5131 | 0.0590 | 265059.7600 | 2641 | 0.7118 |
| without_breadth | vix_proxy,equity_mom,vol_regime | 0.9510 | 0.6660 | 0.1047 | 1.8401 | -0.1588 | 0.1112 | 0.5127 | 0.0450 | 284012.9700 | 2641 | 0.7673 |
| without_vol_regime | vix_proxy,equity_mom,breadth | 0.8920 | 0.7340 | 0.1004 | 1.7259 | -0.1395 | 0.1147 | 0.5059 | 0.0408 | 272585.1100 | 2641 | 0.8038 |
| legacy_5_signal_with_cross_mom | vix_proxy,equity_mom,breadth,vol_regime,cross_mom | 0.9140 | 0.6280 | 0.1017 | 1.7586 | -0.1644 | 0.1129 | 0.5237 | 0.0443 | 275855.5600 | 2641 | 0.7723 |

### Base parameter sensitivity
| MA_LONG | BREADTH_MA | VOL_SHORT | VOL_LONG | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | avg_daily_turnover | average_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 150 | 40 | 10 | 30 | 0.8640 | 0.6400 | 0.0899 | 1.4645 | -0.1434 | 0.1062 | 0.0577 | 0.7378 |
| 150 | 40 | 10 | 60 | 0.8420 | 0.6680 | 0.0881 | 1.4229 | -0.1350 | 0.1072 | 0.0566 | 0.7509 |
| 150 | 40 | 15 | 30 | 0.8950 | 0.6680 | 0.0923 | 1.5221 | -0.1403 | 0.1048 | 0.0574 | 0.7262 |
| 150 | 40 | 15 | 60 | 0.8860 | 0.7610 | 0.0925 | 1.5261 | -0.1237 | 0.1063 | 0.0521 | 0.7410 |
| 150 | 50 | 10 | 30 | 0.8750 | 0.6620 | 0.0907 | 1.4829 | -0.1396 | 0.1056 | 0.0560 | 0.7389 |
| 150 | 50 | 10 | 60 | 0.8520 | 0.7030 | 0.0889 | 1.4415 | -0.1292 | 0.1067 | 0.0546 | 0.7519 |
| 150 | 50 | 15 | 30 | 0.9060 | 0.7030 | 0.0931 | 1.5411 | -0.1343 | 0.1042 | 0.0557 | 0.7272 |
| 150 | 50 | 15 | 60 | 0.8950 | 0.7730 | 0.0932 | 1.5444 | -0.1225 | 0.1058 | 0.0505 | 0.7420 |
| 150 | 60 | 10 | 30 | 0.8410 | 0.6180 | 0.0875 | 1.4090 | -0.1449 | 0.1065 | 0.0541 | 0.7410 |
| 150 | 60 | 10 | 60 | 0.8190 | 0.6640 | 0.0858 | 1.3686 | -0.1327 | 0.1076 | 0.0528 | 0.7541 |
| 150 | 60 | 15 | 30 | 0.8710 | 0.6630 | 0.0898 | 1.4624 | -0.1381 | 0.1051 | 0.0547 | 0.7294 |
| 150 | 60 | 15 | 60 | 0.8610 | 0.7250 | 0.0899 | 1.4660 | -0.1267 | 0.1067 | 0.0494 | 0.7441 |
| 200 | 40 | 10 | 30 | 0.9270 | 0.6730 | 0.0977 | 1.6568 | -0.1471 | 0.1068 | 0.0524 | 0.7433 |
| 200 | 40 | 10 | 60 | 0.9050 | 0.7070 | 0.0960 | 1.6135 | -0.1380 | 0.1078 | 0.0509 | 0.7564 |
| 200 | 40 | 15 | 30 | 0.9580 | 0.7290 | 0.1002 | 1.7198 | -0.1387 | 0.1055 | 0.0519 | 0.7317 |
| 200 | 40 | 15 | 60 | 0.9480 | 0.8100 | 0.1003 | 1.7236 | -0.1252 | 0.1069 | 0.0468 | 0.7465 |
| 200 | 50 | 10 | 30 | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.0506 | 0.7444 |
| 200 | 50 | 10 | 60 | 0.9150 | 0.7370 | 0.0968 | 1.6333 | -0.1331 | 0.1073 | 0.0491 | 0.7574 |
| 200 | 50 | 15 | 30 | 0.9700 | 0.8110 | 0.1010 | 1.7407 | -0.1254 | 0.1049 | 0.0501 | 0.7327 |
| 200 | 50 | 15 | 60 | 0.9580 | 0.8310 | 0.1011 | 1.7431 | -0.1228 | 0.1064 | 0.0453 | 0.7475 |
| 200 | 60 | 10 | 30 | 0.9040 | 0.6580 | 0.0953 | 1.5964 | -0.1471 | 0.1071 | 0.0490 | 0.7465 |
| 200 | 60 | 10 | 60 | 0.8820 | 0.6910 | 0.0936 | 1.5534 | -0.1380 | 0.1081 | 0.0477 | 0.7596 |
| 200 | 60 | 15 | 30 | 0.9340 | 0.7690 | 0.0977 | 1.6555 | -0.1285 | 0.1058 | 0.0492 | 0.7349 |
| 200 | 60 | 15 | 60 | 0.9240 | 0.7650 | 0.0978 | 1.6582 | -0.1295 | 0.1073 | 0.0443 | 0.7496 |
| 250 | 40 | 10 | 30 | 0.9470 | 0.7160 | 0.1007 | 1.7346 | -0.1421 | 0.1074 | 0.0516 | 0.7448 |
| 250 | 40 | 10 | 60 | 0.9260 | 0.7340 | 0.0990 | 1.6903 | -0.1367 | 0.1084 | 0.0500 | 0.7579 |
| 250 | 40 | 15 | 30 | 0.9790 | 0.7050 | 0.1032 | 1.7998 | -0.1475 | 0.1061 | 0.0509 | 0.7332 |
| 250 | 40 | 15 | 60 | 0.9690 | 0.8420 | 0.1034 | 1.8037 | -0.1237 | 0.1075 | 0.0459 | 0.7480 |
| 250 | 50 | 10 | 30 | 0.9580 | 0.7790 | 0.1015 | 1.7552 | -0.1315 | 0.1069 | 0.0499 | 0.7459 |
| 250 | 50 | 10 | 60 | 0.9360 | 0.7840 | 0.0998 | 1.7107 | -0.1288 | 0.1079 | 0.0482 | 0.7589 |
| 250 | 50 | 15 | 30 | 0.9910 | 0.7790 | 0.1040 | 1.8213 | -0.1343 | 0.1056 | 0.0491 | 0.7342 |
| 250 | 50 | 15 | 60 | 0.9790 | 0.8560 | 0.1041 | 1.8237 | -0.1225 | 0.1071 | 0.0443 | 0.7490 |
| 250 | 60 | 10 | 30 | 0.9250 | 0.7310 | 0.0983 | 1.6722 | -0.1363 | 0.1077 | 0.0482 | 0.7480 |
| 250 | 60 | 10 | 60 | 0.9030 | 0.7410 | 0.0966 | 1.6285 | -0.1324 | 0.1088 | 0.0467 | 0.7611 |
| 250 | 60 | 15 | 30 | 0.9550 | 0.7400 | 0.1007 | 1.7336 | -0.1373 | 0.1064 | 0.0482 | 0.7364 |
| 250 | 60 | 15 | 60 | 0.9440 | 0.8460 | 0.1008 | 1.7364 | -0.1204 | 0.1079 | 0.0433 | 0.7511 |

### Base subperiod metrics
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days | period |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| spy_buy_hold | 0.7720 | 0.5600 | 0.1103 | 0.9720 | -0.2071 | 0.1504 | 0.5443 | 0.0000 | 197198.3200 | 1635 | 2010_2016 |
| risk_parity_no_overlay | 0.9440 | 0.9130 | 0.1422 | 1.3700 | -0.1585 | 0.1534 | 0.5018 | 0.0062 | 237000.8700 | 1636 | 2010_2016 |
| base_price_only | 0.9420 | 0.7540 | 0.0896 | 0.7458 | -0.1200 | 0.0960 | 0.4884 | 0.0532 | 174579.2000 | 1636 | 2010_2016 |
| spy_buy_hold | 0.6210 | 0.3480 | 0.1107 | 0.5202 | -0.3614 | 0.2027 | 0.5632 | 0.0000 | 152020.7300 | 1005 | 2017_2020 |
| risk_parity_no_overlay | 0.7950 | 0.5230 | 0.1653 | 0.8405 | -0.3410 | 0.2243 | 0.5682 | 0.0053 | 184052.1400 | 1005 | 2017_2020 |
| base_price_only | 0.9460 | 0.8050 | 0.1132 | 0.5335 | -0.1425 | 0.1211 | 0.5532 | 0.0464 | 153346.9100 | 1005 | 2017_2020 |

### Base opportunity cost versus no-overlay risk parity
| sample | n_days | derisked_day_count | total_opportunity_cost | total_loss_avoided | net_defensive_timing_benefit | opportunity_cost_ratio | actual_base_minus_no_overlay_return | derisked_positive_return_hit_rate | derisked_negative_return_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_sample | 2641 | 1755 | 3.8398 | 3.2924 | -0.5474 | 1.1663 | -0.6066 | 0.5168 | 0.4142 |
| in_sample | 1848 | 1252 | 2.0917 | 1.7267 | -0.3650 | 1.2114 | -0.4067 | 0.4928 | 0.4105 |
| out_of_sample | 793 | 503 | 1.7481 | 1.5657 | -0.1825 | 1.1165 | -0.1999 | 0.5765 | 0.4235 |

## 9c. Cross-momentum exclusion test
Ablation suggested that the 12-1 month cross-momentum component may be too slow for a drawdown-control overlay. This section formally compares the full base model against a defensive four-signal version that excludes cross momentum.

### Full-sample comparison
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_price_only | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 |
| legacy_5_signal_with_cross_mom | 0.9140 | 0.6280 | 0.1017 | 1.7586 | -0.1644 | 0.1129 | 0.5237 | 0.0443 | 275855.5600 | 2641 |

### OOS comparison
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days | sample |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_price_only | 0.9380 | 0.6990 | 0.0985 | 1.6771 | -0.1425 | 0.1062 | 0.5131 | 0.0506 | 267711.7900 | 2641 | full_sample |
| legacy_5_signal_with_cross_mom | 0.9140 | 0.6280 | 0.1017 | 1.7586 | -0.1644 | 0.1129 | 0.5237 | 0.0443 | 275855.5600 | 2641 | full_sample |
| base_price_only | 1.1200 | 0.8810 | 0.1066 | 1.1014 | -0.1200 | 0.0944 | 0.5000 | 0.0512 | 210142.4100 | 1848 | in_sample |
| legacy_5_signal_with_cross_mom | 1.1380 | 1.0120 | 0.1133 | 1.1970 | -0.1108 | 0.0986 | 0.5087 | 0.0438 | 219699.5600 | 1848 | in_sample |
| base_price_only | 0.6580 | 0.6000 | 0.0800 | 0.2740 | -0.1425 | 0.1298 | 0.5435 | 0.0492 | 127395.4200 | 793 | out_of_sample |
| legacy_5_signal_with_cross_mom | 0.5850 | 0.5010 | 0.0750 | 0.2556 | -0.1644 | 0.1408 | 0.5586 | 0.0454 | 125560.3600 | 793 | out_of_sample |

### Subperiod comparison
| strategy | sharpe | calmar | cagr | total_return | max_drawdown | annual_vol | win_rate | avg_daily_turnover | final_capital | n_days | period |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_price_only | 0.9420 | 0.7540 | 0.0896 | 0.7458 | -0.1200 | 0.0960 | 0.4884 | 0.0532 | 174579.2000 | 1636 | 2010_2016 |
| legacy_5_signal_with_cross_mom | 0.9570 | 0.8670 | 0.0953 | 0.8057 | -0.1108 | 0.1004 | 0.4982 | 0.0457 | 180565.0000 | 1636 | 2010_2016 |
| base_price_only | 0.9460 | 0.8050 | 0.1132 | 0.5335 | -0.1425 | 0.1211 | 0.5532 | 0.0464 | 153346.9100 | 1005 | 2017_2020 |
| legacy_5_signal_with_cross_mom | 0.8790 | 0.6990 | 0.1121 | 0.5277 | -0.1644 | 0.1307 | 0.5652 | 0.0420 | 152773.5500 | 1005 | 2017_2020 |

### Drawdown episode analysis
| episode | start_date | end_date | n_days | spy_min_drawdown | avg_scale_with_cross_mom | avg_scale_without_cross_mom | avg_scale_diff_without_minus_with | days_without_cross_more_defensive | days_without_cross_less_defensive | first_more_defensive_date | legacy_with_cross_episode_return | without_cross_episode_return | legacy_with_cross_episode_max_drawdown | without_cross_episode_max_drawdown |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2010-05-20 00:00:00+00:00 | 2010-05-26 00:00:00+00:00 | 5 | -0.1202 | 0.3200 | 0.2750 | -0.0450 | 2 | 0 | 2010-05-20 00:00:00+00:00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 2 | 2010-05-28 00:00:00+00:00 | 2010-06-01 00:00:00+00:00 | 2 | -0.1172 | 0.1000 | 0.0000 | -0.1000 | 2 | 0 | 2010-05-28 00:00:00+00:00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 3 | 2010-06-04 00:00:00+00:00 | 2010-06-10 00:00:00+00:00 | 5 | -0.1340 | 0.1400 | 0.0500 | -0.0900 | 5 | 0 | 2010-06-04 00:00:00+00:00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 4 | 2010-06-14 00:00:00+00:00 | 2010-06-14 00:00:00+00:00 | 1 | -0.1010 | 0.4000 | 0.3750 | -0.0250 | 0 | 0 | nan | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 5 | 2010-06-22 00:00:00+00:00 | 2010-07-12 00:00:00+00:00 | 14 | -0.1610 | 0.3714 | 0.3393 | -0.0321 | 2 | 0 | 2010-07-08 00:00:00+00:00 | -0.0005 | -0.0006 | -0.0003 | -0.0004 |
| 6 | 2010-07-16 00:00:00+00:00 | 2010-07-22 00:00:00+00:00 | 5 | -0.1244 | 0.3200 | 0.2750 | -0.0450 | 2 | 0 | 2010-07-19 00:00:00+00:00 | -0.0002 | -0.0002 | -0.0002 | -0.0002 |
| 7 | 2010-08-11 00:00:00+00:00 | 2010-08-17 00:00:00+00:00 | 5 | -0.1112 | 0.4600 | 0.4500 | -0.0100 | 0 | 0 | nan | -0.0001 | -0.0001 | -0.0001 | -0.0001 |
| 8 | 2010-08-19 00:00:00+00:00 | 2010-09-02 00:00:00+00:00 | 11 | -0.1361 | 0.4545 | 0.4432 | -0.0114 | 1 | 0 | 2010-09-02 00:00:00+00:00 | -0.0001 | -0.0002 | -0.0001 | -0.0002 |
| 9 | 2011-08-04 00:00:00+00:00 | 2011-10-20 00:00:00+00:00 | 55 | -0.1942 | 0.2818 | 0.2273 | -0.0545 | 20 | 0 | 2011-08-04 00:00:00+00:00 | -0.0050 | -0.0108 | -0.0387 | -0.0354 |
| 10 | 2011-11-01 00:00:00+00:00 | 2011-11-01 00:00:00+00:00 | 1 | -0.1058 | 0.4000 | 0.3750 | -0.0250 | 0 | 0 | nan | 0.0029 | 0.0027 | 0.0000 | 0.0000 |
| 11 | 2011-11-17 00:00:00+00:00 | 2011-11-29 00:00:00+00:00 | 8 | -0.1473 | 0.4125 | 0.3906 | -0.0219 | 0 | 0 | nan | 0.0101 | 0.0101 | -0.0186 | -0.0180 |
| 12 | 2011-12-14 00:00:00+00:00 | 2011-12-19 00:00:00+00:00 | 4 | -0.1183 | 0.5000 | 0.5000 | 0.0000 | 0 | 0 | nan | 0.0129 | 0.0129 | -0.0057 | -0.0057 |
| 13 | 2015-08-24 00:00:00+00:00 | 2015-08-25 00:00:00+00:00 | 2 | -0.1229 | 0.3000 | 0.1250 | -0.1750 | 2 | 0 | 2015-08-24 00:00:00+00:00 | 0.0135 | 0.0056 | 0.0000 | 0.0000 |
| 14 | 2015-09-01 00:00:00+00:00 | 2015-09-01 00:00:00+00:00 | 1 | -0.1018 | 0.3000 | 0.1250 | -0.1750 | 1 | 0 | 2015-09-01 00:00:00+00:00 | 0.0070 | 0.0029 | 0.0000 | 0.0000 |
| 15 | 2015-09-28 00:00:00+00:00 | 2015-10-01 00:00:00+00:00 | 4 | -0.1194 | 0.5250 | 0.4062 | -0.1187 | 4 | 0 | 2015-09-28 00:00:00+00:00 | 0.0194 | 0.0152 | 0.0000 | 0.0000 |
| 16 | 2016-01-08 00:00:00+00:00 | 2016-01-11 00:00:00+00:00 | 2 | -0.1011 | 0.6000 | 0.5000 | -0.1000 | 2 | 0 | 2016-01-08 00:00:00+00:00 | 0.0075 | 0.0062 | 0.0000 | 0.0000 |
| 17 | 2016-01-13 00:00:00+00:00 | 2016-01-28 00:00:00+00:00 | 11 | -0.1304 | 0.3364 | 0.1705 | -0.1659 | 11 | 0 | 2016-01-13 00:00:00+00:00 | 0.0181 | 0.0129 | -0.0097 | -0.0041 |
| 18 | 2016-02-02 00:00:00+00:00 | 2016-02-16 00:00:00+00:00 | 10 | -0.1435 | 0.3400 | 0.2250 | -0.1150 | 8 | 2 | 2016-02-02 00:00:00+00:00 | -0.0008 | 0.0056 | -0.0181 | -0.0113 |
| 19 | 2016-02-18 00:00:00+00:00 | 2016-02-19 00:00:00+00:00 | 2 | -0.1007 | 0.4000 | 0.5000 | 0.1000 | 0 | 2 | nan | 0.0076 | 0.0095 | 0.0000 | 0.0000 |
| 20 | 2018-02-08 00:00:00+00:00 | 2018-02-08 00:00:00+00:00 | 1 | -0.1010 | 0.5000 | 0.3750 | -0.1250 | 1 | 0 | 2018-02-08 00:00:00+00:00 | 0.0100 | 0.0075 | 0.0000 | 0.0000 |
| 21 | 2018-04-02 00:00:00+00:00 | 2018-04-02 00:00:00+00:00 | 1 | -0.1016 | 0.3000 | 0.1250 | -0.1750 | 1 | 0 | 2018-04-02 00:00:00+00:00 | 0.0056 | 0.0022 | 0.0000 | 0.0000 |
| 22 | 2018-10-29 00:00:00+00:00 | 2018-10-29 00:00:00+00:00 | 1 | -0.1012 | 0.3000 | 0.1250 | -0.1750 | 1 | 0 | 2018-10-29 00:00:00+00:00 | 0.0050 | 0.0021 | 0.0000 | 0.0000 |
| 23 | 2018-11-20 00:00:00+00:00 | 2018-11-20 00:00:00+00:00 | 1 | -0.1003 | 0.5000 | 0.3750 | -0.1250 | 1 | 0 | 2018-11-20 00:00:00+00:00 | -0.0014 | -0.0011 | 0.0000 | 0.0000 |
| 24 | 2018-11-23 00:00:00+00:00 | 2018-11-23 00:00:00+00:00 | 1 | -0.1033 | 0.6000 | 0.5000 | -0.1000 | 1 | 0 | 2018-11-23 00:00:00+00:00 | 0.0129 | 0.0107 | 0.0000 | 0.0000 |
| 25 | 2018-12-07 00:00:00+00:00 | 2018-12-11 00:00:00+00:00 | 3 | -0.1022 | 0.3000 | 0.1250 | -0.1750 | 3 | 0 | 2018-12-07 00:00:00+00:00 | 0.0016 | 0.0007 | 0.0000 | 0.0000 |
| 26 | 2018-12-14 00:00:00+00:00 | 2019-01-17 00:00:00+00:00 | 23 | -0.2018 | 0.2739 | 0.1902 | -0.0837 | 14 | 3 | 2018-12-14 00:00:00+00:00 | -0.0155 | 0.0019 | -0.0407 | -0.0289 |
| 27 | 2019-01-22 00:00:00+00:00 | 2019-01-24 00:00:00+00:00 | 3 | -0.1046 | 0.5000 | 0.6250 | 0.1250 | 0 | 3 | nan | 0.0064 | 0.0080 | 0.0000 | 0.0000 |
| 28 | 2019-01-28 00:00:00+00:00 | 2019-01-29 00:00:00+00:00 | 2 | -0.1028 | 0.5500 | 0.6875 | 0.1375 | 0 | 2 | nan | 0.0077 | 0.0097 | 0.0000 | 0.0000 |
| 29 | 2020-02-27 00:00:00+00:00 | 2020-02-28 00:00:00+00:00 | 2 | -0.1244 | 0.3000 | 0.1250 | -0.1750 | 2 | 0 | 2020-02-27 00:00:00+00:00 | 0.0156 | 0.0064 | 0.0000 | 0.0000 |
| 30 | 2020-03-03 00:00:00+00:00 | 2020-03-03 00:00:00+00:00 | 1 | -0.1126 | 0.2000 | 0.0000 | -0.2000 | 1 | 0 | 2020-03-03 00:00:00+00:00 | 0.0087 | -0.0002 | 0.0000 | 0.0000 |
| 31 | 2020-03-05 00:00:00+00:00 | 2020-05-29 00:00:00+00:00 | 60 | -0.3410 | 0.4050 | 0.3438 | -0.0612 | 36 | 16 | 2020-03-05 00:00:00+00:00 | 0.0432 | 0.0719 | -0.0471 | -0.0233 |
| 32 | 2020-06-11 00:00:00+00:00 | 2020-06-12 00:00:00+00:00 | 2 | -0.1115 | 0.6000 | 0.5000 | -0.1000 | 2 | 0 | 2020-06-11 00:00:00+00:00 | 0.0094 | 0.0076 | 0.0000 | 0.0000 |
| 33 | 2020-06-24 00:00:00+00:00 | 2020-06-24 00:00:00+00:00 | 1 | -0.1012 | 0.6000 | 0.5000 | -0.1000 | 1 | 0 | 2020-06-24 00:00:00+00:00 | 0.0080 | 0.0066 | 0.0000 | 0.0000 |
| 34 | 2020-06-26 00:00:00+00:00 | 2020-06-29 00:00:00+00:00 | 2 | -0.1132 | 0.5500 | 0.4375 | -0.1125 | 2 | 0 | 2020-06-26 00:00:00+00:00 | 0.0163 | 0.0132 | 0.0000 | 0.0000 |

### Opportunity cost of excluding cross momentum
| sample | strategy | n_days | derisked_day_count | added_risk_day_count | total_opportunity_cost | total_loss_avoided | net_defensive_timing_benefit | opportunity_cost_ratio | total_upside_captured | total_extra_loss | net_total_timing_benefit | actual_strategy_minus_base_return | derisked_positive_return_hit_rate | derisked_negative_return_hit_rate | added_risk_positive_return_hit_rate | added_risk_negative_return_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_sample | base_price_only | 2641 | 1431 | 299 | 0.6030 | 0.5362 | -0.0668 | 1.1245 | 0.1059 | 0.0684 | -0.0292 | -0.0376 | 0.5430 | 0.4375 | 0.4749 | 0.3478 |
| in_sample | base_price_only | 1848 | 979 | 235 | 0.3010 | 0.2403 | -0.0607 | 1.2525 | 0.0599 | 0.0398 | -0.0406 | -0.0474 | 0.5322 | 0.4392 | 0.4383 | 0.3362 |
| out_of_sample | base_price_only | 793 | 452 | 64 | 0.3020 | 0.2959 | -0.0061 | 1.0205 | 0.0460 | 0.0286 | 0.0114 | 0.0098 | 0.5664 | 0.4336 | 0.6094 | 0.3906 |

## Signal frequency and scale diagnostics
| follow_through_day_count | follow_through_day_annualized | distribution_day_count | distribution_day_annualized | heavy_distribution_day_count | heavy_distribution_day_annualized | volume_confirmation_mean | volume_confirmation_std | volume_confirmation_min | volume_confirmation_max | final_scale_mean | final_scale_std | final_scale_min | final_scale_max | final_scale_below_50pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 43 | 3.9100 | 566 | 51.5300 | 184 | 16.7500 | -0.2456 | 0.3112 | -1.0000 | 1.0000 | 0.6762 | 0.2274 | 0.0000 | 1.0000 | 0.2204 |

## 10. Conclusion
The SPY volume-confirmation layer did not add clear incremental value beyond the base price regime model under this tested design.