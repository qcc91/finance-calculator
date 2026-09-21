import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from class_file.data_fetch import fetch_stock_data

from ..errors import ApiError
from ..extensions import db
from ..models import EtlTask, Holding


scheduler = BackgroundScheduler()


def list_tasks(task_id=None, task_name=None):
    query = EtlTask.query
    if task_id:
        query = query.filter(EtlTask.task_id == task_id)
    if task_name:
        query = query.filter(EtlTask.task_name == task_name)
    return [task.to_dict() for task in query.order_by(EtlTask.task_id).all()]


def update_task(data, app):
    task_id = data.get("task_id")
    if not task_id:
        raise ApiError("Task ID is missing in the request")
    task = db.session.get(EtlTask, task_id)
    if not task:
        raise ApiError("Record not found", 404)
    task.task_time = data.get("task_time", task.task_time)
    task.task_switch = data.get("task_switch", task.task_switch)
    db.session.commit()
    configure_jobs(app)
    return task.to_dict()


def import_scheduled_holdings(app):
    with app.app_context():
        path = app.config["HOLDINGS_FILE"]
        if not path.exists():
            app.logger.error("Scheduled holdings file does not exist: %s", path)
            return

        previous_day = (pd.Timestamp.now().date() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        source = pd.read_excel(path)
        replacement = source[source["trade_date"] == previous_day]
        enriched = fetch_stock_data(replacement)

        try:
            Holding.query.filter(Holding.trade_date == previous_day).delete(synchronize_session=False)
            records = enriched.where(pd.notnull(enriched), None).to_dict(orient="records")
            db.session.bulk_insert_mappings(Holding, records)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


def configure_jobs(app):
    scheduler.remove_all_jobs()
    task = db.session.get(EtlTask, "000001")
    if not task or task.task_switch != "开":
        return
    try:
        hour, minute = (int(part) for part in task.task_time.split(":"))
    except (TypeError, ValueError) as error:
        raise ApiError("Task time must use HH:MM format") from error
    scheduler.add_job(
        import_scheduled_holdings,
        args=[app],
        trigger=CronTrigger(hour=hour, minute=minute),
        id=task.task_id,
        name=task.task_name,
        replace_existing=True,
    )


def start_scheduler(app):
    if not scheduler.running:
        scheduler.start()
    with app.app_context():
        configure_jobs(app)
