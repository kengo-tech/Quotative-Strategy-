# Alpaca Paper Trading Handoff

## Purpose

This repository contains the QF621 Macro Regime Trader research prototype. The final research specification is a Defensive 4-Signal Macro Regime Overlay:

1. VIX proxy
2. SPY trend
3. Market breadth
4. Volatility regime

The model is long-only and manages total equity exposure. It does not forecast individual stock returns.

## Safety

The code is configured for Alpaca paper trading only:

- `PAPER = True` is hard-coded in `macro_regime_trader.py`.
- Do not put real-money Alpaca keys in this project.
- Do not commit `Alpaca.env`; it is intentionally ignored by git.
- Use `Alpaca.env.example` as the template for paper credentials.

## Required Files

The friend receiving this project needs:

- `macro_regime_trader.py`
- `requirements.txt`
- `Alpaca.env.example`
- `README.md`
- optional: `results/` research summaries and CSV outputs

They should copy `Alpaca.env.example` to `Alpaca.env` locally and fill in their Alpaca paper key and secret.

## Data Modes

The script can operate in two ways:

- Offline research mode: uses cached parquet files or local CSV data if available.
- Alpaca data mode: downloads data through Alpaca when paper credentials are present.

If no local cache exists, valid Alpaca paper credentials are required for historical data download.

## Recommended Validation Flow

1. Install dependencies from `requirements.txt`.
2. Add Alpaca paper credentials in local `Alpaca.env`.
3. Run the price-only backtest first.
4. Review generated files under `results/`.
5. Only after the backtest completes, test paper live mode.

The final report should use the price-only Defensive 4-Signal model as the main specification. SPY volume confirmation is retained in the code for research comparison, but it is not part of the final strategy conclusion.

## Final Research Conclusion

The final strategy is a Defensive 4-Signal Macro Regime Overlay using VIX proxy, SPY trend, market breadth, and volatility regime. Cross momentum and SPY volume confirmation were tested but excluded because they did not improve the drawdown-focused objective robustly. The final implementation uses scale-change-only rebalancing as the main specification, with weekly rebalancing retained as a conservative low-turnover variant.

## Limitations to Tell the Reviewer

- The local validation dataset used in this workspace was missing META, so local results were based on a 9-stock trade universe.
- A friend with Alpaca access may be able to regenerate results using the intended full 10-stock trade universe.
- This is a research/paper-trading prototype, not a real-money trading system.
