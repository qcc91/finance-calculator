from .extensions import db


class EtlTask(db.Model):
    __tablename__ = "etl_task_define"

    task_id = db.Column(db.String(50), primary_key=True)
    task_name = db.Column(db.String(50), nullable=False)
    task_time = db.Column(db.String(20), nullable=False)
    task_switch = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "task_time": self.task_time,
            "task_switch": self.task_switch,
        }


class Holding(db.Model):
    __tablename__ = "history_holding_show"

    trade_date = db.Column(db.String(10), primary_key=True)
    company = db.Column(db.String(200), primary_key=True)
    department = db.Column(db.String(200), primary_key=True)
    portfolio_code = db.Column(db.String(200), primary_key=True)
    stock_symbol = db.Column(db.String(50), primary_key=True)
    stock_name = db.Column(db.String(50))
    amount = db.Column(db.Float)
    cost = db.Column(db.Float)
    market_value = db.Column(db.Float)
    close_price = db.Column(db.Float)
    industry = db.Column(db.String(50))

    def to_dict(self):
        return {
            "trade_date": self.trade_date,
            "company": self.company,
            "department": self.department,
            "portfolio_code": self.portfolio_code,
            "stock_symbol": self.stock_symbol,
            "stock_name": self.stock_name,
            "amount": self.amount,
            "cost": self.cost,
            "market_value": self.market_value,
            "close_price": self.close_price,
            "industry": self.industry,
        }
