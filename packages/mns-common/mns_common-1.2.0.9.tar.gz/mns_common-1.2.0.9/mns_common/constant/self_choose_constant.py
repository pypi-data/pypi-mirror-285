import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

# 同花顺概念
SELF_CHOOSE_THS_CONCEPT = 'ths_concept'
# 同花顺行业
SELF_CHOOSE_THS_INDUSTRY = 'ths_industry'

SELF_CHOOSE_KPL_CONCEPT = 'kpl_concept'

# 开盘啦一级概念
SELF_CHOOSE_KPL_FIRST_CONCEPT = 'kpl_first_concept'

# 开盘啦二级概念
SELF_CHOOSE_KPL_SECOND_CONCEPT = 'kpl_second_concept'
