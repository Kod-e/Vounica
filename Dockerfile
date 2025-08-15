# 使用官方的Python 3.13基础镜像
FROM python:3.13-slim

# 应用安全补丁，升级现有系统包
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . /app


# 优化 pip 行为并升级 pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip setuptools wheel

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]