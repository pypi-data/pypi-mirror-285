import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import pandas as pd
import requests
import json

fields = ("f352,f2,f3,f5,f6,f8,f10,f11,f22,f12,f14,f15,f16,f17,f18,f20,f21,f26,"
          "f33,f34,f35,f62,f66,f69,f72,f100,f184,f211,f212")


def hk_real_time_quotes(cookie):
    headers = {
        'Cookie': cookie
    }

    url_new = ('https://61.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409497467688484127_1715915661673'
               '&pn=1'
               '&pz=50000'
               '&po=1'
               '&np=1'
               '&ut=bd1d9ddb04089700cf9c27f6f7426281'
               '&fltt=2'
               '&invt=2'
               '&wbp2u=4253366368931142|0|1|0|web'
               '&fid=f3'
               '&fs=m:116+t:3,m:116+t:4,m:116+t:1,m:116+t:2'
               '&fields=' + fields +
               '&_=1715915661690')

    r = requests.get(url_new, headers=headers)
    result = r.content.decode("utf-8")

    startIndex = result.index('"diff"')
    endIndex = result.index('}]}')

    result = result[startIndex + 7:endIndex + 2]

    data_json = json.loads(result)

    temp_df = pd.DataFrame(data_json)

    temp_df = temp_df.rename(columns={

        "f12": "symbol",
        "f14": "name",
        "f3": "chg",
        "f2": "now_price",
        "f5": "volume",
        "f6": "amount",
        "f8": "exchange",
        "f10": "quantity_ratio",
        "f22": "up_speed",
        "f11": "up_speed_05",

        "f15": "high",
        "f16": "low",
        "f17": "open",
        "f18": "yesterday_price",
        "f20": "total_mv",
        "f21": "flow_mv",
        "f26": "list_date",
        "f33": "wei_bi",
        "f34": "outer_disk",
        "f35": "inner_disk",
        "f62": "today_main_net_inflow",
        "f66": "super_large_order_net_inflow",
        "f69": "super_large_order_net_inflow_ratio",
        "f72": "large_order_net_inflow",
        # "f78": "medium_order_net_inflow",
        # "f84": "small_order_net_inflow",
        "f100": "industry",
        # "f103": "concept",
        "f184": "today_main_net_inflow_ratio",
        "f352": "average_price",
        "f211": "buy_1_num",
        "f212": "sell_1_num"
    })
    temp_df.loc[temp_df['buy_1_num'] == '-', 'buy_1_num'] = 0
    temp_df.loc[temp_df['sell_1_num'] == '-', 'sell_1_num'] = 0
    temp_df.loc[temp_df['up_speed_05'] == '-', 'up_speed_05'] = 0
    temp_df.loc[temp_df['up_speed'] == '-', 'up_speed'] = 0
    temp_df.loc[temp_df['average_price'] == '-', 'average_price'] = 0
    temp_df.loc[temp_df['wei_bi'] == '-', 'wei_bi'] = 0
    temp_df.loc[temp_df['yesterday_price'] == '-', 'yesterday_price'] = 0
    temp_df.loc[temp_df['now_price'] == '-', 'now_price'] = 0
    temp_df.loc[temp_df['chg'] == '-', 'chg'] = 0
    temp_df.loc[temp_df['volume'] == '-', 'volume'] = 0
    temp_df.loc[temp_df['amount'] == '-', 'amount'] = 0
    temp_df.loc[temp_df['exchange'] == '-', 'exchange'] = 0
    temp_df.loc[temp_df['quantity_ratio'] == '-', 'quantity_ratio'] = 0
    temp_df.loc[temp_df['high'] == '-', 'high'] = 0
    temp_df.loc[temp_df['low'] == '-', 'low'] = 0
    temp_df.loc[temp_df['open'] == '-', 'open'] = 0
    temp_df.loc[temp_df['total_mv'] == '-', 'total_mv'] = 0
    temp_df.loc[temp_df['flow_mv'] == '-', 'flow_mv'] = 0
    temp_df.loc[temp_df['inner_disk'] == '-', 'inner_disk'] = 0
    temp_df.loc[temp_df['outer_disk'] == '-', 'outer_disk'] = 0
    temp_df.loc[temp_df['today_main_net_inflow_ratio'] == '-', 'today_main_net_inflow_ratio'] = 0
    temp_df.loc[temp_df['today_main_net_inflow'] == '-', 'today_main_net_inflow'] = 0
    temp_df.loc[temp_df['super_large_order_net_inflow'] == '-', 'super_large_order_net_inflow'] = 0
    temp_df.loc[temp_df['super_large_order_net_inflow_ratio'] == '-', 'super_large_order_net_inflow_ratio'] = 0
    temp_df.loc[temp_df['large_order_net_inflow'] == '-', 'large_order_net_inflow'] = 0
    # temp_df.loc[temp_df['medium_order_net_inflow'] == '-', 'medium_order_net_inflow'] = 0
    # temp_df.loc[temp_df['small_order_net_inflow'] == '-', 'small_order_net_inflow'] = 0

    temp_df["list_date"] = pd.to_numeric(temp_df["list_date"], errors="coerce")
    temp_df["wei_bi"] = pd.to_numeric(temp_df["wei_bi"], errors="coerce")
    temp_df["average_price"] = pd.to_numeric(temp_df["average_price"], errors="coerce")
    temp_df["yesterday_price"] = pd.to_numeric(temp_df["yesterday_price"], errors="coerce")
    temp_df["now_price"] = pd.to_numeric(temp_df["now_price"], errors="coerce")
    temp_df["chg"] = pd.to_numeric(temp_df["chg"], errors="coerce")
    temp_df["volume"] = pd.to_numeric(temp_df["volume"], errors="coerce")
    temp_df["amount"] = pd.to_numeric(temp_df["amount"], errors="coerce")
    temp_df["exchange"] = pd.to_numeric(temp_df["exchange"], errors="coerce")
    temp_df["quantity_ratio"] = pd.to_numeric(temp_df["quantity_ratio"], errors="coerce")
    temp_df["high"] = pd.to_numeric(temp_df["high"], errors="coerce")
    temp_df["low"] = pd.to_numeric(temp_df["low"], errors="coerce")
    temp_df["open"] = pd.to_numeric(temp_df["open"], errors="coerce")
    temp_df["total_mv"] = pd.to_numeric(temp_df["total_mv"], errors="coerce")
    temp_df["flow_mv"] = pd.to_numeric(temp_df["flow_mv"], errors="coerce")
    temp_df["outer_disk"] = pd.to_numeric(temp_df["outer_disk"], errors="coerce")
    temp_df["inner_disk"] = pd.to_numeric(temp_df["inner_disk"], errors="coerce")
    temp_df["today_main_net_inflow"] = pd.to_numeric(temp_df["today_main_net_inflow"], errors="coerce")
    temp_df["super_large_order_net_inflow"] = pd.to_numeric(temp_df["super_large_order_net_inflow"],
                                                            errors="coerce")
    temp_df["super_large_order_net_inflow_ratio"] = pd.to_numeric(temp_df["super_large_order_net_inflow_ratio"],
                                                                  errors="coerce")
    temp_df["large_order_net_inflow"] = pd.to_numeric(temp_df["large_order_net_inflow"],
                                                      errors="coerce")
    # temp_df["medium_order_net_inflow"] = pd.to_numeric(temp_df["medium_order_net_inflow"],
    #                                                    errors="coerce")
    # temp_df["small_order_net_inflow"] = pd.to_numeric(temp_df["small_order_net_inflow"], errors="coerce")

    # 大单比例
    temp_df['large_order_net_inflow_ratio'] = round((temp_df['large_order_net_inflow'] / temp_df['amount']) * 100, 2)

    # 外盘是内盘倍数
    temp_df['disk_ratio'] = round((temp_df['outer_disk'] - temp_df['inner_disk']) / temp_df['inner_disk'], 2)
    # 只有外盘没有内盘
    temp_df.loc[temp_df["inner_disk"] == 0, ['disk_ratio']] = 1688
    temp_df['disk_diff_amount'] = round(
        (temp_df['outer_disk'] - temp_df['inner_disk']) * temp_df[
            "average_price"] * 100,
        2)
    return temp_df


if __name__ == '__main__':
    cookie = 'qgqp_b_id=1e0d79428176ed54bef8434efdc0e8c3; mtp=1; ct=QVRY_s8Tiag1WfK2tSW2n03qpsX-PD8aH_rIjKVooawX8K33UVnpIofK088lD1lguWlE_OEIpQwn3PJWFPhHvSvyvYr4Zka3l4vxtZfH1Uikjtyy9z1H4Swo0rQzMKXncVzBXiOo5TjE-Dy9fcoG3ZF7UVdQ35jp_cFwzOlpK5Y; ut=FobyicMgeV51lVMr4ZJXvn-72bp0oeSOvtzifFY_U7kBFtR6og4Usd-VtBM5XBBvHq0lvd9xXkvpIqWro9EDKmv6cbKOQGyawUSMcKVP57isZCaM7lWQ6jWXajvTfvV4mIR-W_MZNK8VY0lL9W4qNMniJ6PBn_gkJsSAJCadmsyI9cxmjx--gR4m54pdF_nie_y4iWHys83cmWR2R7Bt1KKqB25OmkfCQTJJqIf7QsqangVGMUHwMC39Z9QhrfCFHKVNrlqS503O6b9GitQnXtvUdJhCmomu; pi=4253366368931142%3Bp4253366368931142%3B%E8%82%A1%E5%8F%8B9x56I87727%3BYNigLZRW%2FzMdGgVDOJbwReDWnTPHl51dB0gQLiwaCf1XY98mlJYx6eJbsoYr5Nie%2BX1L%2BzaMsec99KkX%2BT29Ds1arfST7sIBXxjUQ3dp11IPUnXy64PaBFRTHzMRWnCFJvvhc%2FAI41rXSGXolC8YMxI%2BvyPS%2BuErwgOVjC5vvsIiKeO7TLyKkhqqQJPX%2F7RWC5Sf3QLh%3Bdwjn4Xho10%2FKjqOgTWs%2FJF4%2FkdKzeuBwM8sz9aLvJovejAkCAyGMyGYA6AE67Xk2Ki7x8zdfBifF2DG%2Fvf2%2BXAYN8ZVISSEWTIXh32Z5MxEacK4JBTkqyiD93e1vFBOFQ82BqaiVmntUq0V6FrTUHGeh1gG5Sg%3D%3D; uidal=4253366368931142%e8%82%a1%e5%8f%8b9x56I87727; sid=170711377; vtpst=|; quote_lt=1; websitepoptg_api_time=1715777390466; emshistory=%5B%22%E8%BD%AC%E5%80%BA%E6%A0%87%22%2C%22%E8%BD%AC%E5%80%BA%E6%A0%87%E7%9A%84%22%5D; st_si=00364513876913; st_asi=delete; HAList=ty-116-00700-%u817E%u8BAF%u63A7%u80A1%2Cty-1-688695-%u4E2D%u521B%u80A1%u4EFD%2Cty-1-600849-%u4E0A%u836F%u8F6C%u6362%2Cty-1-603361-%u6D59%u6C5F%u56FD%u7965%2Cty-1-603555-ST%u8D35%u4EBA%2Cty-0-000627-%u5929%u8302%u96C6%u56E2%2Cty-0-002470-%u91D1%u6B63%u5927%2Cty-0-832876-%u6167%u4E3A%u667A%u80FD%2Cty-0-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cty-107-CWB-%u53EF%u8F6C%u503AETF-SPDR; st_pvi=26930719093675; st_sp=2024-04-28%2017%3A27%3A05; st_inirUrl=https%3A%2F%2Fcn.bing.com%2F; st_sn=23; st_psi=20240517111108288-113200301321-2767127768'
    df_hk_df = hk_real_time_quotes(cookie)
    df_hk_df = df_hk_df[[
        "symbol",
        "name",
        "chg", "amount"
    ]]
    print(df_hk_df)
