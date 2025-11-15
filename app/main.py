"""
CVD监测Web应用
基于Streamlit构建的实时CVD数据分析系统
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import DataLoader, CVDScoreCalculator, RankCalculator, DivergenceDetector
from config.config import *

# 页面配置
st.set_page_config(
    page_title="CVD监测系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_and_process_data():
    """加载并处理数据（缓存30秒）"""
    try:
        loader = DataLoader(DATA_PATH)
        df = loader.load_data()
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None


def main():
    """主函数"""

    # 页面标题
    st.markdown('<h1 class="main-header">📊 CVD监测系统</h1>', unsafe_allow_html=True)

    # 添加刷新按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        refresh_button = st.button("🔄 刷新数据", type="primary")

    # 加载数据
    # 如果点击刷新按钮，清除缓存并重新加载
    if refresh_button:
        st.cache_data.clear()
        st.rerun()

    with st.spinner("正在加载数据..."):
        df = load_and_process_data()

    if df is None or df.empty:
        st.error("❌ 无法加载数据，请检查数据文件路径")
        return

    # 获取所有标的
    all_symbols = sorted(df['symbol'].unique().tolist())

    # 侧边栏 - 筛选条件
    st.sidebar.header("🎯 筛选条件")

    # 标的筛选
    selected_symbols = st.sidebar.multiselect(
        "选择标的 (默认全选)",
        options=all_symbols,
        default=all_symbols,
        help="选择一个或多个标的进行分析"
    )

    # 如果没有选择标的，默认为全选
    if not selected_symbols:
        selected_symbols = all_symbols

    # 时间范围选择
    time_range = st.sidebar.selectbox(
        "时间范围",
        options=[("近3天", 72), ("近1天", 24)],
        format_func=lambda x: x[0],
        index=0,
        help="选择分析的时间范围"
    )

    hours = time_range[1]

    # 筛选数据
    loader = DataLoader(DATA_PATH)
    filtered_df = loader.filter_by_time_range(df, hours)
    filtered_df = loader.filter_by_symbols(filtered_df, selected_symbols)

    if filtered_df.empty:
        st.warning("⚠️ 当前筛选条件下没有数据")
        return

    # 主页面内容
    st.markdown(f"**数据时间范围**: {filtered_df['timestamp'].min()} 至 {filtered_df['timestamp'].max()}")

    # 创建Tab页面
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 CVD曲线分析",
        "🏆 排名统计",
        "⚠️ 背离检测",
        "📊 数据概览"
    ])

    with tab1:
        st.header("CVD曲线分析 (Z-Score标准化)")
        st.write("Z-Score标准化后的CVD曲线，Y轴表示偏离均值的标准差数量")

        # Z-Score说明
        with st.expander("📘 关于Z-Score分析", expanded=False):
            st.markdown("""
            ### Z-Score标准化原理
            **Z-Score公式**: `(当前CVD值 - 均值) / 标准差`

            ### 分析方法
            - **无单位，可比较**: 所有数据都转换为"偏离均值多少个标准差"的单位
            - **直接比较不同标的**: Z-Score为2的标的，其资金推动强度远大于Z-Score为0.5的标的

            ### 动能解读
            - **零轴上方**: 资金净流入强于平均水平
            - **零轴下方**: 资金净流入弱于平均水平

            ### 关键区域
            - **Z-Score > +1**: 持续位于高位且向上倾斜 → 🔴 **强势买入动能**
            - **Z-Score < -1**: 持续位于低位且向下倾斜 → 🟢 **强势卖出动能**
            - **零轴附近**: 动能中性，多空平衡 → ⚪ **中性状态**

            ### 参考线说明
            - **灰色实线**: 零轴（均值线）
            - **红色虚线**: +1标准差阈值
            - **绿色虚线**: -1标准差阈值
            """)

        # 计算Z-Score
        zscore_calc = CVDScoreCalculator()
        df_with_zscore = zscore_calc.calculate_all_z_scores(filtered_df)

        # 创建CVD曲线图
        fig = go.Figure()

        # 为每个标的添加一条线
        for symbol in selected_symbols:
            symbol_data = df_with_zscore[df_with_zscore['symbol'] == symbol]
            if not symbol_data.empty:
                fig.add_trace(go.Scatter(
                    x=symbol_data['timestamp'],
                    y=symbol_data['cvd_zscore'],
                    mode='lines',
                    name=symbol,
                    line=dict(width=2),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  '时间: %{x}<br>' +
                                  'Z-Score: %{y:.2f}<br>' +
                                  '<extra></extra>'
                ))

        # 添加零轴参考线
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_hline(y=1, line_dash="dash", line_color="red", opacity=0.3)
        fig.add_hline(y=-1, line_dash="dash", line_color="green", opacity=0.3)

        # 更新布局
        fig.update_layout(
            height=CHART_HEIGHT,
            xaxis_title="时间",
            yaxis_title="CVD Z-Score",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("排名统计")

        # 创建两个子列
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 交易量排名 (最新)")

            # 交易量排名
            rank_calc = RankCalculator()
            volume_ranking = rank_calc.calculate_rankings(filtered_df, 'period_volume')

            # 只显示前20名
            display_data = volume_ranking.head(20)

            fig = px.bar(
                display_data,
                x='value',
                y='symbol',
                orientation='h',
                title="交易量 Top 20",
                color='value',
                color_continuous_scale='Blues',
                text='rank'
            )

            fig.update_layout(
                height=RANKING_CHART_HEIGHT,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="交易量",
                yaxis_title="标的"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📈 交易笔数排名 (最新)")

            # 交易笔数排名
            trade_ranking = rank_calc.calculate_rankings(filtered_df, 'trade_count')

            # 只显示前20名
            display_data = trade_ranking.head(20)

            fig = px.bar(
                display_data,
                x='value',
                y='symbol',
                orientation='h',
                title="交易笔数 Top 20",
                color='value',
                color_continuous_scale='Greens',
                text='rank'
            )

            fig.update_layout(
                height=RANKING_CHART_HEIGHT,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="交易笔数",
                yaxis_title="标的"
            )

            st.plotly_chart(fig, use_container_width=True)

        # CVD排名
        st.subheader("💎 CVD排名 (最新)")
        cvd_ranking = rank_calc.calculate_rankings(filtered_df, 'cvd')

        display_data = cvd_ranking.head(20)

        fig = px.bar(
            display_data,
            x='value',
            y='symbol',
            orientation='h',
            title="CVD Top 20",
            color='value',
            color_continuous_scale='Reds',
            text='rank'
        )

        fig.update_layout(
            height=RANKING_CHART_HEIGHT,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="CVD值",
            yaxis_title="标的"
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("CVD与价格背离检测")
        st.write("检测近3天内CVD与价格走势背离的标的")

        # 检测背离
        divergence_detector = DivergenceDetector(
            zscore_threshold=DIVERGENCE_ZSCORE_THRESHOLD,
            price_change_threshold=DIVERGENCE_PRICE_CHANGE_THRESHOLD
        )

        # 获取近3天数据用于背离检测
        df_3day = loader.filter_by_time_range(df, 72)
        divergence_symbols = divergence_detector.detect_divergences(df_3day)

        if divergence_symbols:
            st.success(f"检测到 {len(divergence_symbols)} 个存在背离的标的")

            # 显示背离标的列表
            st.subheader("背离标的列表")
            for symbol in divergence_symbols[:20]:  # 最多显示20个
                st.write(f"⚠️ {symbol}")

            # 可视化背离标的
            st.subheader("背离走势可视化")

            # 如果选择了背离标的，只显示这些
            if len(selected_symbols) < len(all_symbols):
                # 如果用户已选择标的，过滤出既是选择的又是背离的
                display_symbols = [s for s in selected_symbols if s in divergence_symbols]
            else:
                # 否则显示所有背离标的
                display_symbols = divergence_symbols[:5]  # 最多显示5个，避免图表过于复杂

            if display_symbols:
                # 计算背离数据
                divergence_data = divergence_detector.calculate_divergence_data(df_3day, display_symbols)
                # 获取背离区间信息
                divergence_periods = divergence_detector.get_divergence_periods(df_3day)

                if not divergence_data.empty:
                    fig = go.Figure()

                    for symbol in display_symbols:
                        symbol_data = divergence_data[divergence_data['symbol'] == symbol]

                        if not symbol_data.empty:
                            # 绘制价格线（左Y轴）
                            fig.add_trace(go.Scatter(
                                x=symbol_data['timestamp'],
                                y=symbol_data['price'],
                                mode='lines',
                                name=f'{symbol} - 价格',
                                line=dict(width=2, color='blue'),
                                yaxis='y',
                                hovertemplate='<b>%{fullData.name}</b><br>' +
                                              '时间: %{x}<br>' +
                                              '价格: %{y:.2f}<br>' +
                                              '<extra></extra>'
                            ))

                            # 绘制CVD曲线（右Y轴）
                            fig.add_trace(go.Scatter(
                                x=symbol_data['timestamp'],
                                y=symbol_data['cvd'],
                                mode='lines',
                                name=f'{symbol} - CVD',
                                line=dict(width=2, color='red'),
                                yaxis='y2',
                                hovertemplate='<b>%{fullData.name}</b><br>' +
                                              '时间: %{x}<br>' +
                                              'CVD: %{y:.2f}<br>' +
                                              '<extra></extra>'
                            ))

                            # 绘制背离区间（阴影区域）
                            if symbol in divergence_periods:
                                for period in divergence_periods[symbol]:
                                    # 添加背离区间阴影
                                    fig.add_vrect(
                                        x0=period['start_time'],
                                        x1=period['end_time'],
                                        fillcolor="orange",
                                        opacity=0.2,
                                        line_width=0,
                                        layer="below",
                                        yref="y2"  # 绑定到右Y轴
                                    )

                                    # 标记背离开始和结束点
                                    fig.add_trace(go.Scatter(
                                        x=[period['start_time']],
                                        y=[symbol_data[symbol_data['timestamp'] <= period['start_time']]['price'].iloc[-1]],
                                        mode='markers',
                                        marker=dict(size=12, color='orange', symbol='triangle-up'),
                                        name=f'{symbol} 背离开始',
                                        yaxis='y',
                                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                                      f'时间: {period["start_time"]}<br>' +
                                                      f'强度: {period["strength"]:.2f}<br>' +
                                                      '<extra></extra>',
                                        showlegend=(period == divergence_periods[symbol][0])  # 只在第一个区间显示图例
                                    ))

                                    fig.add_trace(go.Scatter(
                                        x=[period['end_time']],
                                        y=[symbol_data[symbol_data['timestamp'] <= period['end_time']]['price'].iloc[-1]],
                                        mode='markers',
                                        marker=dict(size=12, color='orange', symbol='triangle-down'),
                                        name=f'{symbol} 背离结束',
                                        yaxis='y',
                                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                                      f'时间: {period["end_time"]}<br>' +
                                                      f'持续: {period["duration"]} 分钟<br>' +
                                                      '<extra></extra>',
                                        showlegend=False
                                    ))

                    # 更新布局（双Y轴）
                    fig.update_layout(
                        height=DIVERGENCE_CHART_HEIGHT,
                        xaxis_title="时间",
                        yaxis=dict(
                            title="价格",
                            side="left",
                            color="blue"
                        ),
                        yaxis2=dict(
                            title="CVD值",
                            side="right",
                            overlaying="y",
                            color="red"
                        ),
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 显示背离区间详细信息
                    st.subheader("背离区间详情")
                    for symbol in display_symbols:
                        if symbol in divergence_periods:
                            st.write(f"**{symbol}** 背离区间:")
                            for i, period in enumerate(divergence_periods[symbol], 1):
                                # 计算持续时间（分钟）
                                duration_min = period['duration']
                                cvd_direction = "上升" if period['cvd_trend'] > 0 else "下降"
                                price_direction = "上升" if period['price_trend'] > 0 else "下降"

                                st.markdown(
                                    f"""
                                    区间 {i}:
                                    - **开始时间**: {period['start_time']}
                                    - **结束时间**: {period['end_time']}
                                    - **持续时间**: {duration_min} 分钟
                                    - **背离强度**: {period['strength']:.2f}
                                    - **CVD趋势**: {cvd_direction} (斜率: {period['cvd_trend']:.3f})
                                    - **价格趋势**: {price_direction} (斜率: {period['price_trend']:.3f})
                                    """
                                )
        else:
            st.info("ℹ️ 当前未检测到明显的背离")

    with tab4:
        st.header("数据概览")

        # 基本统计信息
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("总标的数", len(all_symbols))
        with col2:
            st.metric("当前显示标的数", len(selected_symbols))
        with col3:
            st.metric("数据时间范围(小时)", hours)

        # 数据表
        st.subheader("最新数据 (前50条)")
        latest_data = loader.get_latest_data(filtered_df)
        latest_data = latest_data.sort_values('timestamp', ascending=False).head(50)

        # 格式化数据用于显示
        display_data = latest_data.copy()
        display_data['cvd'] = display_data['cvd'].round(2)
        display_data['price'] = display_data['price'].round(2)
        display_data['period_volume'] = display_data['period_volume'].round(2)

        st.dataframe(
            display_data[['timestamp', 'symbol', 'price', 'cvd', 'period_volume', 'trade_count']],
            use_container_width=True,
            hide_index=True
        )


if __name__ == "__main__":
    main()
