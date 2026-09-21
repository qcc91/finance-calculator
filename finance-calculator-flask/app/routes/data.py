from flask import Blueprint, current_app, jsonify, request, send_file

from ..errors import ApiError
from ..services.holdings import import_holdings
from ..services.tasks import list_tasks, update_task


blueprint = Blueprint("data", __name__)


@blueprint.post("/data/collect/import")
def import_data():
    payload = request.get_json(silent=True) or {}
    count = import_holdings(payload.get("data"))
    return jsonify({"message": "Data imported successfully!", "imported": count}), 201


@blueprint.get("/data/collect/import/download/input_template")
def download_template():
    path = current_app.config["TEMPLATE_FILE"]
    if not path.exists():
        raise ApiError("Input template file not found", 404)
    return send_file(path, as_attachment=True)


@blueprint.get("/data/collect/etl/task/show")
def show_tasks():
    tasks = list_tasks(
        request.args.get("selectedTaskId", ""),
        request.args.get("selectedTaskName", ""),
    )
    return jsonify(tasks)


@blueprint.put("/data/collect/etl/task/set")
def set_task():
    task = update_task(request.get_json(silent=True) or {}, current_app._get_current_object())
    return jsonify({"message": "Task updated successfully!", "data": task})
