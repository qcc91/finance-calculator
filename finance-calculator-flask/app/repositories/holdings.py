from sqlalchemy import and_

from ..models import Holding


IDENTITY_FIELDS = (
    "trade_date",
    "company",
    "department",
    "portfolio_code",
    "stock_symbol",
)


def list_holdings(filters=None):
    filters = filters or {}
    query = Holding.query
    if filters.get("stock_symbol"):
        query = query.filter(Holding.stock_symbol == filters["stock_symbol"])
    if filters.get("start_date"):
        query = query.filter(Holding.trade_date >= filters["start_date"])
    if filters.get("end_date"):
        query = query.filter(Holding.trade_date <= filters["end_date"])
    if filters.get("department"):
        query = query.filter(Holding.department == filters["department"])
    if filters.get("portfolio_code"):
        query = query.filter(Holding.portfolio_code == filters["portfolio_code"])
    if filters.get("industry"):
        query = query.filter(Holding.industry == filters["industry"])
    return query.order_by(Holding.trade_date.desc(), Holding.stock_symbol).all()


def find_by_identity(identity):
    conditions = [getattr(Holding, field) == identity[field] for field in IDENTITY_FIELDS]
    return Holding.query.filter(and_(*conditions)).first()


def list_by_trade_date(trade_date):
    return Holding.query.filter(Holding.trade_date == trade_date).all()
