from flask import Blueprint, jsonify
from sqlalchemy import text

from ..extensions import db


blueprint = Blueprint("health", __name__)


@blueprint.get("/health")
def health():
    db.session.execute(text("SELECT 1"))
    return jsonify({"status": "ok"})
