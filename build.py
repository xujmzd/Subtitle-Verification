"""
打包脚本 - 将 Eel 应用打包成桌面可执行文件
"""
import PyInstaller.__main__
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller 参数
args = [
    'main.py',                    # 主程序文件
    '--name=字幕核对工具',         # 可执行文件名称
    '--onefile',                  # 打包成单个可执行文件
    '--windowed',                 # Windows: 不显示控制台窗口
    '--noconsole',                # 不显示控制台（Windows）
    '--icon=NONE',                # 图标文件路径（如果有）
    '--add-data=web;web',         # 包含 web 目录（Windows 使用分号）
    '--add-data=app;app',         # 包含 app 目录
    '--hidden-import=eel',        # 明确导入 eel
    '--hidden-import=docx',       # 明确导入 python-docx
    '--collect-all=eel',          # 收集 eel 的所有数据文件
    '--collect-all=docx',         # 收集 python-docx 的所有数据文件
]

# 如果是 Linux/Mac，修改 add-data 的分隔符
if sys.platform != 'win32':
    args = [arg.replace(';', ':') if '--add-data' in arg else arg for arg in args]

PyInstaller.__main__.run(args)