import pandas as pd
import baostock as bs


def _rows(result):
    if result.error_code != "0":
        raise RuntimeError(result.error_msg)
    values = []
    while result.next():
        values.append(dict(zip(result.fields, result.get_row_data())))
    return values


def fetch_stock_data(stock_portfolio):
    required = {"trade_date", "stock_symbol", "company", "department", "portfolio_code", "amount", "cost"}
    missing = sorted(required.difference(stock_portfolio.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    login = bs.login()
    if login.error_code != "0":
        raise RuntimeError(f"BaoStock login failed: {login.error_msg}")

    try:
        price_records = []
        marks = stock_portfolio[["trade_date", "stock_symbol"]].drop_duplicates()
        for mark in marks.itertuples(index=False):
            result = bs.query_history_k_data(
                mark.stock_symbol,
                "date,code,close",
                start_date=str(mark.trade_date),
                end_date=str(mark.trade_date),
                frequency="d",
                adjustflag="3",
            )
            rows = _rows(result)
            if not rows:
                raise ValueError(f"No market price found for {mark.stock_symbol} on {mark.trade_date}")
            price_records.extend(rows)

        industry_records = []
        for symbol in marks["stock_symbol"].drop_duplicates():
            rows = _rows(bs.query_stock_industry(code=symbol))
            if not rows:
                raise ValueError(f"No stock information found for {symbol}")
            industry_records.append(rows[0])

        prices = pd.DataFrame(price_records)
        prices["close"] = pd.to_numeric(prices["close"], errors="raise")
        industries = pd.DataFrame(industry_records)
        market_data = prices.merge(industries, on="code", how="inner").drop_duplicates()
        result = stock_portfolio.merge(
            market_data,
            left_on=["trade_date", "stock_symbol"],
            right_on=["date", "code"],
            how="inner",
        )
        result.drop(
            columns=["date", "code", "updateDate", "industryClassification"],
            inplace=True,
            errors="ignore",
        )
        result.rename(columns={"close": "close_price", "code_name": "stock_name"}, inplace=True)
        result["amount"] = pd.to_numeric(result["amount"], errors="raise")
        result["cost"] = pd.to_numeric(result["cost"], errors="raise")
        result["market_value"] = result["amount"] * result["close_price"]
        return result[
            [
                "trade_date",
                "company",
                "department",
                "portfolio_code",
                "stock_symbol",
                "stock_name",
                "cost",
                "amount",
                "market_value",
                "close_price",
                "industry",
            ]
        ]
    finally:
        bs.logout()
