import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 14
project_path = file_path[0:end]
sys.path.append(project_path)
from datetime import datetime
import pandas as pd
import requests
import json
import execjs
from loguru import logger

'''
操作ths 自选股票
'''


def get_js_code():
    '''
    获取js
    :return:
    '''
    '''
       获取js
       :return:
       '''
    with open('ths.js') as f:
        comm = f.read()
    com_result = execjs.compile(comm)
    result = com_result.call('v')
    return result


def get_headers(cookie):
    '''
    获取请求头
    :param cookie:
    :return:
    '''
    v = get_js_code()
    cookie_js = cookie.split('v=')
    cookie_js = cookie_js[0] + 'v=' + v
    headers = {
        'Cookie': cookie_js,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    }
    return headers


# 获取所有自选股票
def get_all_self_choose_stock_list(cookie):
    '''
    获取全部自选股
    :param cookie:
    :return:
    '''

    headers = get_headers(cookie)
    url = 'https://t.10jqka.com.cn/newcircle/group/getSelfStockWithMarket/?'
    now_date = datetime.now()
    now_time = int(now_date.timestamp() * 1000)
    now_time = str(now_time)
    params = {
        'callback': 'selfStock',
        '_': now_time
    }
    res = requests.get(url=url, params=params, headers=headers)
    text = res.text[10:len(res.text) - 2]
    json_text = json.loads(text)
    df = pd.DataFrame(json_text['result'])
    return df


# 添加自选股
def add_stock_to_account(stock, cookie):
    '''
    添加股票到自选股
    :param stock:
    :param cookie:
    :return:
    '''
    now_date = datetime.now()
    now_time = int(now_date.timestamp() * 1000)
    now_time = str(now_time)
    url = 'https://t.10jqka.com.cn/newcircle/group/modifySelfStock/?'
    headers = get_headers(cookie)
    params = {
        'callback': 'modifyStock',
        'op': 'add',
        'stockcode': stock,
        '_': now_time,
    }
    res = requests.get(url=url, params=params, headers=headers)
    text = res.text[12:len(res.text) - 2]
    json_text = json.loads(text)
    err = json_text['errorMsg']
    if err == '修改成功':
        logger.info('{}加入自选股成功', stock)
    else:
        logger.error('{}加入自选股失败,{}', stock, err)


# 删除自选股
def del_stock_from_account(stock, cookie):
    '''
    删除股票从自选股
     :param stock:
    :param cookie:
    :return:
    '''
    url = 'https://t.10jqka.com.cn/newcircle/group/modifySelfStock/?'
    headers = get_headers(cookie)
    try:
        params = {
            'op': 'del',
            'stockcode': stock
        }
        res = requests.get(url=url, params=params, headers=headers)
        text = res.text
        json_text = json.loads(text)
        err = json_text['errorMsg']
        if err == '修改成功':
            logger.info('{}删除自选股成功', stock)
        else:
            logger.error('{}删除自选股失败,{}', stock, err)
    except BaseException as e:
        logger.error('{}删除自选股异常,{}', stock, e)


if __name__ == '__main__':
    cookie_test = ('searchGuide=sg; u_ukey=A10702B8689642C6BE607730E11E6E4A; '
                   'u_uver=1.0.0; '
                   'u_dpass=FiQNmw4Vyp2vyGzE6%2FEbtrgPtUViMbFi%2BSUJ1bTSIaqQP7Dl6EmBT0Xu4HBksFjJHi80LrSsTFH9a%2B6rtRvqGg%3D%3D;'
                   ' u_did=0112000691F9476ABA607A0E4F06AF9B;'
                   ' u_ttype=WEB; spversion=20130314; '
                   'historystock=301298%7C*%7C688272%7C*%7C301041%7C*%7C002156; '
                   'log=; Hm_lvt_722143063e4892925903024537075d0d=1717667296,1718442548,1718875131;'
                   ' Hm_lvt_929f8b362150b1f77b477230541dbbc2=1717667296,1718442548,1718875131; '
                   'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1718105758,1718442548,1718694509,1718875131;'
                   ' ttype=WEB; '
                   'user=MDq%2BsNDQcE06Ok5vbmU6NTAwOjYxMzk4NTQ0ODo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNzo6OjYwMzk4NTQ0ODoxNzE4ODc1MTcwOjo6MTYzNDU2Njk4MDo2MDQ4MDA6MDoxNGE3NzkzNzk2NmZlZDExMmYwNzY1ZjdkNGYzMzI0YWU6ZGVmYXVsdF80OjE%3D; '
                   'userid=603985448; '
                   'u_name=%BE%B0%D0%D0pM; '
                   'escapename=%25u666f%25u884cpM;'
                   ' ticket=9ff8d8cb9b5ad2fe045f50f0ecee8886; '
                   'user_status=0; utk=90e628af72988f5b8e3a54df3de68d70; '
                   'Hm_lpvt_722143063e4892925903024537075d0d=1718875171; '
                   'Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1718875172; '
                   'Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1718875175; '
                   'Hm_lvt_da7579fd91e2c6fa5aeb9d1620a9b333=1718504236,1718875175;'
                   ' Hm_lpvt_da7579fd91e2c6fa5aeb9d1620a9b333=1718875175;'
                   ' v=Ax4savCy9DpUAiBeDC5lBfpcab9l3-NgdKCWVMimjoBciLBhMG8yaUQz5kGb')

    # 设置自己的请求头在get_header配置
    # 获取全部自选股
    df1 = get_headers(cookie_test)
    print(df1)
    # 添加股票
    add_stock_to_account(stock='886016', cookie=cookie_test)
    add_stock_to_account(stock='600031', cookie=cookie_test)
    add_stock_to_account(stock='000001', cookie=cookie_test)
    # 删除股票
    del_stock_from_account(stock='886016', cookie=cookie_test)
    del_stock_from_account(stock='600031', cookie=cookie_test)
    del_stock_from_account(stock='000001', cookie=cookie_test)

    # 获取全部的自选股
    df2 = get_all_self_choose_stock_list(cookie_test)
    print(df2)
