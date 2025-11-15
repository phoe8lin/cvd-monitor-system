"""
配置文件
"""
import os

# 数据文件路径
DATA_PATH = "/Volumes/external/trade/高效cvd计算/cvd_monitor_speed/cvd_data_optimized/cvd_data_all.csv"

# 时间范围设置
DEFAULT_HOURS_3DAY = 72
DEFAULT_HOURS_1DAY = 24

# CVD Z-Score分析参数
ZSCORE_THRESHOLD = 1.0

# 背离检测参数
DIVERGENCE_ZSCORE_THRESHOLD = 1.0
DIVERGENCE_PRICE_CHANGE_THRESHOLD = 0.05

# 页面刷新间隔（秒）
REFRESH_INTERVAL = 30

# 图表配置
CHART_HEIGHT = 500
RANKING_CHART_HEIGHT = 400
DIVERGENCE_CHART_HEIGHT = 400
