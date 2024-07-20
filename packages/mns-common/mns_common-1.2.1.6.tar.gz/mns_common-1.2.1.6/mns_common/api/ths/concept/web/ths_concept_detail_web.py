import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 14
project_path = file_path[0:end]
sys.path.append(project_path)

from loguru import logger
import time
import requests

import mns_common.utils.data_frame_util as data_frame_util
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
from akshare.utils.tqdm import get_tqdm

'''
获取单只股票代码 symbol 所有概念详情
'''
# 获取单个股票新增概念
# https://basic.10jqka.com.cn/basicph/briefinfo.html#/concept?broker=anelicaiapp&showtab=1&code=301016&code_name=%E9%9B%B7%E5%B0%94%E4%BC%9F&market_id=33
'''

'''


def get_one_symbol_all_ths_concepts(symbol: str = "305794") -> pd.DataFrame:
    try:
        url = f"http://basic.10jqka.com.cn/api/stockph/conceptdetail/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iOS AYLCAPP/9.1.2.0/h4526a24eb9445522492fd64caae11b1f scheme/anelicaiapp deviceinfo/I|9.1.2.0|NA|h4526a24eb9445522492fd64caae11b1f pastheme/0",
            "Cookie": "ps_login_app_name=AYLCAPP;"
                      "ps_login_token_id=N_C993F777ACC500B354C762A2627A8862348FC8163799A08EBEB2301C28A2135D220475787D0E81425C1134E15D8CC8761D639FEDBD46C00FE8EA6482C1E42D9801B19918FB3F5C34;"
                      "ps_login_union_id=edc29089a2b64e3882062297030a0386;PAS.CURRENTUNIONID=edc29089a2b64e3882062297030a0386"
        }
        r = requests.get(url, headers=headers)
        data_json = r.json()
        data_concept = data_json['data']
        errorcode = data_json['errorcode']
        errormsg = data_json['errormsg']
        if errorcode == '0' and errormsg == '':
            data_concept_df = pd.DataFrame(data_concept)
            return data_concept_df
        else:
            return None
    except BaseException as e:
        logger.error("获取symbol概念信息异常:{},{}", symbol, e)


# web端口 获取概念详情 极容易被封 最好不使用了
def stock_board_cons_ths(symbol: str = "301558") -> pd.DataFrame:
    """
    通过输入行业板块或者概念板块的代码获取成份股
    https://q.10jqka.com.cn/thshy/detail/code/881121/
    https://q.10jqka.com.cn/gn/detail/code/301558/
    :param symbol: 行业板块或者概念板块的代码
    :type symbol: str
    :return: 行业板块或者概念板块的成份股
    :rtype: pandas.DataFrame
    """
    headers = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": ("searchGuide=sg; Hm_lvt_722143063e4892925903024537075d0d=1717667296,1718442548; "
                   "Hm_lpvt_722143063e4892925903024537075d0d=1718442548; "
                   "Hm_lvt_929f8b362150b1f77b477230541dbbc2=1717667296,1718442548; "
                   "Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1718442548; "
                   "Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1717667297,1718105758,1718442548; "
                   "u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; "
                   "u_dpass=FiQNmw4Vyp2vyGzE6%2FEbtrgPtUViMbFi%2BSUJ1bTSIaqQP7Dl6EmBT0Xu4HBksFjJHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; "
                   "u_did=0112000691F9476ABA607A0E4F06AF9B; u_ttype=WEB; "
                   "user=MDq%2BsNDQcE06Ok5vbmU6NTAwOjYxMzk4NTQ0ODo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNzo6OjYwMzk4NTQ0ODoxNzE4NDQyNTkzOjo6MTYzNDU2Njk4MDo4NjQwMDowOjE5NjMyMzc1ZWNjOGUzNTJmYTczMmFhZjM4OTg3ZGMzNDpkZWZhdWx0XzQ6MQ%3D%3D; "
                   "userid=602085498; u_name=%BE%B0%D0%D0pM; "
                   "escapename=%25u666f%25u884cpM; "
                   "ticket=092428c703980b80d5d407acddb6b474; user_status=0; "
                   "utk=628aa7def3a67c0b3c66869803ab9e23; "
                   "historystock=688272%7C*%7C301041%7C*%7C002156; "
                   "spversion=20130314; "
                   "Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1718504236; "
                   "v=A6WXXy9vL7nJNkuWRIoO2C1psmra4ll0o5Y9yKeKYVzrvsuUbzJpRDPmT4I0"),
        "Host": "q.10jqka.com.cn",
        "Referer": "https://q.10jqka.com.cn/thshy",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\""
    }
    url = f"https://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/1/ajax/1/code/{symbol}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "lxml")
    url_flag = "thshy"
    if soup.find(name="td", attrs={"colspan": "14"}):
        url = f"https://q.10jqka.com.cn/gn/detail/field/199112/order/desc/page/1/ajax/1/code/{symbol}"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, features="lxml")
        url_flag = "gn"
    try:
        page_num = int(
            soup.find_all(name="a", attrs={"class": "changePage"})[-1]["page"]
        )
    except IndexError:
        page_num = 1
    big_df = pd.DataFrame()
    tqdm = get_tqdm()
    for page in tqdm(range(1, page_num + 1), leave=False):
        try:
            time.sleep(2)
            url = f"https://q.10jqka.com.cn/{url_flag}/detail/field/199112/order/desc/page/{page}/ajax/1/code/{symbol}"
            r_detail = requests.get(url, headers=headers)
            if r_detail.status_code == 200:
                temp_df = pd.read_html(StringIO(r.text))[0]
                big_df = pd.concat(objs=[big_df, temp_df], ignore_index=True)
        except BaseException as e:
            logger.error("获取概念详细信息异常:{},{}", symbol, e)
    big_df.rename(
        {
            "涨跌幅(%)": "涨跌幅",
            "涨速(%)": "涨速",
            "换手(%)": "换手",
            "振幅(%)": "振幅",
        },
        inplace=True,
        axis=1,
    )
    if '加自选' in big_df.columns:
        del big_df["加自选"]
    if '代码' not in big_df.columns:
        return None
    big_df["代码"] = big_df["代码"].astype(str).str.zfill(6)
    if data_frame_util.is_not_empty(big_df):
        big_df.rename(columns={"序号": "index",
                               "代码": "symbol",
                               "名称": "name",
                               "现价": "now_price",
                               "涨跌幅": "chg",
                               "涨跌": "change",
                               "涨速": "r_increase",
                               "换手": "exchange",
                               "量比": "q_ratio",
                               "振幅": "pct_chg",
                               "成交额": "amount",
                               "流通股": "tradable_shares",
                               "流通市值": "flow_mv",
                               "市盈率": "pe"
                               }, inplace=True)
        stock_board_cons_ths_df = big_df[
            big_df["index"] != '暂无成份股数据']

        if stock_board_cons_ths_df is None or stock_board_cons_ths_df.shape[0] == 0:
            return
        length = len(list(stock_board_cons_ths_df))
        stock_board_cons_ths_df.insert(length, 'concept_code', symbol)

        stock_board_cons_ths_df['amount'] = stock_board_cons_ths_df['amount'].apply(
            lambda x: pd.to_numeric(x.replace('亿', ''), errors="coerce"))

        stock_board_cons_ths_df['tradable_shares'] = stock_board_cons_ths_df['tradable_shares'].apply(
            lambda x: pd.to_numeric(x.replace('亿', ''), errors="coerce"))

        stock_board_cons_ths_df['flow_mv'] = stock_board_cons_ths_df['flow_mv'].apply(
            lambda x: pd.to_numeric(x.replace('亿', ''), errors="coerce"))
    return stock_board_cons_ths_df


if __name__ == '__main__':
    concept_df = stock_board_cons_ths('886076')

    print(concept_df)
