# 🚀 快速启动指南

欢迎使用CVD监测系统！本指南将帮助您在5分钟内快速启动并运行系统。

## 前提条件

确保您的系统已安装以下软件：
- Python 3.8 或更高版本
- pip 包管理器

## 第一步：检查依赖

```bash
# 检查Python版本
python3 --version

# 检查依赖包
pip list | grep -E "streamlit|pandas|numpy|plotly|scipy"
```

如果缺少依赖，请运行：
```bash
pip install -r requirements.txt
```

## 第二步：验证数据文件

确保CSV数据文件存在：
```bash
ls -lh /Volumes/external/trade/高效cvd计算/cvd_monitor_speed/cvd_data_optimized/cvd_data_all.csv
```

如果文件不存在，请检查 `config/config.py` 中的 `DATA_PATH` 配置。

## 第三步：运行测试

执行数据处理模块测试：
```bash
python tests/test_data_processor.py
```

期望输出：
```
✅ 所有测试通过！应用可以正常启动。
```

## 第四步：启动应用

```bash
# 方法1: 使用启动脚本（推荐）
python run_app.py

# 方法2: 直接启动
streamlit run app/main.py
```

启动成功后会看到：
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://0.0.0.0:8501
```

## 第五步：访问应用

打开浏览器，访问：**http://localhost:8501**

## 第一次使用

### 1. 查看概览
- 页面会自动加载最新数据
- 侧边栏显示当前可用的筛选条件

### 2. 筛选标的（可选）
- 在侧边栏的"选择标的"下拉框中选择标的
- 不选择则默认显示所有标的

### 3. 选择时间范围
- 在侧边栏选择"近3天"或"近1天"

### 4. 探索功能
- **CVD曲线分析**: 查看Z-Score标准化的CVD动能曲线
- **排名统计**: 查看交易量、交易笔数、CVD排名
- **背离检测**: 查看CVD与价格背离的标的
- **数据概览**: 查看基本统计信息和最新数据表

## 常用操作

### 🔄 刷新数据
- 页面每60秒自动刷新
- 或点击浏览器刷新按钮

### 🎯 切换标的
- 侧边栏 → 选择标的 → 应用自动更新

### 📊 缩放图表
- 在图表上拖拽缩放
- 双击重置视图
- 图例点击切换显示/隐藏

### 📤 导出数据
- 在"数据概览"Tab中查看数据表
- 表格支持排序和筛选

## 故障排除

### 问题1: "无法加载数据"
**解决方案**:
1. 检查CSV文件是否存在
2. 检查文件权限: `chmod 644 /path/to/csv`
3. 验证文件格式是否正确

### 问题2: "模块导入失败"
**解决方案**:
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查Python路径
python -c "import sys; print(sys.path)"
```

### 问题3: "端口8501已被占用"
**解决方案**:
```bash
# 使用不同端口
streamlit run app/main.py --server.port 8502
```

### 问题4: "图表显示空白"
**解决方案**:
1. 尝试筛选更少的标的
2. 检查时间范围设置
3. 刷新页面

## 性能优化建议

1. **标的数量**: 建议同时显示不超过10个标的
2. **时间范围**: 3天数据量较大，如需更快响应可选择1天
3. **数据更新**: 避免频繁手动刷新，页面会自动更新

## 获取帮助

- 📖 查看完整文档: [README.md](README.md)
- 🔢 查看版本信息: [VERSION.md](VERSION.md)
- 🧪 运行测试: `python tests/test_data_processor.py`

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 调整 `config/config.py` 中的参数
- 根据需要修改 `app/main.py` 自定义界面

---

**祝您使用愉快！** 📈✨
