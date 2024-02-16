#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:50:19 2024

@author: qinxiangyuan
"""
import pandas as pd
import numpy as np
from scipy.stats import norm
import baostock as bs

def calculate_log_returns(stock_portfolio_calculate, c_start_date, c_end_date):
    #登录证券宝
    #login baostock
    lg = bs.login()
    if lg.error_code != '0':
        raise Exception(f'登录证券宝失败，错误代码：{lg.error_code}, 错误信息：{lg.error_msg}')
    try:
        #获取明细证券的历史数据
        #get stock history close price
        stock_symbol = stock_portfolio_calculate['stock_symbol'].drop_duplicates()
        returns_single_stock_last = pd.DataFrame()
        result = pd.DataFrame()

        #循环查询每只股票的历史数据并计算对数收益率
        #Loop through to query historical data for each stock and calculate logarithmic returns
        for i in stock_symbol:
            #查询股票历史数据
            #query stock history data
            stock_data = bs.query_history_k_data(i, "date,code,close", start_date=c_start_date, end_date=c_end_date, frequency="d", adjustflag="3")
        
            #格式化股票数据
            #format stock data
            result_list = []
            while (stock_data.error_code == '0') & stock_data.next():
                result_list.append(stock_data.get_row_data())
                result = pd.DataFrame(result_list, columns=stock_data.fields)
                result['close'] = result['close'].astype(float)   
                #计算单只股票每一天算数收益率
                #Calculate daily arithmetic returns for a single stock
                returns_single_stock = result['close'].pct_change().dropna() 
                log_returns_single_stock = np.log(1 + returns_single_stock)
                result.insert(3, 'returns_single_stock', returns_single_stock)
                result.insert(4, 'log_returns_single_stock', log_returns_single_stock)
            returns_single_stock_last = pd.concat([returns_single_stock_last, result])
            returns_single_stock_last.dropna(inplace=True)
        return returns_single_stock_last
    
    finally:
        #登出证券宝
        #logout baostock
        bs.logout()

def calculate_var(stock_portfolio_calculate, c_start_date, c_end_date, varMethod, var_percentile, forecastDays, pathCount, confidence_level):
    #计算对数收益率并且拼接数据
    #Calculate logarithmic returns and concatenate data
    returns_single_stock_last = calculate_log_returns(stock_portfolio_calculate, c_start_date, c_end_date)
    returns_stock_detail = stock_portfolio_calculate.merge(returns_single_stock_last, left_on=['stock_symbol'], right_on=['code'],how = 'inner')

    if varMethod == 'historical':
        #图表数据集处理
        #Processing of dataset for chart/graph
        #最明细证券
        #single stock
        returns_single_stock_plr = returns_single_stock_last.groupby('code')['log_returns_single_stock'].quantile(var_percentile).reset_index(name='log_returns_single_stock')
        returns_single_stock_plr['log_returns_single_stock_forecas'] = returns_single_stock_plr['log_returns_single_stock'] * np.sqrt(forecastDays)
        
        #投资组合
        #portfolio
        returns_portfolio_stock_plr_groupby = returns_stock_detail.groupby(['portfolio_code', 'date']).apply(lambda x: (x['portfolio_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_portfolio_daily')
        returns_portfolio_stock_plr = returns_portfolio_stock_plr_groupby.groupby('portfolio_code')['log_returns_portfolio_daily'].quantile(var_percentile).reset_index(name='log_returns_portfolio')
        returns_portfolio_stock_plr['log_returns_portfolio_forecas'] = returns_portfolio_stock_plr['log_returns_portfolio'] * np.sqrt(forecastDays)
        
        #部门
        #department
        returns_department_stock_plr_groupby = returns_stock_detail.groupby(['department', 'date']).apply(lambda x: (x['department_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_department_daily')
        returns_department_stock_plr = returns_department_stock_plr_groupby.groupby('department')['log_returns_department_daily'].quantile(var_percentile).reset_index(name='log_returns_department')
        returns_department_stock_plr['log_returns_department_forecas'] = returns_department_stock_plr['log_returns_department'] * np.sqrt(forecastDays)
        
        #公司
        #company
        returns_company_stock_plr_groupby = returns_stock_detail.groupby(['company','date']).apply(lambda x: (x['company_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_company_daily')
        returns_company_stock_plr = returns_company_stock_plr_groupby.groupby('company')['log_returns_company_daily'].quantile(var_percentile).reset_index(name='log_returns_company')
        returns_company_stock_plr['log_returns_company_forecas'] = returns_company_stock_plr['log_returns_company'] * np.sqrt(forecastDays)
        returns_company_stock_plr_chart = None
        
    elif varMethod == 'parametric':
        #设置分布参数
        #Set distribution parameters
        alpha = norm.ppf(confidence_level)
        
        #图表数据集处理
        #Processing of dataset for chart/graph
        #最明细证券
        #single stock
        returns_single_stock_plr_mean = returns_single_stock_last.groupby('code')['log_returns_single_stock'].mean().reset_index()
        returns_single_stock_plr_mean.columns = ['code', 'log_returns_single_stock_mean']
        returns_single_stock_plr_std = returns_single_stock_last.groupby('code')['log_returns_single_stock'].std().reset_index()
        returns_single_stock_plr_std.columns = ['code', 'log_returns_single_stock_std']
        returns_single_stock_plr = pd.merge(returns_single_stock_plr_mean, returns_single_stock_plr_std, on='code', how='inner') 
        returns_single_stock_plr.insert(3, 'log_returns_single_stock_plr',-1 * (returns_single_stock_plr['log_returns_single_stock_mean'] + alpha * returns_single_stock_plr['log_returns_single_stock_std']))
        returns_single_stock_plr['log_returns_single_stock_forecas'] = returns_single_stock_plr['log_returns_single_stock_plr'] * np.sqrt(forecastDays)
        columns_to_drop = ['log_returns_single_stock_mean', 'log_returns_single_stock_std']
        returns_single_stock_plr.drop(columns=columns_to_drop, inplace=True)
        
        #投资组合
        #portfolio
        returns_portfolio_stock_plr_groupby = returns_stock_detail.groupby(['portfolio_code', 'date']).apply(lambda x: (x['portfolio_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_portfolio_daily')
        returns_portfolio_stock_plr_mean = returns_portfolio_stock_plr_groupby.groupby('portfolio_code')['log_returns_portfolio_daily'].mean().reset_index(name='log_returns_portfolio_mean')
        returns_portfolio_stock_plr_std = returns_portfolio_stock_plr_groupby.groupby('portfolio_code')['log_returns_portfolio_daily'].std().reset_index(name='log_returns_portfolio_std')
        returns_portfolio_stock_plr = pd.merge(returns_portfolio_stock_plr_mean, returns_portfolio_stock_plr_std, on='portfolio_code', how='inner') 
        returns_portfolio_stock_plr.insert(3, 'log_returns_portfolio_stock_plr',-1 * (returns_portfolio_stock_plr['log_returns_portfolio_mean'] + alpha * returns_portfolio_stock_plr['log_returns_portfolio_std']))
        returns_portfolio_stock_plr['log_returns_portfolio_forecas'] = returns_portfolio_stock_plr['log_returns_portfolio_stock_plr'] * np.sqrt(forecastDays)
        columns_to_drop = ['log_returns_portfolio_mean', 'log_returns_portfolio_std']
        returns_portfolio_stock_plr.drop(columns=columns_to_drop, inplace=True)
        
        #部门
        #department
        returns_department_stock_plr_groupby = returns_stock_detail.groupby(['department', 'date']).apply(lambda x: (x['department_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_department_daily')
        returns_department_stock_plr_mean = returns_department_stock_plr_groupby.groupby('department')['log_returns_department_daily'].mean().reset_index(name='log_returns_department_mean')
        returns_department_stock_plr_std = returns_department_stock_plr_groupby.groupby('department')['log_returns_department_daily'].std().reset_index(name='log_returns_department_std')
        returns_department_stock_plr = pd.merge(returns_department_stock_plr_mean, returns_department_stock_plr_std, on='department', how='inner') 
        returns_department_stock_plr.insert(3, 'log_returns_department_stock_plr',-1 * (returns_department_stock_plr['log_returns_department_mean'] + alpha * returns_department_stock_plr['log_returns_department_std']))
        returns_department_stock_plr['log_returns_department_forecas'] = returns_department_stock_plr['log_returns_department_stock_plr'] * np.sqrt(forecastDays)
        columns_to_drop = ['log_returns_department_mean', 'log_returns_department_std']
        returns_department_stock_plr.drop(columns=columns_to_drop, inplace=True)
        
        #公司
        #company
        returns_company_stock_plr_groupby = returns_stock_detail.groupby(['company','date']).apply(lambda x: (x['company_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_company_daily')
        returns_company_stock_plr_mean = returns_company_stock_plr_groupby.groupby('company')['log_returns_company_daily'].mean().reset_index(name='log_returns_company_mean')
        returns_company_stock_plr_std = returns_company_stock_plr_groupby.groupby('company')['log_returns_company_daily'].std().reset_index(name='log_returns_company_std')
        returns_company_stock_plr = pd.merge(returns_company_stock_plr_mean, returns_company_stock_plr_std, on='company', how='inner') 
        returns_company_stock_plr.insert(3, 'log_returns_company_stock_plr',-1 * (returns_company_stock_plr['log_returns_company_mean'] + alpha * returns_company_stock_plr['log_returns_company_std']))
        returns_company_stock_plr['log_returns_company_forecas'] = returns_company_stock_plr['log_returns_company_stock_plr'] * np.sqrt(forecastDays)
        columns_to_drop = ['log_returns_company_mean', 'log_returns_company_std']
        returns_company_stock_plr.drop(columns=columns_to_drop, inplace=True)
        returns_company_stock_plr_chart = None
    
    else:
        #设置模拟次数
        #set simulation times
        mc_num = pathCount
        
        #图表数据集处理
        #Processing of dataset for chart/graph
        #最明细证券
        #single stock
        returns_single_stock_plr_mean = returns_single_stock_last.groupby('code')['log_returns_single_stock'].mean().reset_index()
        returns_single_stock_plr_mean.columns = ['code', 'log_returns_single_stock_mean']
        returns_single_stock_plr_std = returns_single_stock_last.groupby('code')['log_returns_single_stock'].std().reset_index()
        returns_single_stock_plr_std.columns = ['code', 'log_returns_single_stock_std']
        returns_single_stock_plr = pd.merge(returns_single_stock_plr_mean, returns_single_stock_plr_std, on='code', how='inner') 
        returns_single_stock_plr['monte_carlo_simulations'] = returns_single_stock_plr.apply(lambda row: np.random.normal(row['log_returns_single_stock_mean'], row['log_returns_single_stock_std'], (mc_num, forecastDays)), axis=1)
        returns_single_stock_plr['monte_carlo_simulations_cum'] = returns_single_stock_plr['monte_carlo_simulations'].apply(lambda x: np.cumprod(1 + x, axis=1) - 1)
        returns_single_stock_plr['log_returns_single_stock_forecas'] = returns_single_stock_plr['monte_carlo_simulations_cum'].apply(lambda x: np.percentile(x[:, -1], var_percentile * 100))
        columns_to_drop = ['log_returns_single_stock_mean', 'log_returns_single_stock_std', 'monte_carlo_simulations','monte_carlo_simulations_cum']
        returns_single_stock_plr.drop(columns=columns_to_drop, inplace=True)


        #投资组合
        #portfolio
        returns_portfolio_stock_plr_groupby = returns_stock_detail.groupby(['portfolio_code', 'date']).apply(lambda x: (x['portfolio_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_portfolio_daily')
        returns_portfolio_stock_plr_mean = returns_portfolio_stock_plr_groupby.groupby('portfolio_code')['log_returns_portfolio_daily'].mean().reset_index(name='log_returns_portfolio_mean')
        returns_portfolio_stock_plr_std = returns_portfolio_stock_plr_groupby.groupby('portfolio_code')['log_returns_portfolio_daily'].std().reset_index(name='log_returns_portfolio_std')
        returns_portfolio_stock_plr = pd.merge(returns_portfolio_stock_plr_mean, returns_portfolio_stock_plr_std, on='portfolio_code', how='inner') 
        returns_portfolio_stock_plr['monte_carlo_simulations'] = returns_portfolio_stock_plr.apply(lambda row: np.random.normal(row['log_returns_portfolio_mean'], row['log_returns_portfolio_std'], (mc_num, forecastDays)), axis=1)
        returns_portfolio_stock_plr['monte_carlo_simulations_cum'] = returns_portfolio_stock_plr['monte_carlo_simulations'].apply(lambda x: np.cumprod(1 + x, axis=1) - 1)
        returns_portfolio_stock_plr['log_returns_portfolio_forecas'] = returns_portfolio_stock_plr['monte_carlo_simulations_cum'].apply(lambda x: np.percentile(x[:, -1], var_percentile * 100))
        columns_to_drop = ['log_returns_portfolio_mean', 'log_returns_portfolio_std', 'monte_carlo_simulations','monte_carlo_simulations_cum']
        returns_portfolio_stock_plr.drop(columns=columns_to_drop, inplace=True)
        
        #部门
        #department
        returns_department_stock_plr_groupby = returns_stock_detail.groupby(['department', 'date']).apply(lambda x: (x['department_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_department_daily')
        returns_department_stock_plr_mean = returns_department_stock_plr_groupby.groupby('department')['log_returns_department_daily'].mean().reset_index(name='log_returns_department_mean')
        returns_department_stock_plr_std = returns_department_stock_plr_groupby.groupby('department')['log_returns_department_daily'].std().reset_index(name='log_returns_department_std')
        returns_department_stock_plr = pd.merge(returns_department_stock_plr_mean, returns_department_stock_plr_std, on='department', how='inner') 
        returns_department_stock_plr['monte_carlo_simulations'] = returns_department_stock_plr.apply(lambda row: np.random.normal(row['log_returns_department_mean'], row['log_returns_department_std'], (mc_num, forecastDays)), axis=1)
        returns_department_stock_plr['monte_carlo_simulations_cum'] = returns_department_stock_plr['monte_carlo_simulations'].apply(lambda x: np.cumprod(1 + x, axis=1) - 1)
        returns_department_stock_plr['log_returns_department_forecas'] = returns_department_stock_plr['monte_carlo_simulations_cum'].apply(lambda x: np.percentile(x[:, -1], var_percentile * 100))
        columns_to_drop = ['log_returns_department_mean', 'log_returns_department_std', 'monte_carlo_simulations','monte_carlo_simulations_cum']
        returns_department_stock_plr.drop(columns=columns_to_drop, inplace=True)
        
        #公司
        #company
        returns_company_stock_plr_groupby = returns_stock_detail.groupby(['company','date']).apply(lambda x: (x['company_weight'] * x['log_returns_single_stock']).sum()).reset_index(name='log_returns_company_daily')
        returns_company_stock_plr_mean = returns_company_stock_plr_groupby.groupby('company')['log_returns_company_daily'].mean().reset_index(name='log_returns_company_mean') 
        returns_company_stock_plr_std = returns_company_stock_plr_groupby.groupby('company')['log_returns_company_daily'].std().reset_index(name='log_returns_company_std')
        returns_company_stock_plr = pd.merge(returns_company_stock_plr_mean, returns_company_stock_plr_std, on='company', how='inner') 
        returns_company_stock_plr['monte_carlo_simulations'] = returns_company_stock_plr.apply(lambda row: np.random.normal(row['log_returns_company_mean'], row['log_returns_company_std'], (mc_num, forecastDays)), axis=1)
        returns_company_stock_plr['monte_carlo_simulations_cum'] = returns_company_stock_plr['monte_carlo_simulations'].apply(lambda x: np.cumprod(1 + x, axis=1) - 1)
        returns_company_stock_plr['log_returns_company_forecas'] = returns_company_stock_plr['monte_carlo_simulations_cum'].apply(lambda x: np.percentile(x[:, -1], var_percentile * 100))
        returns_company_stock_plr_chart = returns_company_stock_plr.copy()      
        columns_to_drop = ['log_returns_company_mean', 'log_returns_company_std', 'monte_carlo_simulations','monte_carlo_simulations_cum']
        returns_company_stock_plr.drop(columns=columns_to_drop, inplace=True)
    
    return returns_single_stock_plr, returns_portfolio_stock_plr, returns_department_stock_plr, returns_company_stock_plr, returns_company_stock_plr_groupby, returns_company_stock_plr_chart

