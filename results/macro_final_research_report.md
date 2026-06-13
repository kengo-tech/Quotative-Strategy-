# QF621 Macro Regime Trader: Final Research Report Draft

## Executive Summary

This project tests whether a long-only equity portfolio can improve drawdown control by adjusting total equity exposure according to observable macro-regime conditions. The final strategy is a Defensive 4-Signal Macro Regime Overlay using:

1. VIX proxy from SPY realized volatility
2. SPY trend versus long-term moving average
3. Market breadth across a representative liquid-stock universe
4. Volatility regime from short-term versus long-term SPY volatility

The strategy does not forecast individual stock returns. It scales exposure to an inverse-volatility risk-parity stock basket based on market-level risk conditions. Cross momentum and SPY volume confirmation were tested as extensions but excluded from the final specification because they did not improve the drawdown-focused objective robustly. The final implementation uses scale-change-only rebalancing as the main specification, with weekly rebalancing retained as a conservative low-turnover variant.

## Research Question

Can a price-based macro regime overlay improve equity exposure timing and reduce drawdowns relative to buy-and-hold and no-overlay risk parity?

The final implementation question is:

Can the defensive 4-signal overlay preserve drawdown control while avoiding unnecessary daily rebalancing?

## Strategy Design

Each trading date \(t\), the model computes four price-based regime indicators:

- VIX proxy: SPY realized volatility is risk-on when volatility is low and risk-off when volatility is high.
- SPY trend: SPY above its long-term moving average is risk-on; below it is risk-off.
- Market breadth: a high share of stocks above their moving averages is risk-on; weak breadth is risk-off.
- Volatility regime: short-term volatility above long-term volatility indicates stress.

Each component is mapped to \(+1\), \(0\), or \(-1\). The price composite is the average:

\[
S_t = \frac{1}{4}\sum_{j=1}^{4}s_{j,t}
\]

The portfolio exposure scale is:

\[
x_t = clip((S_t+1)/2, 0, 1)
\]

The stock basket is constructed using inverse-volatility risk parity. The final portfolio weight is:

\[
w_{i,t} = x_t \cdot w^{RP}_{i,t}
\]

Signals observed on date \(t\) are applied only to the next tradable return period. The backtest therefore does not use same-day close or volume information to earn same-day returns.

## Hypothesis Evolution

The project started from a five-signal price-based macro regime model. Ablation testing showed that 12-1 month cross-sectional momentum increased drawdown and reduced Calmar in this use case. The interpretation is that cross momentum can be too slow for a defensive risk-management overlay and may dilute faster stress indicators.

The SPY volume-confirmation layer tested whether Follow-Through Days and distribution signals added incremental risk-management value. That extension did not improve the final drawdown-focused objective robustly. In the final price-only run, the volume layer is excluded.

The final model is therefore simpler:

- Include VIX proxy, SPY trend, breadth, and volatility regime
- Exclude cross momentum
- Exclude SPY volume confirmation from the final specification
- Use scale-change-only rebalancing as the main implementation

## Final Benchmark Results

| Strategy | Sharpe | Calmar | CAGR | Max Drawdown | Annual Vol | Avg Daily Turnover |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY buy-and-hold | 0.696 | 0.331 | 11.05% | -36.14% | 17.21% | 0.00% |
| Equal-weight stock basket | 0.920 | 0.564 | 18.52% | -34.04% | 20.85% | 0.04% |
| Risk parity without overlay | 0.855 | 0.460 | 15.02% | -34.10% | 18.36% | 1.03% |
| Final defensive 4-signal overlay | 0.957 | 0.719 | 10.11% | -14.18% | 10.66% | 4.73% |

The final overlay gives up some upside relative to fully invested equity baskets, but it materially reduces Max Drawdown and annualized volatility. Since this is a risk-management overlay, Max Drawdown and Calmar are the primary KPIs.

## Cross Momentum Test

| Specification | Sharpe | Calmar | CAGR | Max Drawdown | Annual Vol |
| --- | ---: | ---: | ---: | ---: | ---: |
| Defensive 4-signal base | 0.957 | 0.719 | 10.11% | -14.18% | 10.66% |
| Legacy 5-signal model with cross momentum | 0.928 | 0.640 | 10.34% | -16.38% | 11.29% |

Cross momentum slightly increased CAGR, but worsened Max Drawdown and Calmar. Because the research objective is drawdown control rather than return maximization, the final strategy excludes cross momentum.

## Rebalancing Policy Robustness

The main implementation question was whether daily rebalancing is necessary. Three policies were tested:

- Daily: refresh target weights every day
- Weekly: refresh target weights once per week
- Scale-change-only: refresh target weights only when the regime scale changes

| Policy | Sharpe | Calmar | CAGR | Max Drawdown | Avg Daily Turnover | Trade Days/Year |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Daily | 0.935 | 0.697 | 9.82% | -14.25% | 5.30% | 239.12 |
| Weekly | 0.836 | 0.671 | 8.92% | -13.63% | 2.85% | 50.67 |
| Scale-change-only | 0.957 | 0.719 | 10.11% | -14.18% | 4.73% | 63.17 |

Scale-change-only is the main specification because it best matches the strategy's economic rationale: trade when market-level exposure changes, not when small daily risk-parity estimates drift. Weekly rebalancing is retained as a conservative implementation variant because it materially reduces turnover.

## OOS Rebalancing Results

| Policy | Sample | Sharpe | Calmar | CAGR | Max Drawdown | Avg Daily Turnover |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Weekly | Out-of-sample | 0.631 | 0.612 | 7.75% | -13.63% | 2.83% |
| Scale-change-only | Out-of-sample | 0.659 | 0.605 | 8.04% | -14.18% | 4.62% |

Out-of-sample, weekly rebalancing has slightly better Calmar and lower turnover, while scale-change-only has slightly higher Sharpe and CAGR. This supports using scale-change-only as the main research specification and weekly as a lower-turnover conservative variant.

## Transaction Cost Sensitivity

| Policy | Cost | Sharpe | Calmar | CAGR | Max Drawdown |
| --- | ---: | ---: | ---: | ---: | ---: |
| Scale-change-only | 0 bps | 1.013 | 0.772 | 10.77% | -13.99% |
| Scale-change-only | 5 bps | 0.957 | 0.719 | 10.11% | -14.18% |
| Scale-change-only | 10 bps | 0.901 | 0.668 | 9.45% | -14.38% |
| Scale-change-only | 20 bps | 0.789 | 0.569 | 8.16% | -14.78% |
| Weekly | 20 bps | 0.737 | 0.585 | 7.75% | -13.79% |

The strategy remains viable under higher transaction-cost assumptions, but weekly rebalancing becomes relatively more attractive in high-cost settings.

## Turnover Attribution

For scale-change-only rebalancing, no trades are triggered by risk-parity updates alone.

| Policy | Trade Reason | Trade Days | Share of Turnover |
| --- | --- | ---: | ---: |
| Scale-change-only | Scale only | 25 | 4.71% |
| Scale-change-only | Risk parity only | 0 | 0.00% |
| Scale-change-only | Scale and risk parity | 629 | 93.79% |

This confirms that the final implementation is not quietly rebalancing every day due to risk-parity drift. It trades when the regime scale changes, and at that time the risk-parity basket is also refreshed.

## Drawdown Episode Evidence

In the 2020 drawdown episode from March 5 to May 29:

| Policy | First Derisk | Days to Derisk | First Re-risk After Minimum | Episode Max Drawdown | Total Turnover |
| --- | --- | ---: | --- | ---: | ---: |
| Daily | 2020-03-05 | 0 | 2020-03-30 | -2.33% | 1.8415 |
| Weekly | 2020-03-09 | 2 | 2020-03-30 | -3.94% | 1.0255 |
| Scale-change-only | 2020-03-05 | 0 | 2020-03-30 | -2.34% | 1.5756 |

Scale-change-only reacted as quickly as daily rebalancing in this major stress episode, while weekly rebalancing lagged by two trading days but used less turnover.

## Limitations

- The local validation dataset is missing META, so the tested trade universe is effectively 9 stocks rather than the intended 10-stock universe.
- The universe is a representative liquid-stock subset, not the full S&P 500.
- The strategy is long-only and does not test short exposure or leverage.
- The backtest uses historical daily data and simplified transaction-cost assumptions.
- The goal is not to optimize parameters for the best backtest result; parameters are treated as pre-specified research definitions and tested for robustness separately.

## Final Conclusion

The final strategy is a Defensive 4-Signal Macro Regime Overlay using VIX proxy, SPY trend, market breadth, and volatility regime. Cross momentum and SPY volume confirmation were tested but excluded because they did not improve the drawdown-focused objective robustly. The final implementation uses scale-change-only rebalancing as the main specification, with weekly rebalancing retained as a conservative low-turnover variant.

The results support the idea that market-level price and volatility regime information can be used to manage long-only equity exposure and materially reduce drawdowns. The strongest claim is not that the model predicts returns, but that it provides a disciplined, transparent framework for reducing equity exposure during adverse regimes.
