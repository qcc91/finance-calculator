from flask import Blueprint, jsonify, request

from ..services.risk import calculate_market_var


blueprint = Blueprint("risk", __name__)


@blueprint.post("/market/var")
def market_var():
    return jsonify(calculate_market_var(request.get_json(silent=True) or {}))
