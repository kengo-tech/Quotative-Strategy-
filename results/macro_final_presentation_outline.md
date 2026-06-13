# QF621 Macro Regime Trader: Presentation Outline

## Slide 1: Title

Defensive 4-Signal Macro Regime Overlay

Subtitle: A long-only equity exposure timing strategy focused on drawdown control

## Slide 2: Research Question

Does a price-based macro regime overlay improve equity exposure timing?

Main KPI:

- Max Drawdown
- Calmar Ratio

Secondary KPI:

- Sharpe
- CAGR
- Annual volatility
- Turnover

Key framing:

The strategy does not forecast individual stock returns. It manages market-level equity exposure.

## Slide 3: Initial Strategy Concept

Original proposal:

- Long-only equity strategy
- Estimate risk-on / risk-off market regime
- Scale equity exposure between 0% and 100%
- Allocate equity exposure using inverse-volatility risk parity

Initial five signals:

- VIX proxy
- SPY trend
- Market breadth
- Volatility regime
- Cross momentum

## Slide 4: Final Strategy Design

Final model:

- VIX proxy
- SPY trend
- Market breadth
- Volatility regime

Excluded:

- Cross momentum
- SPY volume confirmation

Exposure rule:

\[
scale_t = clip((composite_t+1)/2, 0, 1)
\]

## Slide 5: Why Cross Momentum Was Excluded

Key result:

| Model | Calmar | Max Drawdown |
| --- | ---: | ---: |
| Defensive 4-signal base | 0.719 | -14.18% |
| Legacy 5-signal with cross momentum | 0.640 | -16.38% |

Interpretation:

Cross momentum may be too slow for a defensive risk-management overlay. It increased CAGR slightly but weakened drawdown control.

## Slide 6: Why SPY Volume Confirmation Was Excluded

Tested hypothesis:

Follow-Through Days and volume-confirmation signals improve risk-on timing.

Research finding:

The volume layer did not add robust incremental value beyond the price-based regime model.

Interpretation:

Daily volume-distribution penalties were too noisy for this design. FTD is better treated as a research diagnostic than as part of the final strategy.

## Slide 7: Benchmark Results

| Strategy | Calmar | CAGR | Max Drawdown |
| --- | ---: | ---: | ---: |
| SPY buy-and-hold | 0.331 | 11.05% | -36.14% |
| Risk parity without overlay | 0.460 | 15.02% | -34.10% |
| Final 4-signal overlay | 0.719 | 10.11% | -14.18% |

Message:

The strategy gives up some upside but materially improves drawdown control.

## Slide 8: Rebalancing Question

Problem:

Daily risk-parity refresh can create unnecessary turnover.

Tested policies:

- Daily
- Weekly
- Scale-change-only

Key point:

The strategy is about market-level exposure timing, not daily stock-level micro-rebalancing.

## Slide 9: Rebalancing Results

| Policy | Calmar | Max Drawdown | Avg Daily Turnover | Trade Days/Year |
| --- | ---: | ---: | ---: | ---: |
| Daily | 0.697 | -14.25% | 5.30% | 239.12 |
| Weekly | 0.671 | -13.63% | 2.85% | 50.67 |
| Scale-change-only | 0.719 | -14.18% | 4.73% | 63.17 |

Conclusion:

Scale-change-only is the main specification. Weekly is a conservative low-turnover variant.

## Slide 10: OOS Rebalancing Results

| Policy | OOS Calmar | OOS CAGR | OOS Max Drawdown | OOS Turnover |
| --- | ---: | ---: | ---: | ---: |
| Weekly | 0.612 | 7.75% | -13.63% | 2.83% |
| Scale-change-only | 0.605 | 8.04% | -14.18% | 4.62% |

Interpretation:

OOS results do not make scale-change-only dominant. Weekly remains useful as a practical lower-turnover implementation.

## Slide 11: Trade Attribution

For scale-change-only:

- Risk-parity-only trades: 0%
- Scale-only trades: 4.71% of turnover
- Scale plus risk-parity refresh: 93.79% of turnover

Message:

The final strategy is not secretly trading every day because of risk-parity updates. It trades when the regime scale changes.

## Slide 12: Drawdown Episode Example

2020 stress episode:

| Policy | Days to Derisk | Episode Max Drawdown |
| --- | ---: | ---: |
| Daily | 0 | -2.33% |
| Weekly | 2 | -3.94% |
| Scale-change-only | 0 | -2.34% |

Message:

Scale-change-only preserved fast defensive response while reducing trade frequency versus daily rebalancing.

## Slide 13: Limitations

- Local dataset is missing META, so the tested trade universe is 9 stocks.
- Representative liquid-stock universe, not full S&P 500.
- Daily data only.
- Simplified cost assumptions.
- Long-only, no leverage, no shorting.
- Parameters were not optimized for best backtest performance.

## Slide 14: Final Conclusion

The final strategy is a Defensive 4-Signal Macro Regime Overlay using VIX proxy, SPY trend, market breadth, and volatility regime. Cross momentum and SPY volume confirmation were tested but excluded because they did not improve the drawdown-focused objective robustly. The final implementation uses scale-change-only rebalancing as the main specification, with weekly rebalancing retained as a conservative low-turnover variant.

## Slide 15: Discussion

The strongest claim:

This model provides a transparent, disciplined risk-management overlay for reducing equity exposure during adverse market regimes.

The claim to avoid:

This model predicts individual stock returns or guarantees higher total return.
