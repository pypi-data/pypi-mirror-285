import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import akshare as ak


# Index(['代码', '名称', '最新价', 'IOPV实时估值', '基金折价率', '涨跌额', '涨跌幅', '成交量', '成交额',
#        '开盘价', '最高价', '最低价', '昨收', '振幅', '换手率', '量比', '委比', '外盘', '内盘',
#        '主力净流入-净额', '主力净流入-净占比', '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额',
#        '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比', '小单净流入-净额', '小单净流入-净占比', '现手',
#        '买一', '卖一', '最新份额', '流通市值', '总市值', '数据日期', '更新时间'],
def get_etf_real_time_quotes():
    fund_etf_spot_em_df = ak.fund_etf_spot_em()
    fund_etf_spot_em_df = fund_etf_spot_em_df.rename(columns={
        "最新价": "now_price",
        "涨跌幅": "chg",
        "基金折价率": "fund_discount_rate",
        "振幅": "pct_chg",
        "涨跌额": "range",
        "成交额": "amount",
        "成交量": "volume",
        "换手率": "exchange",
        "量比": "quantity_ratio",
        "代码": "symbol",
        "名称": "name",
        "最高价": "high",
        "最低价": "low",
        "开盘价": "open",
        "昨收": "yesterday_price",
        "总市值": "total_mv",
        "流通市值": "flow_mv",
        "委比": "wei_bi",
        "外盘": "outer_disk",
        "内盘": "inner_disk",
        "主力净流入-净额": "today_main_net_inflow",
        "超大单净流入-净额": "super_large_order_net_inflow",
        "超大单净流入-净占比": "super_large_order_net_inflow_ratio",
        "大单净流入-净额": "large_order_net_inflow",
        # "f78": "medium_order_net_inflow",
        # "f84": "small_order_net_inflow",
        # "f103": "concept",
        "主力净流入-净占比": "today_main_net_inflow_ratio",
        "买一": "buy_1_num",
        "卖一": "sell_1_num",
        "最新份额": "latest_share",
        "数据日期": "data_time",
        "更新日期": "update_time"
    })
    return fund_etf_spot_em_df


if __name__ == '__main__':
    fund_etf_df = get_etf_real_time_quotes()
    fund_etf_df = fund_etf_df.sort_values(by=['amount'], ascending=False)
    print(fund_etf_df)

    import akshare as ak

    fund_lof_spot_em_df = ak.fund_lof_spot_em()
    print(fund_lof_spot_em_df)
