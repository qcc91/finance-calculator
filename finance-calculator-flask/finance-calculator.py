#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 20:29:20 2024

@author: qinxiangyuan
"""

#-------引入各种flask包件-------
#-------import flask packages------
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
#-------引入计量包件-------
#-------import calculation packages------
import pandas as pd
#-------引入时间控制包件-------
#-------import time control packages-----
from datetime import datetime, timedelta
#-------引入数据库连接包件-----
#-------import database connection packages----
from sqlalchemy import and_, func
#--------引入自定义功能包---------
#--------import custom packages------
from class_file.db_connection import initialize_database,db
from class_file.table_models import etl_task_define, history_holding_show
from class_file.task_schedule import initialize_scheduler, schedule_task
from class_file.data_fetch import fetch_stock_data
from class_file.data_validation import data_conflict
from class_file.data_process import holding_analyze, var_result
from class_file.data_calculate import calculate_var
#--------------------------------
#创建 Flask 应用程序
#create flask application
app = Flask(__name__)
#-----设置日志输出级别为最高的DEBUG级别------
#-----set the log output level----------
app.logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('flask_error.log', maxBytes=10000, backupCount=1)
app.logger.addHandler(handler)
#-----------------------------------------
#初始化cors
#initialize cors
CORS(app)
#初始化数据库连接
#initialize database connection
initialize_database(app)
#初始化任务调度器
#initialize task scheduler
initialize_scheduler(app)
#----------------------------------前台页面响应-----------------------------------
#-----------------------------handle front end web interaction------------------
#-------数据导入路由------
#------data import route----
@app.route('/data/collect/import', methods=['POST'])
def import_data():
    try:
        data = request.json.get('data')
        if not data:
            raise ValueError("No data provided in the request.")  
        #将数据存储到 DataFrame
        #put json data into DataFrame
        stock_portfolio = pd.DataFrame(data)    
        stock_portfolio_dates = stock_portfolio['trade_date'].drop_duplicates().tolist()

        #构建过滤条件
        #build filter condition
        filters = []
        if stock_portfolio_dates:
            date_filters = [history_holding_show.trade_date.in_(stock_portfolio_dates)]
            filters.extend(date_filters)
            
        #判断上传数据日期是否冲突
        #check whether the uploaded data date conflicts
        existing_record = data_conflict(history_holding_show, filters)
        
        if existing_record:
            #如果有冲突，弹出确认对话框
            #if conflicts return message
            return jsonify({'message': 'Data conflict. Please Check!'}),200
        else:
            stock_portfolio_last = fetch_stock_data(stock_portfolio)
            #将结果存入数据库
            #store the data in database
            stock_portfolio_last.to_sql('history_holding_show', con=db.engine, if_exists='append', index=False)
            #返回消息
            #return message
            return jsonify({'message': 'Data imported successfully!'})
    #异常处理
    #handle exception 
    except Exception as e:
       return jsonify({'error': str(e)}), 500
#------数据导入：下载模板文件的路由------
#------import data：downloading template file route------
@app.route('/data/collect/import/download/input_template', methods=['GET'])
def download_template():
    try:
        template_filepath = 'E:/David/学习/python代码/项目/finance-calculator/下载模板/input_Data.xlsx'
        return send_file(template_filepath, as_attachment=True)
    #异常处理
    #handle exception 
    except Exception as e:
       return jsonify({'error': str(e)}), 500
#------数据任务路由------
#------task scheduler route-----
@app.route('/data/collect/etl/task/show', methods=['GET'])
def etl_task_set():
    try:
        #从前台获取参数
        #get parameter from front-end
        selected_task_id = request.args.get('selectedTaskId', '')
        selected_task_name = request.args.get('selectedTaskName', '')
        
        #构建过滤条件
        #build filter condition
        filters = []
        if selected_task_id:
            filters.append(etl_task_define.task_id == selected_task_id)
        if selected_task_name:
            filters.append(etl_task_define.task_name == selected_task_name)
       #从数据库中读取数据并转换成json
       #query data from database and transfer them to json
        etl_task_list_all = etl_task_define.query.filter(and_(*filters)).all()
        task_list = [{
            'task_id':etl_task_define.task_id,
            'task_name':etl_task_define.task_name, 
            'task_time':etl_task_define.task_time,
            'task_switch':etl_task_define.task_switch, 
            } for etl_task_define in etl_task_list_all]      
        etl_task_list = pd.DataFrame(task_list)
       #对数据结果进行判断
       #check the data
        if etl_task_list.empty:
            return jsonify({'message': 'The task list is empty. successfully!'})
        else:
            json_data = etl_task_list.to_json(orient='records')
            return json_data
    #异常处理
    #handle exception 
    except Exception as e:
       return jsonify({'error': str(e)}), 500
#------数据任务:修改路由------
#------task scheduler：scheduler modify route
@app.route('/data/collect/etl/task/set', methods=['PUT'])
def etl_task_modify():
    try:
        #从请求中获取更新数据
        #get data from front-end json
        updated_data = request.json
        
        #构造查询条件，根据任务ID来查找记录
        #build filter conditon
        task_id = request.json.get('task_id')
        
        if not task_id:
            return jsonify({'error': 'Task ID is missing in the request'}), 400
        existing_record = etl_task_define.query.get(task_id)
        if not existing_record:
            return jsonify({'error': 'Record not found'}), 404
        #更新记录的字段值
        #update data
        existing_record.task_time = updated_data.get('task_time', existing_record.task_time)
        existing_record.task_switch = updated_data.get('task_switch', existing_record.task_switch)
        #提交更新到数据库
        #commit update
        db.session.commit()
        #重新设置任务调度
        #reset the task schedule
        schedule_task(app)
        #返回成功消息
        #return success message
        return jsonify({'message': 'Task updated successfully!'}), 200
    #异常处理
    #handle exception 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#------持仓编辑路由------
#-----holding edit route------
@app.route('/data/edit/show', methods=['GET'])
def modify_data():
    try:
        #从前台获取参数
        #get data from front-end
        selected_stock_code = request.args.get('selectedStockCode', '')
        selected_start_date = request.args.get('selectedStartDate', '')
        selected_end_date = request.args.get('selectedEndDate', '')
        selected_department = request.args.get('selectedDepartment', '')
        selected_portfolio_code = request.args.get('selectedPortfolioCode', '')
        selected_industry = request.args.get('selectedIndustry', '')
        
        #构建查询条件
        #build filter conditon 
        filters = []
        if selected_stock_code:
            filters.append(history_holding_show.stock_symbol == selected_stock_code)
        if selected_start_date:
            filters.append(history_holding_show.trade_date >= selected_start_date)
        if selected_end_date:
            filters.append(history_holding_show.trade_date <= selected_end_date)
        if selected_department:
            filters.append(history_holding_show.department == selected_department)
        if selected_portfolio_code:
            filters.append(history_holding_show.portfolio_code == selected_portfolio_code)
        if selected_industry:
            filters.append(history_holding_show.industry == selected_industry)

        #从数据库中读取数据并转换成json
        #query data from database and transfer them to json
        holdings_data_all = history_holding_show.query.filter(and_(*filters)).all()
        holdings_data = [{
            'trade_date': holding.trade_date,
            'company': holding.company, 
            'department': holding.department,
            'portfolio_code': holding.portfolio_code, 
            'stock_symbol': holding.stock_symbol, 
            'stock_name': holding.stock_name, 
            'amount': holding.amount, 
            'cost': holding.cost,
            'market_value': holding.market_value, 
            'close_price': holding.close_price, 
            'industry': holding.industry 
            } for holding in holdings_data_all]      
        stock_portfolio_last = pd.DataFrame(holdings_data)
        
       #对数据结果进行判断
       #check the data
        if stock_portfolio_last.empty:
            return jsonify({'message': 'The stock_portfolio_last DataFrame is empty.'})
        else:
            json_data = stock_portfolio_last.to_json(orient='records')
            return json_data
    #异常处理
    #handle exception 
    except Exception as e:
       return jsonify({'error': str(e)}), 500
#------持仓编辑：新增数据路由------
#------holding edit：add new data route-----
@app.route('/data/edit/add', methods=['POST'])
def add_data():
    try:
        #从请求中获取新增数据参数
        #get data from front-end
        new_data = request.json
        trade_date = new_data.get('tradeDate','')
        company = new_data.get('company','')
        department = new_data.get('department','')
        portfolio_code = new_data.get('portfolioCode','')
        stock_symbol = new_data.get('stockSymbol','')

        #构建查询条件
        #build filter conditon 
        filters = []
        if trade_date:
            filters.append(history_holding_show.trade_date == trade_date)
        if company:
            filters.append(history_holding_show.company == company)
        if department:
            filters.append(history_holding_show.department == department)
        if portfolio_code:
            filters.append(history_holding_show.portfolio_code == portfolio_code)
        if stock_symbol:
            filters.append(history_holding_show.stock_symbol == stock_symbol)

        #检查是否存在相同关键信息的记录
        #check whether the new data conflicts
        existing_record = data_conflict(history_holding_show, filters)
        
        if existing_record:
            #如果存在重复数据，则返回适当的错误消息给前端
            #if conflicts， return message
            return jsonify({'message': 'Data conflict. Please Check!'}),200
        else:
            #执行新增数据的操作
            #execute adding data
            new_record = history_holding_show(
                trade_date=new_data['tradeDate'],
                company=new_data['company'],
                department=new_data['department'],
                portfolio_code=new_data['portfolioCode'],
                stock_symbol=new_data['stockSymbol'],
                stock_name=new_data['stockName'],
                amount=new_data['amount'],
                cost=new_data['cost'],
                market_value=new_data['marketValue'],
                close_price=new_data['closePrice'],
                industry=new_data['industry']
                )
        
            db.session.add(new_record)
            db.session.commit()
        
            #返回成功消息
            #return success message
            return jsonify({'message': 'Data added successfully!'}), 201
    #异常处理
    #handle exception
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#------持仓编辑：修改数据路由------
#------holding edit：modify data route-----
@app.route('/data/edit/update', methods=['PUT'])
def update_data():
    try:
        #从请求中获取更新数据参数
        #get data from front-end
        updated_data = request.json
        trade_date = updated_data.get('tradeDate','')
        company = updated_data.get('company','')
        department = updated_data.get('department','')
        portfolio_code = updated_data.get('portfolioCode','')
        stock_symbol = updated_data.get('stockSymbol','')
        
        #构建查询条件
        #build filter conditon 
        filters = []
        if trade_date:
            filters.append(history_holding_show.trade_date == trade_date)
        if company:
            filters.append(history_holding_show.company == company)
        if department:
            filters.append(history_holding_show.department == department)
        if portfolio_code:
            filters.append(history_holding_show.portfolio_code == portfolio_code)
        if stock_symbol:
            filters.append(history_holding_show.stock_symbol == stock_symbol)
        
        #查找相同关键信息的记录
        #query data from database
        existing_record = history_holding_show.query.filter(and_(*filters)).first()
        if not existing_record:
            #如果没找到数据，返回前端信息
            #if there is no matching data，return message
            return jsonify({'error': 'Record not found'}), 404
        else:
            #更新记录的字段值
            #update data
            existing_record.amount = updated_data.get('amount', existing_record.amount)
            existing_record.cost = updated_data.get('cost', existing_record.cost)
            existing_record.market_value = updated_data.get('marketValue', existing_record.market_value)
            existing_record.close_price = updated_data.get('closePrice', existing_record.close_price)
            existing_record.industry = updated_data.get('industry', existing_record.industry)
        
            #提交更新到数据库
            #commit update
            db.session.commit()
        
            #返回成功消息
            #return success message
            return jsonify({'message': 'Data updated successfully!'}), 200
    #异常处理
    #handle exception
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#------持仓编辑：删除数据路由------
#------holding edit：delete data route-----
@app.route('/data/edit/delete', methods=['POST'])
def delete_data():
    try:
        #从请求中获取选中行的关键信息
        #get data from front-end
        data = request.json
        trade_date = data.get('trade_date','')
        company = data.get('company','')
        department = data.get('department','')
        portfolio_code = data.get('portfolio_code','')
        stock_symbol = data.get('stock_symbol','')
        
        #构建查询条件
        #build filter conditon 
        filters = []
        if trade_date:
            filters.append(history_holding_show.trade_date == trade_date)
        if company:
            filters.append(history_holding_show.company == company)
        if department:
            filters.append(history_holding_show.department == department)
        if portfolio_code:
            filters.append(history_holding_show.portfolio_code == portfolio_code)
        if stock_symbol:
            filters.append(history_holding_show.stock_symbol == stock_symbol)
            
        #查询要删除的行并进行删除操作
        #query data from database
        row_to_delete = history_holding_show.query.filter(and_(*filters)).first()
        if not row_to_delete:
            return jsonify({'message': 'Data not found'}), 404
        else:    
            db.session.delete(row_to_delete)
            db.session.commit()
            return jsonify({'message': 'Data deleted successfully'}), 200
    #异常处理
    #handle exception
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#-------持仓展示路由------
#-------holding show route------
@app.route('/holdings/show', methods=['GET'])
def output_data():
    try:
        #从请求中参数信息
        #get data from front-end
        selected_stock_code = request.args.get('selectedStockCode', '')
        selected_start_date = request.args.get('selectedStartDate', '')
        selected_end_date = request.args.get('selectedEndDate', '')
        selected_department = request.args.get('selectedDepartment', '')
        selected_portfolio_code = request.args.get('selectedPortfolioCode', '')
        selected_industry = request.args.get('selectedIndustry', '')
        
        #构建查询条件
        #build filter conditon 
        filters = []
        if selected_stock_code:
            filters.append(history_holding_show.stock_symbol == selected_stock_code)
        if selected_start_date:
            filters.append(history_holding_show.trade_date >= selected_start_date)
        if selected_end_date:
            filters.append(history_holding_show.trade_date <= selected_end_date)
        if selected_department:
            filters.append(history_holding_show.department == selected_department)
        if selected_portfolio_code:
            filters.append(history_holding_show.portfolio_code == selected_portfolio_code)
        if selected_industry:
            filters.append(history_holding_show.industry == selected_industry)

        #从数据库中根据筛选条件查询数据并转换成json
        #query data from database and transfer them to json
        holdings_data_all = history_holding_show.query.filter(and_(*filters)).all()
        holdings_data = [{
            'trade_date': holding.trade_date,
            'company': holding.company, 
            'department': holding.department,
            'portfolio_code': holding.portfolio_code, 
            'stock_symbol': holding.stock_symbol, 
            'stock_name': holding.stock_name, 
            'amount': holding.amount, 
            'cost': holding.cost,
            'market_value': holding.market_value, 
            'close_price': holding.close_price, 
            'industry': holding.industry 
            } for holding in holdings_data_all]      
        stock_portfolio_last = pd.DataFrame(holdings_data)
       
       #对数据结果进行判断
       #check the data
        if stock_portfolio_last.empty:
            return jsonify({'message': 'The stock_portfolio_last DataFrame is empty.'})
        else:
            json_data = stock_portfolio_last.to_json(orient='records')
            return json_data
    #异常处理
    #handle exception
    except Exception as e:
       return jsonify({'error': str(e)}), 500

#-------持仓分析路由------
#-------holding analyse route------
@app.route('/holdings/analyse', methods=['POST'])
def analyse_data():
    try:
        #从请求中获取选中行的关键信息
        #get useful parameter from front-end json
        data = request.json
        tradeDate = data.get('tradeDate','')
        analyseLevel = data.get('analyseLevel','')
        department = data.get('department','')
        portfolio_code = data.get('portfolioCode','')
        #转换 tradeDate 字符串为 datetime 对象
        #transfer tradedate format
        trade_date_year = datetime.strptime(tradeDate, '%Y-%m-%d').year

        #构建查询条件
        #build filter conditon 
        filters = []
        if trade_date_year:
            filters.append(func.extract('year', func.to_date(history_holding_show.trade_date, 'YYYY-MM-DD')) == trade_date_year)
        
        #根据 tradeDate 年份筛选数据
        #query data from database
        holdings_data_all = history_holding_show.query.filter(and_(*filters)).all()
        holdings_data = [{
            'trade_date': history_holding_show.trade_date,
            'company': history_holding_show.company, 
            'department': history_holding_show.department,
            'portfolio_code': history_holding_show.portfolio_code, 
            'stock_symbol': history_holding_show.stock_symbol, 
            'stock_name': history_holding_show.stock_name, 
            'amount': history_holding_show.amount, 
            'cost': history_holding_show.cost,
            'market_value': history_holding_show.market_value, 
            'close_price': history_holding_show.close_price, 
            'industry': history_holding_show.industry 
        } for history_holding_show in holdings_data_all]
        stock_portfolio_last = pd.DataFrame(holdings_data)
        
        #调用计算函数并赋值
        #call the calculate function
        table_data, chart1_data, chart2_data, chart3_data = holding_analyze(stock_portfolio_last, analyseLevel, tradeDate, department, portfolio_code)
        
        #对数据结果进行判断
        #check the data
        if table_data.empty and chart1_data.empty and chart2_data.empty and chart3_data.empty:
            return jsonify({'message': 'The table and chart data is empty.'})
        else:
            json_data = {
                'table_data': table_data.reset_index().to_dict(orient='records'),
                'chart1_data': chart1_data.reset_index().to_dict(orient='records'),
                'chart2_data': chart2_data.reset_index().to_dict(orient='records'),
                'chart3_data': chart3_data.reset_index().to_dict(orient='records')
                }
            return json_data
    #异常处理
    #handle exception
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#-------VaR计量路由------
#-------VaR calculate route------
@app.route('/market/var', methods=['POST'])
def var_calculate():
    try:
        #获取前端传来的计量参数    
        #get parameter from front-end
        data = request.json
        tradeDate = data.get('tradeDate','')
        varMethod = data.get('varMethod','')
        confidenceLevel = data.get('confidenceLevel','')
        historicalInterval = data.get('historicalInterval','')
        forecastDays = int(data.get('forecastDays',''))
        pathCount = int(data.get('pathCount',''))
    
        #根据前端来的参数加工计量参数
        #secondary operation parameter
        if historicalInterval == 1:
            c_start_date = datetime.strptime(tradeDate, "%Y-%m-%d") - timedelta(days=365)
            c_start_date = str(c_start_date.strftime("%Y-%m-%d"))
            c_end_date = tradeDate
        elif historicalInterval == 2:
            c_start_date = datetime.strptime(tradeDate, "%Y-%m-%d") - timedelta(days=730)
            c_start_date = str(c_start_date.strftime("%Y-%m-%d"))
            c_end_date = tradeDate
        else:
            c_start_date = datetime.strptime(tradeDate, "%Y-%m-%d") - timedelta(days=1095)
            c_start_date = str(c_start_date.strftime("%Y-%m-%d"))
            c_end_date = tradeDate    
            
        confidence_level = confidenceLevel / 100
        var_percentile = (100 - (confidence_level * 100)) / 100
            
        #构建查询条件
        #build filter conditon 
        filters = []
        if tradeDate:
            filters.append(history_holding_show.trade_date == tradeDate)
        
        #从数据库中读取要计量的数据
        #query data from database
        holdings_data_all = history_holding_show.query.filter(and_(*filters)).all()
        holdings_data = [{
            'trade_date':history_holding_show.trade_date,
            'company':history_holding_show.company, 
            'department':history_holding_show.department,
            'portfolio_code':history_holding_show.portfolio_code, 
            'stock_symbol':history_holding_show.stock_symbol, 
            'stock_name':history_holding_show.stock_name, 
            'amount':history_holding_show.amount, 
            'cost':history_holding_show.cost,
            'market_value':history_holding_show.market_value, 
            'close_price':history_holding_show.close_price, 
            'industry':history_holding_show.industry 
            } for history_holding_show in holdings_data_all]      
        stock_portfolio_calculate = pd.DataFrame(holdings_data)
        
        #加入数据权重
        #preliminary processing data
        stock_portfolio_calculate['portfolio_sum'] = stock_portfolio_calculate.groupby('portfolio_code')['market_value'].transform('sum')
        stock_portfolio_calculate['department_sum'] = stock_portfolio_calculate.groupby('department')['market_value'].transform('sum')
        stock_portfolio_calculate['company_sum'] = stock_portfolio_calculate.groupby('company')['market_value'].transform('sum')
        stock_portfolio_calculate['portfolio_weight'] = stock_portfolio_calculate['market_value'] / stock_portfolio_calculate.groupby('portfolio_code')['market_value'].transform('sum')
        stock_portfolio_calculate['department_weight'] = stock_portfolio_calculate['market_value'] / stock_portfolio_calculate.groupby('department')['market_value'].transform('sum')
        stock_portfolio_calculate['company_weight'] = stock_portfolio_calculate['market_value'] / stock_portfolio_calculate.groupby('company')['market_value'].transform('sum')

        #call the calculate function
        returns_single_stock_plr, returns_portfolio_stock_plr, returns_department_stock_plr, returns_company_stock_plr, returns_company_stock_plr_groupby, returns_company_stock_plr_chart = calculate_var(stock_portfolio_calculate, c_start_date, c_end_date, varMethod, var_percentile, forecastDays, pathCount, confidence_level)
        var_show_front, var_para_chart_data = var_result(varMethod, stock_portfolio_calculate, returns_single_stock_plr, returns_portfolio_stock_plr, returns_department_stock_plr, returns_company_stock_plr, returns_company_stock_plr_groupby, returns_company_stock_plr_chart)
        #对数据结果进行判断
        #check the data
        if var_show_front.empty or var_para_chart_data.empty:
            return jsonify({'message': 'The table and chart data is empty.'})
        else:
            json_data = {'table_data': var_show_front.to_dict(orient='records'), 'chart_data': var_para_chart_data.to_dict(orient='records')}
            return json_data
    #异常处理
    #handle exception
    except Exception as e:
          return jsonify({'error': str(e)}), 500
   
#---------------------------------主程序开始---------------------------------------
#-----------------------------main app start--------------------------------------
if __name__ == '__main__':
    schedule_task(app)
    app.run(host='localhost', port=3000, debug=False)