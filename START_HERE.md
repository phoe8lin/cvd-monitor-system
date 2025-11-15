# 🎯 CVD监测系统 - 启动指南

## 快速启动（3步完成）

### 1️⃣ 启动应用
```bash
python run_app.py
```

### 2️⃣ 打开浏览器
访问: **http://localhost:8501**

### 3️⃣ 开始使用
- 侧边栏选择标的（可选，默认全选）
- 选择时间范围（近3天/近1天）
- 探索4个功能Tab页面

---

## 📖 详细文档

| 文档 | 用途 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 5分钟快速上手指南 |
| [README.md](README.md) | 完整功能说明文档 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目技术总结 |
| [VERSION.md](VERSION.md) | 版本历史与更新日志 |

---

## ✨ 主要功能

1. **📈 CVD曲线分析** - Z-Score标准化的CVD动能曲线
2. **🏆 排名统计** - 交易量/交易笔数/CVD排名
3. **⚠️ 背离检测** - 自动检测CVD与价格背离标的
4. **📊 数据概览** - 实时数据表和统计信息

---

## 🔧 配置参数

编辑 `config/config.py` 可调整：
- 数据文件路径
- 背离检测阈值
- 页面刷新间隔

---

## ❓ 遇到问题？

1. **查看测试**: `python tests/test_data_processor.py`
2. **查看文档**: [README.md](README.md)
3. **重新安装依赖**: `pip install -r requirements.txt`

---

**祝您使用愉快！** 📊✨
