from flask import Blueprint, jsonify, request

from ..services.holdings import (
    analyse_holdings,
    create_holding,
    delete_holding,
    get_holdings,
    update_holding,
)


blueprint = Blueprint("holdings", __name__)


def _filters_from_request():
    return {
        "stock_symbol": request.args.get("selectedStockCode", ""),
        "start_date": request.args.get("selectedStartDate", ""),
        "end_date": request.args.get("selectedEndDate", ""),
        "department": request.args.get("selectedDepartment", ""),
        "portfolio_code": request.args.get("selectedPortfolioCode", ""),
        "industry": request.args.get("selectedIndustry", ""),
    }


@blueprint.get("/holdings/show")
@blueprint.get("/data/edit/show")
def show_holdings():
    return jsonify(get_holdings(_filters_from_request()))


@blueprint.post("/data/edit/add")
def add_holding():
    holding = create_holding(request.get_json(silent=True) or {})
    return jsonify({"message": "Data added successfully!", "data": holding}), 201


@blueprint.put("/data/edit/update")
def edit_holding():
    holding = update_holding(request.get_json(silent=True) or {})
    return jsonify({"message": "Data updated successfully!", "data": holding})


@blueprint.post("/data/edit/delete")
def remove_holding():
    delete_holding(request.get_json(silent=True) or {})
    return jsonify({"message": "Data deleted successfully"})


@blueprint.post("/holdings/analyse")
def analyse():
    return jsonify(analyse_holdings(request.get_json(silent=True) or {}))
