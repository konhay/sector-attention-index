"""
 * RoyalFlush Sector Service
 *
 * @since 2023.9
 * @version 1st
 * @author Bing.Han
 *
"""
import sys
import numpy as np
import pandas as pd
import socket
import urllib
import gzip
import re
import time
import requests
import datetime
from urllib.request import urlopen, build_opener, install_opener
from selenium import webdriver
from bs4 import BeautifulSoup
from io import BytesIO
from common.mysql_service import MySQLUtil


def write_bk(bk_type, write=False) :
    """
    Get and write the latest industry or concept sector list from the RoyalFlush Market Center
    :param bk_type: sector type, "thshy"(industry) or "gn"(concept)
    :param write: insert into database or not
    :return:
    """
    bk_dict = {"thshy":"行业板块", "gn":"概念板块"}
    if bk_type not in bk_dict.keys():
        print("WRONG bk_type: '%s' %s" % (bk_type, list(bk_dict.keys())))
        sys.exit()

    # 403 Forbidden
    opener = build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    install_opener(opener)
    socket.setdefaulttimeout(100)

    # get content
    if bk_type =='thshy':
        url = "http://q.10jqka.com.cn/thshy/"
        html = urlopen(url)
        bsObj = BeautifulSoup(html, 'html.parser')
        content = bsObj.find("div", {"class": "cate_inner visible"}).findAll("a")
        html.close()
    else :
        url = "http://q.10jqka.com.cn/gn/"
        html = urlopen(url)
        bsObj = BeautifulSoup(html, 'html.parser')
        content = bsObj.find("div", {"class": "cate_inner"}).findAll("a")
        html.close()

    # make bk dafaframe
    bk_list = []
    for i in content:
        code = i.attrs['href'][-7:-1]
        name = i.get_text()
        bk_list.append({"bk_source": "同花顺"
                           , "bk_type": bk_dict[bk_type]
                           , "bk_code": code
                           , "bk_name": name
                           , "use_flag": 0
                           , "data_date": datetime.date.today().strftime("%Y%m%d")
                        })
        df = pd.DataFrame(bk_list)

    # write to mysql
    if write:
        try:
            MySQLUtil.df_write(df, 'bk_info')
            print("write bk info successfully.")
        except Exception as e:
            print(e)
    else:
        print("get bk info successfully.")
        return df


def get_cookie():
    """
    Get dynamic cookies
    :return:
    """
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')
    driver = webdriver.Chrome(chrome_options=options)
    url = "http://q.10jqka.com.cn/thshy/"
    driver.get(url)
    cookie = driver.get_cookies()
    driver.close()
    return cookie[0]['value']


def write_bk_hist(bk_code, year, cookie) :
    """
    Get and write a single RoyalFlush sector history data by year
    :param bk_code: sector code
    :param year:
    :param cookie:
    :return:
    """
    url = 'http://d.10jqka.com.cn/v4/line/bk_{}/01/{}.js'.format(bk_code, str(year))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Referer': 'http://q.10jqka.com.cn/thshy/detail',
        'Cookie': 'v={}'.format(cookie)
        }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Response [{}] {}".format(response.status_code, url))
            return
        bsObj = BeautifulSoup(response.content, 'html.parser')
        pattern = re.compile('{"data":"(.*?)"}', re.S)
        content = re.findall(pattern, str(bsObj))[0].split(';')
        arr = []
        for row in content:
            arr.append((bk_code + ',' + row).split(',')[:8])
        df = pd.DataFrame(arr, columns=['bk_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount', ])
        MySQLUtil.df_write(df, 'bk_daily')
        print("write hist successfully: {}/{}(bk_code/year)".format(bk_code, year))
    except Exception as e:
        print(e)


def write_bk_hist_all(year):
    """
    Get and write all RoyalFlush sector history data by year
    :param year:
    :return:
    """
    sql = """select distinct bk_code from bk_info where bk_source ='同花顺' and bk_type = '行业板块' order by bk_code;"""
    df = MySQLUtil.df_read(sql)
    cookie = get_cookie()
    for bk_code in df["bk_code"]:
        write_bk_hist(bk_code, year, cookie)
    # -- verify
    # select current_timestamp(); -- 2023-09-01 15:51:43
    # select bk_code, count(0) from bk_daily bd where trade_date like '2017%' group by bk_code ;  -- 76 244
    # select bk_code, count(0) from bk_daily bd where trade_date like '2018%' group by bk_code ;  -- 76 243
    # select bk_code, count(0) from bk_daily bd where trade_date like '2019%' group by bk_code ;  -- 76 244
    # select bk_code, count(0) from bk_daily bd where trade_date like '2020%' group by bk_code ;  -- 76 243
    # select bk_code, count(0) from bk_daily bd where trade_date like '2021%' group by bk_code ;  -- 76 243
    # select bk_code, count(0) from bk_daily bd where trade_date like '2022%' group by bk_code ;  -- 76 242
    # select bk_code, count(0) from bk_daily bd where trade_date like '2023%' group by bk_code ;  -- 76 163


def append_bk_hist_all():
    """
    Append data method, nightly updating recommended.
    :return:
    """
    year = datetime.date.today().year
    write_bk_hist_all(year)


def get_bk_stock_(bk_code):
    """
    Real-time access to the components of the RoyalFlush sector, such as the sector code 881172
    example url: http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/1/ajax/1/code/881172
    :param bk_code: sector code
    :return:
    """
    # How to get cookie? Unresolved. Currently obtained through F12
    cookie = 'u_ukey=A10702B86896***'

    page = 1
    stock_list = []
    while(True):
        url = 'http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/%s/ajax/1/code/%s'%(str(page),str(code))
        # To solve the garbled code problem, refer to https://blog.csdn.net/weixin_43116971/article/details/121291281
        request = urllib.request.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        request.add_header('user-agent', "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36") #防止403
        request.add_header('cookie', cookie) #防止401
        response = urlopen(request)
        html = response.read()
        encoding = response.info().get('Content-Encoding') #gzip
        def gzip1(data):
            buf = BytesIO(data)
            f = gzip.GzipFile(fileobj=buf)
            return f.read()
        if encoding == 'gzip':
            html = gzip1(html)
        else:
            print("")
            return
        bsObj = BeautifulSoup(html, 'html.parser')
        content = bsObj.findAll("a",{"target":"_blank"})
        if len(content)==0:
            break
        for i in np.arange(int(len(content) / 2)) * 2:
            code = content[i].getText()
            name = content[i+1].getText()
            stock_list.append({"code": code, "name": name})
        page=page+1
    df = pd.DataFrame(stock_list)
    return df


def get_bk_stock(bk_code):
    """
    Real-time access to the components of the RoyalFlush sector, such as the sector code 881172
    example url: http://q.10jqka.com.cn/thshy/detail/code/881172/
    :param bk_code: sector code
    :return:
    """
    url = 'http://q.10jqka.com.cn/thshy/detail/code/{}/'.format(bk_code)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"') #防止403 Nginx forbidden.
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    time.sleep(2)
    stock_list = []
    while (True):
        html = driver.execute_script('return document.documentElement.outerHTML')
        bsObj = BeautifulSoup(html, 'html.parser')
        content = bsObj.find("div", {"class": "body m-pager-box"}).find('tbody').findAll("a")
        for i in np.arange(0, len(content), 3):
            code = content[i].get_text()
            name = content[i + 1].get_text()
            stock_list.append([code, name])
        try:
            #--- Dynamic list
            # Find next table page element
            next_page = driver.find_element_by_link_text("下一页")
            # Sleep is essential, otherwise a mistake will occur
            time.sleep(2)
            # If at last table page
            if next_page.get_attribute("class") == "nolink":
                break
            # Take your driver into next table page by click
            next_page.click()
            # Sleep is essential, otherwise a mistake will occur
            time.sleep(2)
        except Exception as e:
            # If table just has only one page
            print(e)
            break
    driver.quit()
    df = pd.DataFrame(stock_list, columns=['code', 'name'])
    return df

