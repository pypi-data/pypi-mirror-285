import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 7
project_path = file_path[0:end]
sys.path.append(project_path)
import pandas as pd
from functools import lru_cache
import requests

fields_all = "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100,f101,f102,f103,f104,f105,f106,f107,f108" \
             ",f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200" \
             ",f209,f210,f212,f213,f214,f215,f216,f217,f218,f219,f220,f221,f222,f223,f224,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f283,f284,f285,f286,f287,f288,f289,f290,f291,f292,f293,f294,f295,f296,f297,f298,f299,f300" \
             ",f309,f310,f312,f313,f314,f315,f316,f317,f318,f319,f320,f321,f322,f323,f324,f325,f326,f327,f328,f329,f330,f331,f332,f333,f334,f335,f336,f337,f338,f339,f340,f341,f342,f343,f344,f345,f346,f347,f348,f349,f350,f351,f352,f353,f354,f355,f356,f357,f358,f359,f360,f361,f362,f363,f364,f365,f366,f367,f368,f369,f370,f371,f372,f373,f374,f375,f376,f377,f378,f379,f380,f381,f382,f383,f384,f385,f386,f387,f388,f389,f390,f391,f392,f393,f394,f395,f396,f397,f398,f399,f401"


# 行情报价接口

@lru_cache()
def __code_id_map_em() -> dict:
    """
    东方财富-股票和市场代码
    https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 股票和市场代码
    :rtype: dict
    """
    url = "http://80.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:1 t:2,m:1 t:23",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df["market_id"] = 1
    temp_df.columns = ["sh_code", "sh_id"]
    code_id_dict = dict(zip(temp_df["sh_code"], temp_df["sh_id"]))
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:6,m:0 t:80",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
    temp_df_sz["sz_id"] = 0
    code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["sz_id"])))
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:81 s:2048",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
    temp_df_sz["bj_id"] = 0
    code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["bj_id"])))
    return code_id_dict


def stock_bid_ask_em(symbol: str = "000001") -> dict:
    """
    东方财富-行情报价
    https://quote.eastmoney.com/sz000001.html
    :param symbol: 股票代码
    :type symbol: str
    :return: 行情报价
    :rtype: pandas.DataFrame
    """
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    code_id_map_em_dict = __code_id_map_em()
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f43,f51,f52,f191,f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295",
        # "fields" :fields_02,
        "secid": f"{code_id_map_em_dict[symbol]}.{symbol}",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    tick_dict = {
        "now_price": data_json["data"]["f43"],
        "dt_price": data_json["data"]["f52"],
        "zt_price": data_json["data"]["f51"],
        "wei_bi": data_json["data"]["f191"],
        "sell_5": data_json["data"]["f31"],
        "sell_5_vol": data_json["data"]["f32"] * 100,
        "sell_4": data_json["data"]["f33"],
        "sell_4_vol": data_json["data"]["f34"] * 100,
        "sell_3": data_json["data"]["f35"],
        "sell_3_vol": data_json["data"]["f36"] * 100,
        "sell_2": data_json["data"]["f37"],
        "sell_2_vol": data_json["data"]["f38"] * 100,
        "sell_1": data_json["data"]["f39"],
        "sell_1_vol": data_json["data"]["f40"] * 100,
        "buy_1": data_json["data"]["f19"],
        "buy_1_vol": data_json["data"]["f20"] * 100,
        "buy_2": data_json["data"]["f17"],
        "buy_2_vol": data_json["data"]["f18"] * 100,
        "buy_3": data_json["data"]["f15"],
        "buy_3_vol": data_json["data"]["f16"] * 100,
        "buy_4": data_json["data"]["f13"],
        "buy_4_vol": data_json["data"]["f14"] * 100,
        "buy_5": data_json["data"]["f11"],
        "buy_5_vol": data_json["data"]["f12"] * 100,
    }
    temp_df = pd.DataFrame(tick_dict, index=[1])
    temp_df.reset_index(inplace=True)
    temp_df.loc[temp_df['wei_bi'] == '-', 'wei_bi'] = 0
    temp_df.loc[temp_df['sell_5'] == '-', 'sell_5_vol'] = 0
    temp_df.loc[temp_df['sell_5'] == '-', 'sell_5'] = 0
    temp_df.loc[temp_df['sell_4'] == '-', 'sell_4_vol'] = 0
    temp_df.loc[temp_df['sell_4'] == '-', 'sell_4'] = 0
    temp_df.loc[temp_df['sell_3'] == '-', 'sell_3_vol'] = 0
    temp_df.loc[temp_df['sell_3'] == '-', 'sell_3'] = 0
    temp_df.loc[temp_df['sell_2'] == '-', 'sell_2_vol'] = 0
    temp_df.loc[temp_df['sell_2'] == '-', 'sell_2'] = 0
    temp_df.loc[temp_df['sell_1'] == '-', 'sell_1_vol'] = 0
    temp_df.loc[temp_df['sell_1'] == '-', 'sell_1'] = 0
    temp_df.loc[temp_df['buy_1'] == '-', 'buy_1_vol'] = 0
    temp_df.loc[temp_df['buy_1'] == '-', 'buy_1'] = 0
    temp_df.loc[temp_df['buy_2'] == '-', 'buy_2_vol'] = 0
    temp_df.loc[temp_df['buy_2'] == '-', 'buy_2'] = 0
    temp_df.loc[temp_df['buy_3'] == '-', 'buy_3_vol'] = 0
    temp_df.loc[temp_df['buy_3'] == '-', 'buy_3'] = 0
    temp_df.loc[temp_df['buy_4'] == '-', 'buy_4_vol'] = 0
    temp_df.loc[temp_df['buy_4'] == '-', 'buy_4'] = 0
    temp_df.loc[temp_df['buy_5'] == '-', 'buy_5_vol'] = 0
    temp_df.loc[temp_df['buy_5'] == '-', 'buy_5'] = 0
    temp_df['symbol'] = symbol
    return temp_df


if __name__ == '__main__':
    while True:
        df = stock_bid_ask_em('301082')
        print(df)
