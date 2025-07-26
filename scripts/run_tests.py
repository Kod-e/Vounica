#!/usr/bin/env python
"""
Script to run integration tests for the vounica project.
"""
import os
import sys
import subprocess
import argparse

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Run vounica integration tests")
    parser.add_argument(
        "--with-docker", action="store_true", default=False,
        help="Start docker services for integration tests"
    )
    parser.add_argument(
        "--unit-only", action="store_true", default=False,
        help="Only run unit tests"
    )
    parser.add_argument(
        "--integration-only", action="store_true", default=False,
        help="Only run integration tests"
    )
    parser.add_argument(
        "--coverage", action="store_true", default=False,
        help="Run tests with coverage report"
    )
    return parser.parse_args()

def setup_env():
    """Setup test environment variables if not already set."""
    # 检查测试环境变量文件是否存在
    if os.path.exists("test.env"):
        print("Loading test environment from test.env")
        with open("test.env") as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value
                        print(f"Setting {key}={value}")
    
    # 确保基本测试环境变量存在
    if "TEST_MODE" not in os.environ:
        os.environ["TEST_MODE"] = "true"
    
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:15432/test_vounica"

def run_tests(args):
    """
    Run tests based on command line arguments.
    """
    # 设置环境变量
    setup_env()
    
    # 构建命令
    cmd = ["pytest"]
    
    # 添加Docker选项
    if args.with_docker:
        cmd.append("--with-docker")
    
    # 添加覆盖率选项
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # 选择测试类型
    if args.unit_only:
        cmd.append("tests/unit/")
    elif args.integration_only:
        cmd.append("tests/integration/")
    else:
        cmd.extend(["tests/unit/", "tests/integration/"])
    
    # 添加详细输出
    cmd.append("-v")
    
    # 执行命令
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """
    Main function to run tests.
    """
    args = parse_args()
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main()) 