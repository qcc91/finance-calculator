#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 21:53:49 2024

@author: qinxiangyuan
"""
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from class_file.table_models import etl_task_define, history_holding_show
from class_file.db_connection import db
from class_file.data_fetch import fetch_stock_data

scheduler = BackgroundScheduler()

def get_task_parameter(app):
    with app.app_context():
        task_data = etl_task_define.query.filter_by(task_id='000001').first()
        if task_data:
            return task_data.task_id, task_data.task_name, task_data.task_time, task_data.task_switch
        else:
            return None, None, None, None

def schedule_task(app):
    with app.app_context():
        task_id, task_name, task_time, task_switch = get_task_parameter(app)
        hour, minute = map(int, task_time.split(':'))
        if task_switch == '开':
            scheduler.remove_all_jobs()
            scheduler.add_job(
                lambda: holding_data_save(app),
                trigger=CronTrigger(hour=hour, minute=minute),
                id=task_id,
                name=task_name,
                replace_existing=True
                )
        else:
            scheduler.remove_all_jobs()

def holding_data_save(app):
    with app.app_context():
        excel_data = pd.read_excel('/Users/qinxiangyuan/Desktop/个人文件夹/python代码/项目库/finance-calculator/存放数据文件夹/holdings.xlsx')
        previous_day = (pd.Timestamp.now().date() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        row_to_delete = history_holding_show.query.filter_by(trade_date=previous_day).all()
        if row_to_delete:
            for row in row_to_delete:
                db.session.delete(row)
            db.session.commit()
        filtered_data = excel_data[excel_data['trade_date'] == previous_day]
        filtered_data_last = fetch_stock_data(filtered_data)
        filtered_data_last.to_sql('history_holding_show', con=db.engine, if_exists='append', index=False)

def initialize_scheduler(app):
    with app.app_context():
        scheduler.start()
