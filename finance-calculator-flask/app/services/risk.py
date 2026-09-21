from datetime import datetime, timedelta

import pandas as pd

from class_file.data_calculate import calculate_var
from class_file.data_process import var_result

from ..errors import ApiError
from ..repositories.holdings import list_by_trade_date


def calculate_market_var(data):
    required = ("tradeDate", "varMethod", "confidenceLevel", "historicalInterval", "forecastDays", "pathCount")
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}")

    try:
        trade_date = datetime.strptime(data["tradeDate"], "%Y-%m-%d")
        interval = int(data["historicalInterval"])
        forecast_days = int(data["forecastDays"])
        path_count = int(data["pathCount"])
        confidence_level = float(data["confidenceLevel"]) / 100
    except (TypeError, ValueError) as error:
        raise ApiError("Invalid VaR calculation parameters") from error

    if not 0 < confidence_level < 1 or forecast_days < 1 or path_count < 1:
        raise ApiError("VaR parameters are outside their allowed range")
    if data["varMethod"] not in {"historical", "parametric", "monteCarlo"}:
        raise ApiError("varMethod must be historical, parametric, or monteCarlo")

    rows = list_by_trade_date(data["tradeDate"])
    if not rows:
        raise ApiError("No holdings found for the selected date", 404)

    frame = pd.DataFrame([row.to_dict() for row in rows])
    for group in ("portfolio_code", "department", "company"):
        frame[f"{group.replace('_code', '')}_sum"] = frame.groupby(group)["market_value"].transform("sum")
        frame[f"{group.replace('_code', '')}_weight"] = (
            frame["market_value"] / frame.groupby(group)["market_value"].transform("sum")
        )

    start_date = (trade_date - timedelta(days=365 * min(max(interval, 1), 3))).strftime("%Y-%m-%d")
    percentile = 1 - confidence_level
    calculated = calculate_var(
        frame,
        start_date,
        data["tradeDate"],
        data["varMethod"],
        percentile,
        forecast_days,
        path_count,
        confidence_level,
    )
    table, chart = var_result(data["varMethod"], frame, *calculated)
    return {
        "table_data": table.to_dict(orient="records"),
        "chart_data": chart.to_dict(orient="records"),
    }
