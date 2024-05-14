import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine, text


def plot_author():
    """
    绘制用户发帖数量的直方图
    :return:
    """
    filename = "D:/eastmoney-guba-main/database/east_guba_cmt.csv"
    data = pd.read_csv(filename, names=["code", "dtime", "title", "author"], header=0)
    data = data[data["code"] == "600999"]
    all_trade_days = pd.read_csv("ALL_TRADE_DAYS", header=None)

    authors= list(data["author"])
    x=[]
    for i in set(authors):
        x.append([i,authors.count(i)])
    df = pd.DataFrame(x)
    df.columns = ['author','count']
    df.sort_values('count', inplace=True,ascending=False)
    plt.hist(df['count'], bins=20, color='blue', alpha=0.5)
    plt.show()


def plot_dtime():
    """
    绘制评论数量与收盘价格的复合折线图
    :return:
    """
    filename = "D:/eastmoney-guba-main/database/east_guba_cmt.csv"
    data = pd.read_csv(filename, names=["code", "dtime", "title", "author"], header=0)
    data = data[data["code"] == "600999"]
    all_trade_days = pd.read_csv("ALL_TRADE_DAYS", header=None)

    dtime = list(data['dtime'].str.slice(0, 10))
    x=[]
    for i in set(dtime):
        x.append([i,dtime.count(i)])
    df = pd.DataFrame(x)
    df.columns = ['dtime','count']
    df = df.loc[df['dtime'].isin(list(all_trade_days[0]))]

    # def dt_convert(dtime):
    #     # change '2020/1/1' to '20200101'
    #     # datetime.strptime('2020/1/1','%Y/%m/%d').strftime("%Y%m%d")
    #     return datetime.strptime(dtime,'%Y-%m-%d').strftime("%Y%m%d")
    # df['dtime'] = df["dtime"].apply(dt_convert)

    df['dtime'] = df['dtime'].str.replace('-', '')
    df.sort_values('dtime', inplace=True,ascending=True)
    df.columns = ['trade_date','count']

    #plt.plot(np.arange(len(df)),df['count'])
    #plt.show()

    sql = "SELECT * FROM finance.pro_stock_daily where ts_code='600999.SH' AND trade_date between '20200102' AND '20200902';"
    conn = create_engine('mysql://username:password@hostname:3306/finance?charset=utf8')
    price = pd.read_sql(text(sql), conn.connect())

    # plt.plot(np.arange(len(price)),price['close'])
    # plt.show()

    df_all = pd.merge(df, price, on='trade_date', how='inner')
    #df_all = pd.merge(df, price, on='trade_date', how='right')
    #df_all.fillna(0,inplace=True)

    fig,ax1 = plt.subplots()
    ax2 = ax1.twinx()
    line1 = ax1.plot(np.arange(len(df_all)),df_all['count'], label='count', color ='royalblue')
    line2 = ax2.plot(np.arange(len(df_all)),df_all['close'], label='close', color='tomato', ls='--')
    ax1.set_xlabel('date')
    ax1.set_ylabel('count')
    ax2.set_ylabel('close')
    plt.legend()
    plt.show()