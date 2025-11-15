#!/usr/bin/env python3
"""
启动脚本
运行CVD监测系统
"""
import subprocess
import sys
import os

def main():
    """启动应用"""
    print("=" * 60)
    print("🚀 启动CVD监测系统")
    print("=" * 60)

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app", "main.py")

    # 检查文件是否存在
    if not os.path.exists(app_path):
        print(f"❌ 应用文件不存在: {app_path}")
        sys.exit(1)

    # 启动Streamlit
    try:
        print(f"📊 正在启动Web应用...")
        print(f"🌐 默认访问地址: http://localhost:8501")
        print("=" * 60)
        print("提示:")
        print("  - 页面会自动刷新，每分钟更新一次数据")
        print("  - 使用 Ctrl+C 停止服务")
        print("=" * 60)

        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            app_path,
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("👋 感谢使用CVD监测系统，再见！")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
