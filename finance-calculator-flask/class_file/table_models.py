#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:36:31 2024

@author: qinxiangyuan
"""
from class_file.db_connection import db

#任务定义表
#task difine table
class etl_task_define(db.Model):
    __tablename__ = 'etl_task_define'  
    task_id = db.Column(db.String, primary_key=True)
    task_name = db.Column(db.String)
    task_time = db.Column(db.String)
    task_switch = db.Column(db.String)

#历史持仓表
#history_holding_show table
class history_holding_show(db.Model):
    __tablename__ = 'history_holding_show'  
    trade_date = db.Column(db.String, primary_key=True)
    company = db.Column(db.String, primary_key=True)
    department = db.Column(db.String, primary_key=True)
    portfolio_code = db.Column(db.String, primary_key=True)
    stock_symbol = db.Column(db.String, primary_key=True)
    stock_name = db.Column(db.String)
    amount = db.Column(db.Float)
    cost = db.Column(db.Float)
    market_value = db.Column(db.Float)
    close_price = db.Column(db.Float)
    industry = db.Column(db.String)


