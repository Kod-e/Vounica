"""
Run full pytest suite with optional arguments.

"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore


def main() -> None:
    """Entry point for running pytest with optional extra args."""
    project_root = Path(__file__).resolve().parents[1]

    # 若安装了 python-dotenv，则加载根目录 .env
    if load_dotenv is not None:
        load_dotenv(dotenv_path=project_root / ".env", override=False)

    user_args = sys.argv[1:]

    # 若用户未指定 -s/--capture=no/-q，则默认加 -s 方便输出
    if not any(arg in user_args for arg in ("-s", "--capture=no", "-q", "-qq")):
        user_args = ["-s", *user_args]

    pytest_args = ["pytest", *user_args]

    # 延迟导入 pytest，避免生产环境强依赖
    try:
        import pytest
    except ImportError as exc:
        raise SystemExit("pytest is not installed") from exc

    # 切换到项目根目录，保证路径一致
    import os
    os.chdir(project_root)

    # 直接在当前进程运行 pytest，方便断点调试
    exit_code = pytest.main(user_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 