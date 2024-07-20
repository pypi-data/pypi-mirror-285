import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 14
project_path = file_path[0:end]
sys.path.append(project_path)
# 大单同步表
BIG_DEAL_NAME = "ths_big_deal_fund"
# 大单选择表
BIG_DEAL_CHOOSE_NAME = "big_deal_fund_choose"
# 实时行情表 临时数据
REAL_TIME_QUOTES_NOW = 'realtime_quotes_now'
# 当前实时涨停表
TODAY_ZT_POOL = 'today_zt_pool'
# 集合竞价表
CALL_AUCTION_DB_NAME = 'call_auction_signal'
# 实时竞价表
CALL_AUCTION_DB_NAME_REAL_TIME = 'call_auction_signal_realtime'
# 涨停打板表
NOW_TIME_ZT_DA_BAN = 'now_time_zt_da_ban'
# 开盘啦精选指数表
KPL_BEST_CHOOSE_INDEX = 'kpl_best_choose_index'
# 开盘啦详细组成
KPL_BEST_CHOOSE_INDEX_DETAIL = "kpl_best_choose_index_detail"

# 同花顺概念表
THS_CONCEPT_LIST = "ths_concept_list"

# 同花顺概念详情表
THS_STOCK_CONCEPT_DETAIL = "ths_stock_concept_detail"
# 今日排除买入股票
TODAY_EXCLUDE_STOCK = "today_exclude_stocks"
# 今日买入股票
BUY_STOCK_NAME = 'trade_stocks'

#  公司信息表
COMPANY_INFO = 'company_info'
#  公司信息历史表
COMPANY_INFO_HIS = 'company_info_his'

# TODAY_NEW_CONCEPT_LIST
TODAY_NEW_CONCEPT_LIST = 'today_new_concept_list'

# 开票啦历史数据
KPL_BEST_CHOOSE_HIS = 'kpl_best_choose_his'

# 开票啦每日数据
KPL_BEST_CHOOSE_DAILY = 'kpl_best_choose_daily'

# 当前持仓股票
POSITION_STOCK = 'position_stock'

# 个股黑名单
SELF_BLACK_STOCK = 'self_black_stock'
# 自选板块
SELF_CHOOSE_PLATE = 'self_choose_plate'
# 自选个股
SELF_CHOOSE_STOCK = 'self_choose_stock'

# 利润表
EM_STOCK_PROFIT = 'em_stock_profit'

# 资产负债表
EM_STOCK_ASSET_LIABILITY = 'em_stock_asset_liability'

# 退市股票列表
DE_LIST_STOCK = 'de_list_stock'

# 当前涨停列表
STOCK_ZT_POOL = 'stock_zt_pool'

# ths问财涨停股票池
THS_ZT_POOL = 'ths_zt_pool'

# 五板以上的历史高标
STOCK_ZT_POOL_FIVE = 'stock_zt_pool_five'

# 香港公司信息
COMPANY_INFO_HK = 'company_info_hk'

# k线前复权
STOCK_QFQ_DAILY = 'stock_qfq_daily'

# 最近高涨股票
RECENT_HOT_STOCKS = 'recent_hot_stocks'

# 互动提问
STOCK_INTERACTIVE_QUESTION = 'stock_interactive_question'

# 上交所 互动ID映射代码

SSE_INFO_UID = 'sse_info_uid'

# kcx 高涨幅>9.5 当天开盘数据
KCX_HIGH_CHG_OPEN_DATA = 'realtime_quotes_now_zt_new_kc_open'

# 涨停股票(chg>=9.57)实时行情数据
ZT_STOCK_REAL_TIME_QUOTES = "realtime_quotes_now_zt_new"

# 高涨幅和涨停表
STOCK_HIGH_CHG_POOL = 'stock_high_chg_pool'

# 股票账户信息
STOCK_ACCOUNT_INFO = 'stock_account_info'

# 可转债信息
KZZ_DEBT_INFO = 'kzz_debt_info'
