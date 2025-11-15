"""
CVD分析模块
负责计算Z-Score、排名和背离检测
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
    """CVD与价格背离检测器"""

    def __init__(self, zscore_threshold: float = 1.0, price_change_threshold: float = 0.05):
        """
        初始化背离检测器

        Args:
            zscore_threshold: Z-Score阈值（默认1.0）
            price_change_threshold: 价格变化阈值（默认5%）
        """
        self.zscore_threshold = zscore_threshold
        self.price_change_threshold = price_change_threshold

    def detect_divergences(self, df: pd.DataFrame) -> List[str]:
        """
        检测CVD与价格背离的标的

        Args:
            df: 包含价格和CVD数据的DataFrame

        Returns:
            List[str]: 存在背离的标的列表
        """
        divergence_symbols = []

        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp').copy()

            if len(symbol_data) < 10:  # 数据点太少
                continue

            # 计算价格变化
            symbol_data['price_change'] = symbol_data['price'].pct_change()

            # 计算Z-Score
            zscore_calc = CVDScoreCalculator()
            symbol_data = zscore_calc.calculate_all_z_scores(symbol_data)

            # 检测背离
            # 1. CVD极值（Z-Score > 阈值或 < -阈值）
            cvd_extreme = symbol_data[
                (symbol_data['cvd_zscore'] > self.zscore_threshold) |
                (symbol_data['cvd_zscore'] < -self.zscore_threshold)
            ]

            if len(cvd_extreme) == 0:
                continue

            # 2. 价格变化趋势与CVD趋势相反
            for idx in cvd_extreme.index:
                window = symbol_data.loc[:idx].tail(10)  # 查看前10个数据点

                if len(window) < 5:
                    continue

                # CVD趋势
                cvd_trend = window['cvd_zscore'].iloc[-1] - window['cvd_zscore'].iloc[0]

                # 价格趋势
                price_trend = (window['price'].iloc[-1] - window['price'].iloc[0]) / window['price'].iloc[0]

                # 背离条件：
                # - CVD正极值但价格下降，或
                # - CVD负极值但价格上升
                if (cvd_trend > 0 and price_trend < -self.price_change_threshold) or \
                   (cvd_trend < 0 and price_trend > self.price_change_threshold):
                    divergence_symbols.append(symbol)
                    break

        return list(set(divergence_symbols))

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

    def get_divergence_points(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        获取背离点的详细信息

        Args:
            df: 原始数据

        Returns:
            Dict: {symbol: [{'timestamp': ..., 'price': ..., 'cvd': ...}, ...]}
        """
        divergence_points = {}

        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp').copy()

            if len(symbol_data) < 10:
                continue

            # 计算价格变化
            symbol_data['price_change'] = symbol_data['price'].pct_change()

            # 计算Z-Score
            zscore_calc = CVDScoreCalculator()
            symbol_data = zscore_calc.calculate_all_z_scores(symbol_data)

            # 检测背离
            cvd_extreme = symbol_data[
                (symbol_data['cvd_zscore'] > self.zscore_threshold) |
                (symbol_data['cvd_zscore'] < -self.zscore_threshold)
            ]

            if len(cvd_extreme) == 0:
                continue

            # 记录背离点
            points = []
            for idx in cvd_extreme.index:
                window = symbol_data.loc[:idx].tail(10)

                if len(window) < 5:
                    continue

                cvd_trend = window['cvd_zscore'].iloc[-1] - window['cvd_zscore'].iloc[0]
                price_trend = (window['price'].iloc[-1] - window['price'].iloc[0]) / window['price'].iloc[0]

                if (cvd_trend > 0 and price_trend < -self.price_change_threshold) or \
                   (cvd_trend < 0 and price_trend > self.price_change_threshold):
                    points.append({
                        'timestamp': symbol_data.loc[idx, 'timestamp'],
                        'price': symbol_data.loc[idx, 'price'],
                        'cvd': symbol_data.loc[idx, 'cvd'],
                        'cvd_zscore': symbol_data.loc[idx, 'cvd_zscore']
                    })

            if points:
                divergence_points[symbol] = points

        return divergence_points
