"""
QF621 Macro Regime Trader: Python Handoff Notes
================================================

This file is a Python-format handoff companion for `macro_regime_trader.py`.
It is meant for a collaborator who has Alpaca PAPER trading access.

The actual strategy implementation is:

    macro_regime_trader.py

Final research specification:

    Defensive 4-Signal Macro Regime Overlay

Signals included:

    1. VIX proxy
    2. SPY trend
    3. Market breadth
    4. Volatility regime

Signals tested but excluded from the final strategy:

    - 12-1 month cross momentum
    - SPY volume confirmation / Follow-Through Day layer
    - Option skew

Final implementation:

    - Long-only equity exposure overlay
    - Inverse-volatility risk-parity stock basket
    - Scale-change-only rebalancing as the main specification
    - Weekly rebalancing retained as a conservative low-turnover variant
    - Alpaca PAPER trading only

Important safety rule:

    Do not put real-money Alpaca keys in this project.
    Do not commit `Alpaca.env`.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
STRATEGY_FILE = ROOT_DIR / "macro_regime_trader.py"
ENV_TEMPLATE = ROOT_DIR / "Alpaca.env.example"
LOCAL_ENV = ROOT_DIR / "Alpaca.env"


FINAL_STRATEGY_SUMMARY = {
    "strategy_name": "Defensive 4-Signal Macro Regime Overlay",
    "included_signals": [
        "VIX proxy",
        "SPY trend",
        "Market breadth",
        "Volatility regime",
    ],
    "excluded_after_testing": [
        "Cross momentum",
        "SPY volume confirmation / Follow-Through Day layer",
        "Option skew",
    ],
    "main_rebalance_policy": "scale_change_only",
    "conservative_variant": "weekly",
    "trading_mode": "Alpaca paper trading only",
}


def check_handoff_files() -> dict[str, bool]:
    """Return whether the files a collaborator needs are present."""
    return {
        "macro_regime_trader.py": STRATEGY_FILE.exists(),
        "requirements.txt": (ROOT_DIR / "requirements.txt").exists(),
        "Alpaca.env.example": ENV_TEMPLATE.exists(),
        "README.md": (ROOT_DIR / "README.md").exists(),
        "final_report": (ROOT_DIR / "results" / "macro_final_research_report.md").exists(),
        "presentation_outline": (
            ROOT_DIR / "results" / "macro_final_presentation_outline.md"
        ).exists(),
    }


def check_alpaca_env() -> dict[str, bool]:
    """
    Check whether local Alpaca PAPER credentials appear to be configured.

    This function does not print or expose secret values.
    """
    return {
        "Alpaca.env_exists": LOCAL_ENV.exists(),
        "ALPACA_PAPER_API_KEY_MR_set": bool(os.getenv("ALPACA_PAPER_API_KEY_MR")),
        "ALPACA_PAPER_API_SECRET_MR_set": bool(os.getenv("ALPACA_PAPER_API_SECRET_MR")),
    }


def print_handoff_summary() -> None:
    """Print a concise handoff checklist for the collaborator."""
    print("QF621 Macro Regime Trader Handoff")
    print("=" * 40)
    print(f"Strategy file: {STRATEGY_FILE.name}")
    print(f"Final strategy: {FINAL_STRATEGY_SUMMARY['strategy_name']}")
    print(f"Main rebalance policy: {FINAL_STRATEGY_SUMMARY['main_rebalance_policy']}")
    print(f"Conservative variant: {FINAL_STRATEGY_SUMMARY['conservative_variant']}")
    print(f"Trading mode: {FINAL_STRATEGY_SUMMARY['trading_mode']}")
    print()

    print("Included signals:")
    for signal in FINAL_STRATEGY_SUMMARY["included_signals"]:
        print(f"  - {signal}")
    print()

    print("Excluded after testing:")
    for signal in FINAL_STRATEGY_SUMMARY["excluded_after_testing"]:
        print(f"  - {signal}")
    print()

    print("Required file check:")
    for name, ok in check_handoff_files().items():
        print(f"  - {name}: {'OK' if ok else 'MISSING'}")
    print()

    print("Credential safety:")
    print("  - Use Alpaca PAPER keys only.")
    print("  - Copy Alpaca.env.example to Alpaca.env locally.")
    print("  - Never commit Alpaca.env or .env.")
    print("  - PAPER remains True in macro_regime_trader.py.")
    print()

    print("Recommended validation flow:")
    print("  1. Install dependencies from requirements.txt.")
    print("  2. Add Alpaca PAPER credentials in Alpaca.env.")
    print("  3. Run the price-only backtest first.")
    print("  4. Review generated files under results/.")
    print("  5. Only then test Alpaca paper live mode.")


if __name__ == "__main__":
    print_handoff_summary()
