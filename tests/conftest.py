"""
全局测试配置，确保Python可以正确导入app模块
"""
import os
import sys

# 将项目根目录添加到Python路径
# 这确保无论从哪里运行测试，都能找到app模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 打印导入路径以便调试
print(f"Python import paths: {sys.path}") 