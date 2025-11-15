#!/usr/bin/env python3
"""
数据处理模块测试脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import DataLoader, CVDScoreCalculator, RankCalculator, DivergenceDetector
from config.config import DATA_PATH

def test_data_loader():
    """测试数据加载器"""
    print("\n" + "=" * 60)
    print("测试1: 数据加载器")
    print("=" * 60)

    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()
        print(f"✅ 数据加载成功，共 {len(df)} 行")
        print(f"✅ 数据列: {list(df.columns)}")
        print(f"✅ 标的数量: {len(df['symbol'].unique())}")
        print(f"✅ 时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")

        # 测试筛选功能
        df_3day = loader.filter_by_time_range(df, 72)
        print(f"✅ 近3天数据: {len(df_3day)} 行")

        symbols = loader.get_symbols()
        print(f"✅ 获取标的列表成功: {len(symbols)} 个")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zscore_calculator():
    """测试Z-Score计算器"""
    print("\n" + "=" * 60)
    print("测试2: Z-Score计算器")
    print("=" * 60)

    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()

        # 筛选少量数据用于测试
        symbols = df['symbol'].unique()[:5]
        df_test = df[df['symbol'].isin(symbols)]

        zscore_calc = CVDScoreCalculator()
        df_with_zscore = zscore_calc.calculate_all_z_scores(df_test)

        print(f"✅ Z-Score计算成功")
        print(f"✅ 包含Z-Score列: {'cvd_zscore' in df_with_zscore.columns}")

        # 验证Z-Score分布
        latest_data = df_with_zscore.sort_values('timestamp').groupby('symbol').tail(1)
        print(f"✅ 最新数据Z-Score范围: {latest_data['cvd_zscore'].min():.2f} 至 {latest_data['cvd_zscore'].max():.2f}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rank_calculator():
    """测试排名计算器"""
    print("\n" + "=" * 60)
    print("测试3: 排名计算器")
    print("=" * 60)

    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()

        rank_calc = RankCalculator()

        # 测试交易量排名
        volume_ranking = rank_calc.calculate_rankings(df, 'period_volume')
        print(f"✅ 交易量排名计算成功: {len(volume_ranking)} 个标的")
        print(f"✅ Top 3: {volume_ranking.head(3)['symbol'].tolist()}")

        # 测试交易笔数排名
        trade_ranking = rank_calc.calculate_rankings(df, 'trade_count')
        print(f"✅ 交易笔数排名计算成功: {len(trade_ranking)} 个标的")

        # 测试CVD排名
        cvd_ranking = rank_calc.calculate_rankings(df, 'cvd')
        print(f"✅ CVD排名计算成功: {len(cvd_ranking)} 个标的")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_divergence_detector():
    """测试背离检测器"""
    print("\n" + "=" * 60)
    print("测试4: 背离检测器")
    print("=" * 60)

    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()

        # 获取近3天数据
        df_3day = loader.filter_by_time_range(df, 72)
        print(f"✅ 近3天数据: {len(df_3day)} 行")

        detector = DivergenceDetector()
        divergence_symbols = detector.detect_divergences(df_3day)

        print(f"✅ 背离检测完成")
        print(f"✅ 发现 {len(divergence_symbols)} 个背离标的")

        if divergence_symbols:
            print(f"   前10个: {divergence_symbols[:10]}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 CVD监测系统 - 数据处理模块测试")
    print("=" * 60)

    tests = [
        test_data_loader,
        test_zscore_calculator,
        test_rank_calculator,
        test_divergence_detector
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"总测试数: {len(results)}")
    print(f"通过: {sum(results)}")
    print(f"失败: {len(results) - sum(results)}")

    if all(results):
        print("\n✅ 所有测试通过！应用可以正常启动。")
        return True
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
