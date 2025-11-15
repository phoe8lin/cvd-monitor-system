"""
CVD分析模块 - 新版本
负责计算Z-Score、排名和背离检测（基于区间对比）
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class CVDScoreCalculator:
    """CVD Z-Score计算器"""

    def __init__(self):
        """初始化计算器"""
        pass

    def calculate_z_score(self, cvd_series: pd.Series) -> pd.Series:
        """
        计算CVD的Z-Score标准化

        Args:
            cvd_series: CVD时间序列

        Returns:
            pd.Series: Z-Score标准化后的数据
        """
        if len(cvd_series) == 0 or cvd_series.std() == 0:
            return pd.Series([0] * len(cvd_series), index=cvd_series.index)

        mean_val = cvd_series.mean()
        std_val = cvd_series.std()
        return (cvd_series - mean_val) / std_val

    def calculate_all_z_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有标的的Z-Score

        Args:
            df: 包含CVD数据的DataFrame

        Returns:
            DataFrame: 包含Z-Score的DataFrame
        """
        df_result = df.copy()
        df_result['cvd_zscore'] = df_result.groupby('symbol')['cvd'].transform(
            lambda x: self.calculate_z_score(x)
        )
        return df_result


class RankCalculator:
    """排名计算器"""

    def __init__(self):
        """初始化排名计算器"""
        pass

    def calculate_rankings(self, df: pd.DataFrame, metric: str = 'period_volume') -> pd.DataFrame:
        """
        计算排名

        Args:
            df: 数据DataFrame
            metric: 排名指标（period_volume, trade_count, cvd）

        Returns:
            DataFrame: 包含排名的DataFrame
        """
        if metric not in df.columns:
            raise ValueError(f"指标 {metric} 不存在于数据中")

        df_result = df.copy()

        if metric == 'period_volume':
            # 交易量排名
            latest_data = df_result.sort_values('timestamp').groupby('symbol').tail(1)
            latest_data = latest_data.sort_values('period_volume', ascending=False).reset_index(drop=True)
            latest_data[f'{metric}_rank'] = range(1, len(latest_data) + 1)
            return latest_data[['symbol', 'period_volume', 'period_volume_rank']].rename(
                columns={'period_volume': 'value', 'period_volume_rank': 'rank'}
            )

        elif metric == 'trade_count':
            # 交易笔数排名
            latest_data = df_result.sort_values('timestamp').groupby('symbol').tail(1)
            latest_data = latest_data.sort_values('trade_count', ascending=False).reset_index(drop=True)
            latest_data[f'{metric}_rank'] = range(1, len(latest_data) + 1)
            return latest_data[['symbol', 'trade_count', 'trade_count_rank']].rename(
                columns={'trade_count': 'value', 'trade_count_rank': 'rank'}
            )

        elif metric == 'cvd':
            # CVD排名
            latest_data = df_result.sort_values('timestamp').groupby('symbol').tail(1)
            latest_data = latest_data.sort_values('cvd', ascending=False).reset_index(drop=True)
            latest_data[f'{metric}_rank'] = range(1, len(latest_data) + 1)
            return latest_data[['symbol', 'cvd', 'cvd_rank']].rename(
                columns={'cvd': 'value', 'cvd_rank': 'rank'}
            )

        else:
            raise ValueError(f"不支持的排名指标: {metric}")


class DivergenceDetector:
    """CVD与价格背离检测器（基于区间对比）"""

    def __init__(self, zscore_threshold: float = 1.0, price_change_threshold: float = 0.05, window_size: int = 30):
        """
        初始化背离检测器

        Args:
            zscore_threshold: Z-Score阈值（默认1.0）
            price_change_threshold: 价格变化阈值（默认5%）
            window_size: 滑动窗口大小（默认30分钟）
        """
        self.zscore_threshold = zscore_threshold
        self.price_change_threshold = price_change_threshold
        self.window_size = window_size

    def calculate_trend(self, series: pd.Series) -> float:
        """
        计算序列的趋势（使用线性回归斜率）

        Args:
            series: 数据序列

        Returns:
            float: 趋势斜率（正值表示上升，负值表示下降）
        """
        if len(series) < 2:
            return 0

        # 使用线性回归计算趋势
        x = np.arange(len(series))
        y = series.values

        # 计算斜率
        slope = np.polyfit(x, y, 1)[0]
        return slope

    def detect_divergences(self, df: pd.DataFrame) -> List[str]:
        """
        检测CVD与价格背离的标的（基于区间对比）

        Args:
            df: 包含价格和CVD数据的DataFrame

        Returns:
            List[str]: 存在背离的标的列表
        """
        divergence_symbols = []

        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp').copy()

            if len(symbol_data) < self.window_size * 2:  # 数据点太少
                continue

            # 计算Z-Score
            zscore_calc = CVDScoreCalculator()
            symbol_data = zscore_calc.calculate_all_z_scores(symbol_data)

            # 滑动窗口检测背离
            divergence_periods = self._detect_divergence_periods(symbol_data)

            if divergence_periods:
                divergence_symbols.append(symbol)

        return list(set(divergence_symbols))

    def _detect_divergence_periods(self, symbol_data: pd.DataFrame) -> List[Dict]:
        """
        检测背离区间

        Args:
            symbol_data: 单个标的数据

        Returns:
            List[Dict]: 背离区间列表，每个区间包含开始、结束、强度等信息
        """
        divergence_periods = []

        # 滑动窗口检测
        for i in range(self.window_size, len(symbol_data) - self.window_size):
            # 获取当前窗口
            window_start = i - self.window_size
            window_end = i
            window_data = symbol_data.iloc[window_start:window_end]

            # 计算CVD趋势（使用Z-Score）
            cvd_trend = self.calculate_trend(window_data['cvd_zscore'])

            # 计算价格趋势
            price_trend = self.calculate_trend(window_data['price'])

            # 标准化趋势（除以标准差，使其可比较）
            cvd_trend_normalized = cvd_trend / (window_data['cvd_zscore'].std() + 1e-10)
            price_trend_normalized = price_trend / (window_data['price'].std() + 1e-10)

            # 判断背离条件：
            # 1. CVD趋势显著（绝对值 > 0.1）
            # 2. 价格趋势显著（绝对值 > 0.1）
            # 3. 趋势方向相反
            if (abs(cvd_trend_normalized) > 0.1 and
                abs(price_trend_normalized) > 0.1 and
                cvd_trend_normalized * price_trend_normalized < 0):

                # 计算背离强度
                divergence_strength = min(abs(cvd_trend_normalized), abs(price_trend_normalized))

                # 检查是否与前一个背离区间重叠
                if divergence_periods:
                    last_period = divergence_periods[-1]
                    if i < last_period['end_idx']:
                        continue  # 跳过重叠的区间

                # 找到背离结束点
                end_idx = self._find_divergence_end(symbol_data, i, cvd_trend_normalized, price_trend_normalized)

                divergence_periods.append({
                    'start_idx': window_start,
                    'end_idx': end_idx,
                    'start_time': window_data.iloc[0]['timestamp'],
                    'end_time': symbol_data.iloc[end_idx - 1]['timestamp'],
                    'cvd_trend': cvd_trend_normalized,
                    'price_trend': price_trend_normalized,
                    'strength': divergence_strength,
                    'duration': end_idx - window_start
                })

        return divergence_periods

    def _find_divergence_end(self, symbol_data: pd.DataFrame, start_idx: int, cvd_trend: float, price_trend: float) -> int:
        """
        找到背离区间的结束点

        Args:
            symbol_data: 数据
            start_idx: 背离开始索引
            cvd_trend: CVD趋势
            price_trend: 价格趋势

        Returns:
            int: 结束索引
        """
        max_lookahead = self.window_size  # 最多再看window_size个点

        for j in range(start_idx + 5, min(start_idx + max_lookahead, len(symbol_data))):
            # 获取当前窗口
            window_data = symbol_data.iloc[j-self.window_size:j]

            # 重新计算趋势
            current_cvd_trend = self.calculate_trend(window_data['cvd_zscore'])
            current_price_trend = self.calculate_trend(window_data['price'])

            # 标准化
            cvd_trend_normalized = current_cvd_trend / (window_data['cvd_zscore'].std() + 1e-10)
            price_trend_normalized = current_price_trend / (window_data['price'].std() + 1e-10)

            # 如果趋势不再相反，或者趋势减弱，背离结束
            if (cvd_trend_normalized * price_trend_normalized >= 0 or
                abs(cvd_trend_normalized) < 0.05 or
                abs(price_trend_normalized) < 0.05):
                return j

        # 如果没找到结束点，返回开始点+window_size
        return min(start_idx + self.window_size, len(symbol_data))

    def calculate_divergence_data(self, df: pd.DataFrame, symbols: List[str]) -> pd.DataFrame:
        """
        计算背离数据用于可视化

        Args:
            df: 原始数据
            symbols: 标的列表

        Returns:
            DataFrame: 包含背离分析的数据
        """
        result_data = []

        for symbol in symbols:
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp').copy()

            if len(symbol_data) < 10:
                continue

            # 计算Z-Score
            zscore_calc = CVDScoreCalculator()
            symbol_data = zscore_calc.calculate_all_z_scores(symbol_data)

            # 计算价格变化
            symbol_data['price_change'] = symbol_data['price'].pct_change()

            result_data.append(symbol_data)

        if result_data:
            return pd.concat(result_data, ignore_index=True)
        else:
            return pd.DataFrame()

    def get_divergence_periods(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        获取背离区间信息

        Args:
            df: 原始数据

        Returns:
            Dict: {symbol: [{'start_time': ..., 'end_time': ..., 'strength': ..., ...}, ...]}
        """
        divergence_periods_dict = {}

        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp').copy()

            if len(symbol_data) < self.window_size * 2:
                continue

            # 计算Z-Score
            zscore_calc = CVDScoreCalculator()
            symbol_data = zscore_calc.calculate_all_z_scores(symbol_data)

            # 检测背离区间
            periods = self._detect_divergence_periods(symbol_data)

            if periods:
                divergence_periods_dict[symbol] = periods

        return divergence_periods_dict
