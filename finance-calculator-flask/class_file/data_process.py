import pandas as pd


def _concentration(frame, group_column):
    market_value = frame.groupby(group_column)["market_value"].sum()
    total = market_value.sum()
    ratio = market_value / total if total else market_value * 0
    return pd.concat(
        [market_value, ratio.rename("market_value_ratio")],
        axis=1,
    ).rename_axis("organization")


def holding_analyze(stock_portfolio, analyse_level, trade_date, department, portfolio_code):
    selected_day = stock_portfolio["trade_date"] == trade_date
    history = stock_portfolio["trade_date"] <= trade_date

    if analyse_level == "company":
        concentration_column = "department"
    elif analyse_level == "department":
        if not department:
            raise ValueError("department is required for department analysis")
        selected_day &= stock_portfolio["department"] == department
        history &= stock_portfolio["department"] == department
        concentration_column = "portfolio_code"
    elif analyse_level == "portfolio":
        if not department or not portfolio_code:
            raise ValueError("department and portfolioCode are required for portfolio analysis")
        selected_day &= stock_portfolio["department"] == department
        selected_day &= stock_portfolio["portfolio_code"] == portfolio_code
        history &= stock_portfolio["department"] == department
        history &= stock_portfolio["portfolio_code"] == portfolio_code
        concentration_column = "stock_symbol"
    else:
        raise ValueError("analyseLevel must be company, department, or portfolio")

    current = stock_portfolio[selected_day]
    historical = stock_portfolio[history]
    table_data = (
        current.groupby(["stock_symbol", "stock_name"])["market_value"]
        .sum()
        .nlargest(10)
    )
    chart1_data = historical.groupby("trade_date")["market_value"].sum()
    chart2_data = _concentration(current, concentration_column)
    chart3_data = _concentration(current, "industry")
    return table_data, chart1_data, chart2_data, chart3_data


def var_result(
    var_method,
    stock_portfolio,
    single_stock_returns,
    portfolio_returns,
    department_returns,
    company_returns,
    company_daily_returns,
    company_simulations,
):
    result = stock_portfolio.merge(
        single_stock_returns, left_on="stock_symbol", right_on="code", how="inner"
    )
    result = result.merge(portfolio_returns, on="portfolio_code", how="inner")
    result = result.merge(department_returns, on="department", how="inner")
    result = result.merge(company_returns, on="company", how="inner")

    result["stock_VaR"] = result["market_value"] * result["log_returns_single_stock_forecas"]
    result["portfolio_VaR"] = result["portfolio_sum"] * result["log_returns_portfolio_forecas"]
    result["department_VaR"] = result["department_sum"] * result["log_returns_department_forecas"]
    result["company_VaR"] = result["company_sum"] * result["log_returns_company_forecas"]

    table = result[
        [
            "company",
            "company_sum",
            "company_VaR",
            "department",
            "department_sum",
            "department_VaR",
            "portfolio_code",
            "portfolio_sum",
            "portfolio_VaR",
            "stock_symbol",
            "stock_name",
            "market_value",
            "stock_VaR",
        ]
    ].copy()
    table["stock_symbol"] = table["stock_symbol"] + "." + table["stock_name"]
    table.drop(columns="stock_name", inplace=True)

    if var_method in {"historical", "parametric"}:
        chart = company_daily_returns.drop(columns=["company"], errors="ignore").copy()
    else:
        simulations = company_simulations["monte_carlo_simulations_cum"].apply(list).tolist()
        chart = pd.concat([pd.DataFrame(values) for values in simulations], ignore_index=True)
        chart.columns = [str(index + 1) for index in range(chart.shape[1])]
        chart.insert(0, "0", 0)

    return table, chart
