import pandas as pd
import pytest

from class_file.data_process import holding_analyze


def test_portfolio_concentration_uses_ratio():
    holdings = pd.DataFrame(
        [
            {
                "trade_date": "2026-09-21",
                "company": "A",
                "department": "D",
                "portfolio_code": "P",
                "stock_symbol": "one",
                "stock_name": "One",
                "market_value": 75.0,
                "industry": "I",
            },
            {
                "trade_date": "2026-09-21",
                "company": "A",
                "department": "D",
                "portfolio_code": "P",
                "stock_symbol": "two",
                "stock_name": "Two",
                "market_value": 25.0,
                "industry": "I",
            },
        ]
    )

    _, _, concentration, _ = holding_analyze(
        holdings, "portfolio", "2026-09-21", "D", "P"
    )

    assert concentration.loc["one", "market_value_ratio"] == pytest.approx(0.75)
    assert concentration.loc["two", "market_value_ratio"] == pytest.approx(0.25)
