#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:40:06 2024

@author: qinxiangyuan
"""

import pandas as pd

def holding_analyze(stock_portfolio_last, analyseLevel, tradeDate, department, portfolio_code):
    if analyseLevel == 'company':
        #(1) 查询日期当天的汇总后公司前十大股票的信息并且倒序排列
        #(1) Retrieve information on the top ten stocks of the company aggregated on the current date, sorted in descending order
        condition = stock_portfolio_last['trade_date'] == tradeDate
        condition1 = stock_portfolio_last['trade_date'] <= tradeDate
        stock_analyse_tradedate = stock_portfolio_last[condition]
        stock_analyse = stock_portfolio_last[condition1]
        table_data = stock_analyse_tradedate.groupby(['stock_symbol', 'stock_name']).sum()['market_value'].nlargest(10)
        #(2) 查询日期同一年的公司每一天市值汇总值的列表数据
        #(2) Retrieve a list of aggregated daily market values for the company throughout the selected date's year
        chart1_data = stock_analyse.groupby(['trade_date']).sum()['market_value']
        #(3) 查询日期当天以公司汇总的市值的集中度
        #(3) Retrieve the concentration of market value aggregated by the company on the selected date
        market_value_by_department = stock_analyse_tradedate.groupby('department').sum()['market_value']
        market_value_ratio_by_department = market_value_by_department / market_value_by_department.sum()
        market_value_ratio_by_department = market_value_ratio_by_department.rename('market_value_ratio')
        chart2_data = pd.concat([market_value_by_department, market_value_ratio_by_department], axis=1)
        chart2_data = chart2_data.rename_axis('organization')
        #(4) 查询日期当天以行业汇总的市值的集中度
        #(4) Retrieve the concentration of market value aggregated by industry on the selected date
        market_value_by_industry = stock_analyse_tradedate.groupby('industry').sum()['market_value']
        market_value_ratio_by_industry = market_value_by_industry / market_value_by_industry.sum()
        market_value_ratio_by_industry = market_value_ratio_by_industry.rename('market_value_ratio')
        chart3_data = pd.concat([market_value_by_industry, market_value_ratio_by_industry], axis=1)        
    
    elif analyseLevel == 'department':
        #获取参数
        #get parameter
        department = department
        #(1) 查询日期当天的汇总后部门前十大股票的信息并且倒序排列
        #(1) Retrieve information on the top ten stocks of the department aggregated on the current date, sorted in descending order
        condition = (stock_portfolio_last['trade_date'] == tradeDate) & (stock_portfolio_last['department'] == department)
        condition1 = (stock_portfolio_last['department'] == department) & (stock_portfolio_last['trade_date'] <= tradeDate)
        stock_analyse_tradedate = stock_portfolio_last[condition]
        stock_analyse = stock_portfolio_last[condition1]
        table_data = stock_analyse_tradedate.groupby(['stock_symbol', 'stock_name']).sum()['market_value'].nlargest(10)
        #(2) 查询日期同一年的部门每一天市值汇总值的列表数据
        #(2) Retrieve a list of aggregated daily market values for the department throughout the selected date's year
        chart1_data = stock_analyse.groupby(['trade_date']).sum()['market_value']
        #(3) 查询日期当天以部门汇总的市值的集中度
        #(3) Retrieve the concentration of market value aggregated by the department on the selected date
        market_value_by_portfolio = stock_analyse_tradedate.groupby('portfolio_code').sum()['market_value']
        market_value_ratio_by_portfolio = market_value_by_portfolio / market_value_by_portfolio.sum()
        market_value_ratio_by_portfolio = market_value_ratio_by_portfolio.rename('market_value_ratio')
        chart2_data = pd.concat([market_value_by_portfolio, market_value_ratio_by_portfolio], axis=1)
        chart2_data = chart2_data.rename_axis('organization')
        #(4) 查询日期当天以行业汇总的市值的集中度
        #(4) Retrieve the concentration of market value aggregated by industry on the selected date
        market_value_by_industry = stock_analyse_tradedate.groupby('industry').sum()['market_value']
        market_value_ratio_by_industry = market_value_by_industry / market_value_by_industry.sum()
        market_value_ratio_by_industry = market_value_ratio_by_industry.rename('market_value_ratio')
        chart3_data = pd.concat([market_value_by_industry, market_value_ratio_by_industry], axis=1)
    
    else:
        #获取参数
        #get parameter
        department = department
        portfolio_code = portfolio_code
        #(1) 查询日期当天的汇总后组合前十大股票的信息并且倒序排列
        #(1) Retrieve information on the top ten stocks of the portfolio aggregated on the current date, sorted in descending order
        condition = (stock_portfolio_last['trade_date'] == tradeDate) & (stock_portfolio_last['department'] == department) & (stock_portfolio_last['portfolio_code'] == portfolio_code)
        condition1 = (stock_portfolio_last['department'] == department) & (stock_portfolio_last['portfolio_code'] == portfolio_code) & (stock_portfolio_last['trade_date'] <= tradeDate)
        stock_analyse_tradedate = stock_portfolio_last[condition]
        stock_analyse = stock_portfolio_last[condition1]
        table_data = stock_analyse_tradedate.groupby(['stock_symbol', 'stock_name']).sum()['market_value'].nlargest(10)
        #(2) 查询日期同一年的组合每一天市值汇总值的列表数据
        #(2) Retrieve a list of aggregated daily market values for the portfolio throughout the selected date's year
        chart1_data = stock_analyse.groupby(['trade_date']).sum()['market_value']
        #(3) 查询日期当天以组合汇总的市值的集中度
        #(3) Retrieve the concentration of market value aggregated by the portfolio on the selected date
        market_value_by_stock = stock_analyse_tradedate.groupby('stock_symbol').sum()['market_value']
        market_value_ratio_by_stock = market_value_by_stock / market_value_by_stock.sum()
        market_value_ratio_by_stock = market_value_by_stock.rename('market_value_ratio')
        chart2_data = pd.concat([market_value_by_stock, market_value_ratio_by_stock], axis=1)
        chart2_data = chart2_data.rename_axis('organization')
        #(4) 查询日期当天以行业汇总的市值的集中度
        #(4) Retrieve the concentration of market value aggregated by industry on the selected date
        market_value_by_industry = stock_analyse_tradedate.groupby('industry').sum()['market_value']
        market_value_ratio_by_industry = market_value_by_industry / market_value_by_industry.sum()
        market_value_ratio_by_industry = market_value_ratio_by_industry.rename('market_value_ratio')
        chart3_data = pd.concat([market_value_by_industry, market_value_ratio_by_industry], axis=1)
        
    return table_data, chart1_data, chart2_data, chart3_data

def var_result(varMethod, stock_portfolio_calculate, returns_single_stock_plr, returns_portfolio_stock_plr, returns_department_stock_plr, returns_company_stock_plr, returns_company_stock_plr_groupby, returns_company_stock_plr_chart):
    #二维表格数据
    #Two-dimensional tabular data
    #组合各个层级的数据
    #Combine data from various levels
    var_single_stock = stock_portfolio_calculate.merge(returns_single_stock_plr, left_on=['stock_symbol'], right_on=['code'],how = 'inner')
    var_portfolio_stock = var_single_stock.merge(returns_portfolio_stock_plr, left_on=['portfolio_code'], right_on=['portfolio_code'],how = 'inner')
    var_department_stock = var_portfolio_stock.merge(returns_department_stock_plr, left_on=['department'], right_on=['department'],how = 'inner')
    var_company_stock = var_department_stock.merge(returns_company_stock_plr, left_on=['company'], right_on=['company'],how = 'inner')

    var_company_stock['stock_VaR'] = var_company_stock['market_value'] * var_company_stock['log_returns_single_stock_forecas'] 
    var_company_stock['portfolio_VaR'] = var_company_stock['portfolio_sum'] * var_company_stock['log_returns_portfolio_forecas'] 
    var_company_stock['department_VaR'] = var_company_stock['department_sum'] * var_company_stock['log_returns_department_forecas'] 
    var_company_stock['company_VaR'] = var_company_stock['company_sum'] * var_company_stock['log_returns_company_forecas'] 
    
    var_show = var_company_stock[['company','company_sum','company_VaR','department','department_sum','department_VaR','portfolio_code','portfolio_sum','portfolio_VaR','stock_symbol','stock_name','market_value','stock_VaR']]
    
    #处理成前端所需要的样式
    #Process into the style required by the frontend
    var_show_front = var_show
    var_show_front['stock_symbol'] = var_show_front['stock_symbol'] + '.' + var_show_front['stock_name']
    var_show_front.drop(columns='stock_name', inplace=True)
    
    #图表数据
    #chart data
    if varMethod == 'historical' or varMethod == 'parametric':
        columns_to_drop = ['company']
        returns_company_stock_plr_groupby.drop(columns=columns_to_drop, inplace=True)
        var_para_chart_data = returns_company_stock_plr_groupby
    else:
        columns_to_drop = ['log_returns_company_mean', 'log_returns_company_std','log_returns_company_forecas','monte_carlo_simulations','company']
        returns_company_stock_plr_chart.drop(columns=columns_to_drop, inplace=True)
        data = returns_company_stock_plr_chart['monte_carlo_simulations_cum'].apply(lambda x: x.tolist()).tolist()
        var_para_chart_data = pd.concat([pd.DataFrame(x) for x in data], axis=0, ignore_index=True)
        var_para_chart_data.columns = [f'{i+1}' for i in range(var_para_chart_data.shape[1])]
        var_para_chart_data.insert(0, '0', 0)
        
    return var_show_front, var_para_chart_data


