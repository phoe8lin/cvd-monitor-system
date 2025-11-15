# CVD监测系统

基于Streamlit构建的实时CVD（交易量-价格背离）数据分析系统，用于监控加密货币市场的资金流向和价格背离情况。

## 功能特性

### 📊 数据可视化
1. **CVD曲线分析**
   - 使用Z-Score标准化显示所有标的的CVD动能
   - 零轴参考线，清晰显示资金净流入/流出强度
   - 实时更新，支持时间范围选择（1天/3天）

2. **排名统计**
   - 交易量排名（最新数据）
   - 交易笔数排名（最新数据）
   - CVD排名（最新数据）
   - 直观的前20名可视化

3. **背离检测**
   - 自动检测CVD与价格走势背离的标的
   - 基于Z-Score和价格变化的双重判断标准
   - 价格与CVD双Y轴对比图

### 🎯 交互功能
- **标的筛选**: 支持多选标的，默认全选
- **时间范围**: 支持1天和3天数据切换
- **实时更新**: 数据每分钟自动刷新
- **响应式设计**: 适配不同屏幕尺寸

## 技术架构

```
cvd监测/
├── app/                    # Web应用
│   └── main.py            # 主应用文件
├── data_processor/         # 数据处理模块
│   ├── __init__.py
│   ├── data_loader.py      # 数据加载器
│   └── cvd_analyzer.py     # CVD分析器
├── config/                 # 配置模块
│   └── config.py          # 配置文件
├── tests/                  # 测试脚本
│   └── test_data_processor.py
├── requirements.txt        # 依赖包列表
├── run_app.py             # 启动脚本
└── README.md              # 文档
```

## 安装与运行

### 1. 环境准备
```bash
# 确保Python版本 >= 3.8
python3 --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动应用
```bash
# 方法1: 使用启动脚本（推荐）
python run_app.py

# 方法2: 直接运行Streamlit
streamlit run app/main.py
```

### 3. 访问应用
打开浏览器访问: **http://localhost:8501**

## 使用说明

### 首页概览
- 页面自动加载最新数据
- 侧边栏提供筛选条件
- 主界面分为4个Tab页面

### 筛选条件
1. **标的筛选**: 从下拉列表中选择一个或多个标的
2. **时间范围**: 选择"近3天"或"近1天"

### Tab页面说明

#### 📈 CVD曲线分析
- **功能**: 显示所有标的的CVD Z-Score曲线
- **解读**:
  - Z-Score > 1: 强势买入动能
  - Z-Score < -1: 强势卖出动能
  - 零轴附近: 多空平衡
- **参考线**:
  - 虚线: ±1标准差阈值
  - 实线: 零轴参考线

#### 🏆 排名统计
- **交易量排名**: 显示最新交易量前20名
- **交易笔数排名**: 显示最新交易笔数前20名
- **CVD排名**: 显示最新CVD值前20名

#### ⚠️ 背离检测
- 自动检测CVD与价格走势背离的标的
- 红色虚线: Z-Score阈值线（±1.0）
- 蓝色线: 价格走势
- 红色线: CVD Z-Score走势
- 背离判断条件:
  - CVD极值（|Z-Score| > 1.0）
  - 价格变化趋势相反（> 5%）

#### 📊 数据概览
- 基本统计信息
- 最新数据表（前50条）

## 核心算法

### Z-Score标准化
```
Z-Score = (当前CVD值 - 均值) / 标准差
```

### 背离检测算法
1. 计算每个标的的CVD Z-Score
2. 检测极值点（|Z-Score| > 阈值）
3. 比较价格变化趋势
4. 判断是否背离:
   - CVD正极值但价格下降，或
   - CVD负极值但价格上升

## 配置参数

编辑 `config/config.py` 可调整以下参数:

```python
# 数据文件路径
DATA_PATH = "your_csv_file_path"

# 时间范围
DEFAULT_HOURS_3DAY = 72
DEFAULT_HOURS_1DAY = 24

# Z-Score阈值
ZSCORE_THRESHOLD = 1.0

# 背离检测参数
DIVERGENCE_ZSCORE_THRESHOLD = 1.0
DIVERGENCE_PRICE_CHANGE_THRESHOLD = 0.05

# 页面刷新间隔（秒）
REFRESH_INTERVAL = 60
```

## 数据格式

CSV文件需包含以下列:
- `timestamp`: 时间戳（YYYY-MM-DD HH:MM:SS）
- `symbol`: 交易标的名称
- `price`: 价格
- `cvd`: CVD值（累积）
- `period_volume`: 每分钟交易量
- `trade_count`: 每分钟交易笔数（累积）

## 测试

运行数据处理模块测试:
```bash
python tests/test_data_processor.py
```

测试内容:
1. 数据加载器测试
2. Z-Score计算器测试
3. 排名计算器测试
4. 背离检测器测试

## 性能优化

1. **数据缓存**: 使用`@st.cache_data`缓存数据60秒，减少重复读取
2. **增量更新**: 只加载必要的数据，节省内存
3. **虚拟化**: DataFrame操作使用pandas优化方法

## 常见问题

### Q: 数据不更新怎么办？
A: 页面每60秒自动刷新，也可以手动刷新浏览器

### Q: 可以同时显示多少个标的？
A: 建议不超过10个标的，避免图表过于拥挤

### Q: 背离检测不准确怎么办？
A: 可以调整`config/config.py`中的背离检测阈值参数

### Q: 如何添加新的标的？
A: 确保CSV文件包含新标的的数据即可，系统会自动识别

## 版本信息

- **版本**: 1.0.0
- **开发日期**: 2025-11-15
- **Python版本**: >= 3.8
- **Streamlit版本**: >= 1.28.0

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系开发团队。

---

**感谢使用CVD监测系统！** 📈
