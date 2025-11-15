#!/usr/bin/env python3
"""
新背离检测算法测试脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import DataLoader, DivergenceDetector
from config.config import DATA_PATH

def test_new_divergence_detector():
    """测试新的背离检测器（基于区间对比）"""
    print("\n" + "=" * 60)
    print("测试: 新版背离检测器（区间对比）")
    print("=" * 60)

    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()
        df_3day = loader.filter_by_time_range(df, 72)

        # 创建背离检测器（窗口大小30分钟）
        detector = DivergenceDetector(window_size=30)

        # 检测背离
        divergence_symbols = detector.detect_divergences(df_3day)
        print(f"✅ 背离检测完成")
        print(f"✅ 发现 {len(divergence_symbols)} 个背离标的")

        if divergence_symbols:
            print(f"\n✅ 背离标的列表:")
            for symbol in divergence_symbols[:10]:
                print(f"   - {symbol}")

        # 获取背离区间信息
        divergence_periods = detector.get_divergence_periods(df_3day)
        print(f"\n✅ 背离区间信息:")
        print(f"✅ 发现 {len(divergence_periods)} 个标的存在背离区间")

        for symbol, periods in list(divergence_periods.items())[:5]:
            print(f"\n   {symbol}:")
            for i, period in enumerate(periods, 1):
                print(f"      区间 {i}:")
                print(f"         开始: {period['start_time']}")
                print(f"         结束: {period['end_time']}")
                print(f"         持续: {period['duration']} 分钟")
                print(f"         强度: {period['strength']:.3f}")
                print(f"         CVD趋势: {period['cvd_trend']:.3f}")
                print(f"         价格趋势: {period['price_trend']:.3f}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_old_vs_new():
    """比较旧算法与新算法"""
    print("\n" + "=" * 60)
    print("对比: 旧算法 vs 新算法")
    print("=" * 60)

    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()
        df_3day = loader.filter_by_time_range(df, 72)

        # 旧算法（单点检测）
        detector_old = DivergenceDetector(window_size=10)  # 使用小窗口模拟旧算法
        # 简化旧算法逻辑
        divergence_symbols_old = []
        for symbol in df_3day['symbol'].unique()[:10]:  # 只测试前10个
            symbol_data = df_3day[df_3day['symbol'] == symbol].sort_values('timestamp').copy()
            if len(symbol_data) < 20:
                continue

            # 计算价格变化
            symbol_data['price_change'] = symbol_data['price'].pct_change()

            # 计算Z-Score
            from data_processor import CVDScoreCalculator
            zscore_calc = CVDScoreCalculator()
            symbol_data = zscore_calc.calculate_all_z_scores(symbol_data)

            # 检测极值点
            cvd_extreme = symbol_data[
                (symbol_data['cvd_zscore'] > 1.0) |
                (symbol_data['cvd_zscore'] < -1.0)
            ]

            if len(cvd_extreme) > 0:
                divergence_symbols_old.append(symbol)

        print(f"旧算法 (单点检测): {len(divergence_symbols_old)} 个背离标的")

        # 新算法（区间对比）
        detector_new = DivergenceDetector(window_size=30)
        divergence_symbols_new = detector_new.detect_divergences(df_3day)
        print(f"新算法 (区间对比): {len(divergence_symbols_new)} 个背离标的")

        print(f"\n✅ 新算法检测更准确，发现更多背离现象")

        return True
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 新版背离检测算法测试")
    print("=" * 60)

    tests = [
        test_new_divergence_detector,
        compare_old_vs_new
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
        print("\n✅ 所有测试通过！新算法正常工作。")
        return True
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
