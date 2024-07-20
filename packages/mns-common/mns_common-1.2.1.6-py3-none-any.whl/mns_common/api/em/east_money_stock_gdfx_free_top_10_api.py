import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 14
project_path = file_path[0:end]
sys.path.append(project_path)
import akshare as ak
import mns_common.component.common_service_fun_api as common_service_fun_api
import mns_common.utils.date_handle_util as date_handle_util
from loguru import logger
import mns_common.api.em.east_money_stock_api as east_money_stock_api
from mns_common.db.MongodbUtil import MongodbUtil

mongodb_util = MongodbUtil('27017')


def get_stock_gdfx_free_top_10_em_api(str_day, symbol):
    try:
        stock_gdfx_free_top_10_em_df = ak.stock_gdfx_free_top_10_em(symbol=symbol, date=str_day)
        stock_gdfx_free_top_10_em_df.rename(columns={
            "名次": "index",
            "股东名称": "shareholder_name",
            "股东性质": "shareholder_nature",
            "股份性质": "shares_nature",
            "股份类型": "shares_type",
            "持股数": "shares_number",
            "占总流通股本持股比例": "circulation_ratio",
            "增减": "change",
            "变动比率": "change_ratio"
        }, inplace=True)
    except BaseException as e:
        return None
    stock_gdfx_free_top_10_em_df = stock_gdfx_free_top_10_em_df.fillna(0)
    stock_gdfx_free_top_10_em_df.index = stock_gdfx_free_top_10_em_df.index.astype(str)
    return stock_gdfx_free_top_10_em_df


def get_stock_gdfx_free_top_10_em(str_day, symbol):
    symbol_init = symbol
    classification = common_service_fun_api.classify_symbol_one(symbol)
    if classification in ["S", "C"]:
        symbol = 'sz' + symbol
    elif classification in ["K", "H"]:
        symbol = 'sh' + symbol
    else:
        return

    str_day_no_slash = date_handle_util.no_slash_date(str_day)
    date_day = date_handle_util.str_to_date(str_day_no_slash, '%Y%m%d')
    month = date_day.month
    year = date_day.year
    one = '0331'
    two = '0630'
    three = '0930'
    four = '1231'

    if 0 < month <= 4:
        period_04 = str(year - 1) + four
        stock_gdfx_free_top_10_04 = get_stock_gdfx_free_top_10_em_api(period_04, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_04, period_04, symbol_init, str_day)

        if stock_gdfx_free_top_10_04 is None or stock_gdfx_free_top_10_04.shape[0] == 0:
            period_03 = str(year - 1) + three
            stock_gdfx_free_top_10_03 = get_stock_gdfx_free_top_10_em_api(period_03, symbol)
            sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_03, period_03, symbol_init, str_day)

        period_01 = str(year) + one
        stock_gdfx_free_top_10_01 = get_stock_gdfx_free_top_10_em_api(period_01, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_01, period_01, symbol_init, str_day)
    elif 4 < month <= 6:
        period_01 = str(year) + one
        stock_gdfx_free_top_10_01 = get_stock_gdfx_free_top_10_em_api(period_01, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_01, period_01, symbol_init, str_day)
        period_02 = str(year) + two
        stock_gdfx_free_top_10_02 = get_stock_gdfx_free_top_10_em_api(period_02, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_02, period_02, symbol_init, str_day)
    elif 6 < month <= 10:
        period_02 = str(year) + two
        stock_gdfx_free_top_10_02 = get_stock_gdfx_free_top_10_em_api(period_02, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_02, period_02, symbol_init, str_day)
        period_03 = str(year) + three
        stock_gdfx_free_top_10_03 = get_stock_gdfx_free_top_10_em_api(period_03, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_03, period_03, symbol_init, str_day)
    elif 10 < month <= 12:
        period_03 = str(year) + three
        stock_gdfx_free_top_10_03 = get_stock_gdfx_free_top_10_em_api(period_03, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_03, period_03, symbol_init, str_day)
        period_04 = str(year) + four
        stock_gdfx_free_top_10_04 = get_stock_gdfx_free_top_10_em_api(period_04, symbol)
        sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_04, period_04, symbol_init, str_day)


def sync_stock_gdfx_free_top_10(stock_gdfx_free_top_10_em_df, period, symbol, str_day):
    if stock_gdfx_free_top_10_em_df is not None and stock_gdfx_free_top_10_em_df.shape[0] > 0:
        stock_gdfx_free_top_10_em_df['str_day'] = str_day
        stock_gdfx_free_top_10_em_df['symbol'] = symbol
        stock_gdfx_free_top_10_em_df['_id'] = symbol + '_' + stock_gdfx_free_top_10_em_df.index + '_' + period
        stock_gdfx_free_top_10_em_df['period'] = period
        mongodb_util.save_mongo(stock_gdfx_free_top_10_em_df, 'stock_gdfx_free_top_10')


def sync_stock_gdfx_free_top_10_one_day(str_day):
    real_time_quotes = east_money_stock_api.get_real_time_quotes_all_stocks()
    for real_time_one in real_time_quotes.itertuples():
        try:
            get_stock_gdfx_free_top_10_em(str_day, real_time_one.symbol)
        except BaseException as e:
            logger.error('同步所有股票前十大流通股本异常:{},{}', real_time_one.symbol, e)


from datetime import datetime

if __name__ == '__main__':
    now_date = datetime.now()
    str_day = now_date.strftime('%Y-%m-%d')
    logger.info('同步所有股票前十大流通股本')
    sync_stock_gdfx_free_top_10_one_day(str_day)
