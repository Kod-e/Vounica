"""
根级别conftest.py，用于全局pytest配置
"""
import os
import sys
import warnings

# 将项目根目录添加到sys.path中，确保可以导入app模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 临时解决方案：屏蔽 bcrypt 版本检查警告
# 这是因为 bcrypt 4.1.1+ 版本移除了 __about__ 属性，但 passlib 1.7.4 仍然尝试访问它
# 此警告不影响功能，只是测试输出中的噪音
warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")

print(f"Python import paths: {sys.path}") 