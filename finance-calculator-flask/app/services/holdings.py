from datetime import datetime

import pandas as pd
from class_file.data_fetch import fetch_stock_data
from class_file.data_process import holding_analyze

from ..errors import ApiError
from ..extensions import db
from ..models import Holding
from ..repositories.holdings import IDENTITY_FIELDS, find_by_identity, list_holdings


CREATE_FIELD_MAP = {
    "tradeDate": "trade_date",
    "company": "company",
    "department": "department",
    "portfolioCode": "portfolio_code",
    "stockSymbol": "stock_symbol",
    "stockName": "stock_name",
    "amount": "amount",
    "cost": "cost",
    "marketValue": "market_value",
    "closePrice": "close_price",
    "industry": "industry",
}


def _require_fields(data, fields):
    missing = [field for field in fields if data.get(field) in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}")


def _number(value, field):
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ApiError(f"{field} must be a number") from error


def identity_from_camel_case(data):
    required = ("tradeDate", "company", "department", "portfolioCode", "stockSymbol")
    _require_fields(data, required)
    return {
        "trade_date": data["tradeDate"],
        "company": data["company"],
        "department": data["department"],
        "portfolio_code": data["portfolioCode"],
        "stock_symbol": data["stockSymbol"],
    }


def identity_from_snake_case(data):
    _require_fields(data, IDENTITY_FIELDS)
    return {field: data[field] for field in IDENTITY_FIELDS}


def get_holdings(filters):
    return [holding.to_dict() for holding in list_holdings(filters)]


def create_holding(data):
    _require_fields(data, CREATE_FIELD_MAP)
    identity = identity_from_camel_case(data)
    if find_by_identity(identity):
        raise ApiError("Data conflict. Please Check!", 409)

    values = {target: data[source] for source, target in CREATE_FIELD_MAP.items()}
    for field in ("amount", "cost", "market_value", "close_price"):
        values[field] = _number(values[field], field)
    holding = Holding(**values)
    db.session.add(holding)
    db.session.commit()
    return holding.to_dict()


def update_holding(data):
    holding = find_by_identity(identity_from_camel_case(data))
    if not holding:
        raise ApiError("Record not found", 404)

    updates = {
        "amount": "amount",
        "cost": "cost",
        "marketValue": "market_value",
        "closePrice": "close_price",
        "industry": "industry",
    }
    for source, target in updates.items():
        if source in data:
            value = data[source]
            if target in {"amount", "cost", "market_value", "close_price"}:
                value = _number(value, target)
            setattr(holding, target, value)
    db.session.commit()
    return holding.to_dict()


def delete_holding(data):
    holding = find_by_identity(identity_from_snake_case(data))
    if not holding:
        raise ApiError("Data not found", 404)
    db.session.delete(holding)
    db.session.commit()


def import_holdings(data):
    if not isinstance(data, list) or not data:
        raise ApiError("No data provided in the request")

    frame = pd.DataFrame(data)
    required = {"trade_date", "company", "department", "portfolio_code", "stock_symbol", "amount", "cost"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ApiError(f"Missing required columns: {', '.join(missing)}")

    dates = frame["trade_date"].dropna().unique().tolist()
    if dates and Holding.query.filter(Holding.trade_date.in_(dates)).first():
        raise ApiError("Data conflict. Please Check!", 409)

    enriched = fetch_stock_data(frame)
    records = enriched.where(pd.notnull(enriched), None).to_dict(orient="records")
    db.session.bulk_insert_mappings(Holding, records)
    db.session.commit()
    return len(records)


def analyse_holdings(data):
    _require_fields(data, ("tradeDate", "analyseLevel"))
    try:
        year = datetime.strptime(data["tradeDate"], "%Y-%m-%d").year
    except ValueError as error:
        raise ApiError("tradeDate must use YYYY-MM-DD format") from error

    rows = Holding.query.filter(
        Holding.trade_date >= f"{year}-01-01",
        Holding.trade_date <= f"{year}-12-31",
    ).all()
    if not rows:
        raise ApiError("No holdings found for the selected year", 404)

    frame = pd.DataFrame([row.to_dict() for row in rows])
    try:
        table, chart1, chart2, chart3 = holding_analyze(
            frame,
            data["analyseLevel"],
            data["tradeDate"],
            data.get("department", ""),
            data.get("portfolioCode", ""),
        )
    except ValueError as error:
        raise ApiError(str(error)) from error
    return {
        "table_data": table.reset_index().to_dict(orient="records"),
        "chart1_data": chart1.reset_index().to_dict(orient="records"),
        "chart2_data": chart2.reset_index().to_dict(orient="records"),
        "chart3_data": chart3.reset_index().to_dict(orient="records"),
    }
