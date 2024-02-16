#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 22:04:20 2024

@author: qinxiangyuan
"""

import pandas as pd
import baostock as bs

def fetch_stock_data(stock_portfolio):
    #登录证券宝
    #login to baostock
    lg = bs.login()
    if lg.error_code != '0':
        raise Exception(f'登录证券宝失败，错误代码：{lg.error_code}, 错误信息：{lg.error_msg}')
    
    try:
        #获取证券额外信息
        #get extra stock info
        stock_mark = stock_portfolio[['trade_date','stock_symbol']]
        stock_merge = pd.DataFrame()
        stock_price_acu = pd.DataFrame()
        stock_info_acu = pd.DataFrame()

        for i in stock_mark.itertuples(index=False):
            #查询证券价格信息
            #query stock close price
            stock_price = bs.query_history_k_data(i.stock_symbol, "date,code,close", start_date=i.trade_date, end_date=i.trade_date, frequency="d", adjustflag="3")
            result_list_price = []
            while (stock_price.error_code == '0') & stock_price.next():
                result_list_price.append(stock_price.get_row_data())
                result_price = pd.DataFrame(result_list_price, columns=stock_price.fields)
                result_price['close'] = result_price['close'].astype(float)
            stock_price_acu = pd.concat([stock_price_acu, result_price])

            #查询证券信息
            #query stock info
            stock_info = bs.query_stock_industry(code=i.stock_symbol)
            result_list_info = []
            while (stock_info.error_code == '0') & stock_info.next():
                result_list_info.append(stock_info.get_row_data())
                result_info = pd.DataFrame(result_list_info, columns=stock_info.fields)
            stock_info_acu = pd.concat([stock_info_acu, result_info])

        #拼接数据
        #concatenated data
        stock_merge = pd.merge(stock_price_acu, stock_info_acu, on='code', how='inner') 
        stock_merge = stock_merge.drop_duplicates()
        stock_portfolio_last = stock_portfolio.merge(stock_merge, left_on=['trade_date','stock_symbol'], right_on=['date','code'],how = 'inner')

        #数据处理
        #data process
        columns_to_drop = ['date', 'code', 'updateDate', 'industryClassification']
        stock_portfolio_last.drop(columns=columns_to_drop, inplace=True)
        new_column_names = {'close': 'close_price', 'code_name': 'stock_name'}
        stock_portfolio_last.rename(columns=new_column_names, inplace=True)
        new_column_order = ['trade_date', 'company','department', 'portfolio_code', 'stock_symbol', 'stock_name', 'cost', 'amount', 'close_price', 'industry']
        stock_portfolio_last = stock_portfolio_last.reindex(columns=new_column_order)
        stock_portfolio_last.insert(8, 'market_value', stock_portfolio_last['amount'] * stock_portfolio_last['close_price'])    

        return stock_portfolio_last
    finally:
        #登出证券宝
        #log out baostock
        bs.logout()