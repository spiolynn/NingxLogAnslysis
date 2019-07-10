# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 16:36
# @Author  : hoo
# @Site    : 
# @File    : NginxLogStatistical.py
# @Software: PyCharm Community Edition

'''
nginx log Statistical
'''

import pandas as pd
import datetime
from tabulate import tabulate

def TradeMode(file):
    '''
    初始化交易白名单
    :param file:
    :return:
    '''
    tradeList = pd.read_csv(file,sep='@',error_bad_lines=False)
    return tradeList


def LogStatis(file,trademodefile):

    '''
    日志统计分析
    :param file:
    :param trademode:
    :return:
    '''

    # 数据初始化
    tradeList = TradeMode(trademodefile)
    nginx_df = pd.read_csv(file,sep='@',parse_dates=['r_time_local_time'],error_bad_lines=False)

    if len(nginx_df) == 0 :
        print("pandas data is empty")
        return

    nginx_df["r_request_time"] = nginx_df["r_request_time"].astype(float)
    nginx_df["r_upstream_response_time"] = nginx_df["r_upstream_response_time"].astype(float)


    ## 根据 url group by
    logfile =  "show1_" + (datetime.datetime.now()).strftime('%Y%m%d')
    logfilef = open(logfile, 'w', encoding='utf-8')
    logfile1 = "show2_" +(datetime.datetime.now()).strftime('%Y%m%d')
    logfilef1 = open(logfile1, 'w', encoding='utf-8')


    #######################################################
    ## 1 交易时间统计
    df1 = nginx_df.groupby('r_request_url_real')['r_request_time'].describe()
    # df1.sort_values("count", inplace=True)
    # result = tabulate(df1, headers='keys', tablefmt='psql')
    # logfilef.write(str(result) + "\n")


    # 筛选r_request_time 小于200ms 数据
    df_l_200 = nginx_df[(nginx_df["r_request_time"]<=0.2)]
    df_l_500 = nginx_df[ (nginx_df["r_request_time"] > 0.2) & (nginx_df["r_request_time"] < 0.5) ]
    df_l_500max = nginx_df[(nginx_df["r_request_time"]>=0.5)]

    # 统计r_request_time 小于200ms 数据个数
    df_l_200_count = df_l_200.groupby('r_request_url_real')['r_request_time'].count()
    df_l_500_count = df_l_500.groupby('r_request_url_real')['r_request_time'].count()
    df_l_500max_count = df_l_500max.groupby('r_request_url_real')['r_request_time'].count()

    # reset index
    df_l_200_count = df_l_200_count.reset_index()
    df_l_500_count = df_l_500_count.reset_index()
    df_l_500max_count = df_l_500max_count.reset_index()

    # 合并数据
    p = pd.merge(df_l_200_count, df_l_500_count, how='outer', on='r_request_url_real')
    p1 = pd.merge(p, df_l_500max_count, how='outer', on='r_request_url_real')
    df2 = pd.merge(df1, p1, how='outer', on='r_request_url_real')

    # 合并表 排序by count
    df2.sort_values("count", inplace=True)

    #  rename title
    df2.rename(columns={'r_request_time_x': '200ms', 'r_request_time_y': '200-500ms','r_request_time':'500ms+'}, inplace=True)

    _200ms_p = df2["200ms"] / df2["count"]
    _500ms_p = df2["200-500ms"] / df2["count"]
    _500msp_p = df2["500ms+"] / df2["count"]
    _200ms_p = _200ms_p.apply(lambda x: format(x, '.2%'))
    _500ms_p = _500ms_p.apply(lambda x: format(x, '.2%'))
    _500msp_p = _500msp_p.apply(lambda x: format(x, '.2%'))
    df2['200ms'] = _200ms_p
    df2['200-500ms'] = _500ms_p
    df2['500ms+'] = _500msp_p

    #  白名单标记
    for index, row in tradeList.iterrows():
        df2.loc[df2['r_request_url_real'] == row['trade'], 'r_request_url_real'] = df2.loc[df2['r_request_url_real'] == row['trade'], 'r_request_url_real'].map(lambda x: "ok  "+x)

    #  save log
    result = tabulate(df2, headers='keys', tablefmt='psql')
    logfilef.write(str(result) + "\n")



    #######################################################
    ## 2 交易占比统计

    # group by r_request_url_real','r_stutas  统计
    pd_status_count = nginx_df.groupby(['r_request_url_real','r_stutas'])['r_trade_key_str'].count()
    pd_status_count = pd.DataFrame(pd_status_count)
    pd_status_count = pd_status_count.reset_index()

    # group by r_request_url_real 统计
    pd_status_sum = nginx_df.groupby(['r_request_url_real'])['r_trade_key_str'].count()
    pd_status_sum = pd.DataFrame(pd_status_sum)
    pd_status_sum = pd_status_sum.reset_index()

    # merge
    p = pd.merge(pd_status_count, pd_status_sum, how='outer', on='r_request_url_real')

    # 百分比
    m = p["r_trade_key_str_x"] / p["r_trade_key_str_y"]
    m = m.apply(lambda x: format(x, '.2%'))
    p["rate"] = m

    # rename
    p.rename(columns={'r_trade_key_str_x': 'status_count', 'r_trade_key_str_7': 'sum'},
               inplace=True)

    # save log
    result1 = (tabulate(p, headers='keys', tablefmt='psql'))
    logfilef1.write(str(result1) + "\n")