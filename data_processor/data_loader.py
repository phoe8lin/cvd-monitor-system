"""
数据加载模块
负责读取和预处理CSV数据
"""
import pandas as pd
from typing import List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta


class DataLoader:
    """数据加载器"""

    def __init__(self, csv_path: str):
        """
        初始化数据加载器

        Args:
            csv_path: CSV文件路径
        """
        self.csv_path = csv_path

    def load_data(self) -> pd.DataFrame:
        """
        加载CSV数据

        Returns:
            DataFrame: 包含所有数据的DataFrame
        """
        try:
            df = pd.read_csv(self.csv_path)
            # 转换时间戳
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # 对CVD保留两位小数
            df['cvd'] = df['cvd'].round(2)
            return df
        except Exception as e:
            print(f"加载数据时出错: {e}")
            raise

    def get_symbols(self) -> List[str]:
        """
        获取所有交易标的

        Returns:
            List[str]: 标的列表
        """
        df = self.load_data()
        return sorted(df['symbol'].unique().tolist())

    def filter_by_time_range(self, df: pd.DataFrame, hours: int = 72) -> pd.DataFrame:
        """
        按时间范围筛选数据

        Args:
            df: 原始数据
            hours: 小时数（默认72小时=3天）

        Returns:
            DataFrame: 筛选后的数据
        """
        latest_time = df['timestamp'].max()
        start_time = latest_time - timedelta(hours=hours)
        return df[df['timestamp'] >= start_time].copy()

    def filter_by_day(self, df: pd.DataFrame, days: int = 1) -> pd.DataFrame:
        """
        按天数筛选数据

        Args:
            df: 原始数据
            days: 天数（默认1天）

        Returns:
            DataFrame: 筛选后的数据
        """
        latest_time = df['timestamp'].max()
        start_time = latest_time - timedelta(days=days)
        return df[df['timestamp'] >= start_time].copy()

    def filter_by_symbols(self, df: pd.DataFrame, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        按标的筛选数据

        Args:
            df: 原始数据
            symbols: 标的列表，如果为None则返回所有数据

        Returns:
            DataFrame: 筛选后的数据
        """
        if symbols is None or len(symbols) == 0:
            return df
        return df[df['symbol'].isin(symbols)].copy()

    def get_latest_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        获取每个标的的最新数据

        Args:
            df: 原始数据

        Returns:
            DataFrame: 最新数据
        """
        return df.sort_values('timestamp').groupby('symbol').tail(1).reset_index(drop=True)
