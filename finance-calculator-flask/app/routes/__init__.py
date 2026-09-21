from .data import blueprint as data_blueprint
from .health import blueprint as health_blueprint
from .holdings import blueprint as holdings_blueprint
from .risk import blueprint as risk_blueprint


BLUEPRINTS = (health_blueprint, holdings_blueprint, data_blueprint, risk_blueprint)
