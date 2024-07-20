import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import mns_common.api.akshare.stock_bid_ask_api as stock_bid_ask_api
from mns_common.constant.price_enum import PriceEnum

'''

'''


def get_trade_price(symbol, price_code, limit_chg):
    stock_bid_ask_df = stock_bid_ask_api.stock_bid_ask_em(symbol)
    wei_bi = list(stock_bid_ask_df['wei_bi'])[0]
    now_price = list(stock_bid_ask_df['now_price'])[0]
    if wei_bi == PriceEnum.ZT_WEI_BI.price_name:
        trade_price = list(stock_bid_ask_df['buy_1'])[0]
    elif wei_bi == PriceEnum.DT_WEI_BI.price_name:
        trade_price = list(stock_bid_ask_df['sell_1'])[0]
    elif price_code == PriceEnum.BUY_1.price_code:
        trade_price = list(stock_bid_ask_df['buy_1'])[0]
    elif price_code == PriceEnum.BUY_2.price_code:
        trade_price = list(stock_bid_ask_df['buy_2'])[0]
    elif price_code == PriceEnum.BUY_3.price_code:
        trade_price = list(stock_bid_ask_df['buy_3'])[0]
    elif price_code == PriceEnum.BUY_4.price_code:
        trade_price = list(stock_bid_ask_df['buy_4'])[0]
    elif price_code == PriceEnum.BUY_5.price_code:
        trade_price = list(stock_bid_ask_df['buy_5'])[0]

    elif price_code == PriceEnum.SELL_1.price_code:
        trade_price = list(stock_bid_ask_df['sell_1'])[0]
    elif price_code == PriceEnum.SELL_2.price_code:
        trade_price = list(stock_bid_ask_df['sell_2'])[0]
    elif price_code == PriceEnum.SELL_3.price_code:
        trade_price = list(stock_bid_ask_df['sell_3'])[0]
    elif price_code == PriceEnum.SELL_4.price_code:
        trade_price = list(stock_bid_ask_df['sell_4'])[0]
    elif price_code == PriceEnum.SELL_5.price_code:
        trade_price = list(stock_bid_ask_df['sell_5'])[0]

    elif price_code == PriceEnum.BUY_PRICE_LIMIT.price_code:
        trade_price = round(now_price * (1 + limit_chg), 2)
    elif price_code == PriceEnum.SEll_PRICE_LIMIT.price_code:
        trade_price = round(now_price * (1 - limit_chg), 2)

    elif price_code == PriceEnum.ZT_PRICE.price_code:
        trade_price = list(stock_bid_ask_df['zt_price'])[0]

    elif price_code == PriceEnum.DT_PRICE.price_code:
        trade_price = list(stock_bid_ask_df['dt_price'])[0]
    else:
        trade_price = list(stock_bid_ask_df['now_price'])[0]

    trade_price = round(trade_price, 2)
    return trade_price


if __name__ == '__main__':
    price = get_trade_price('301314', PriceEnum.BUY_PRICE_LIMIT.price_code)
    print(price)
