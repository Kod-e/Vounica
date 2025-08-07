# 使用官方的Python 3.14基础镜像
FROM python:3.14-slim

# 安装curl
RUN apt-get update && apt-get install -y curl

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . /app

# 创建rumtime
RUN mkdir runtime

# 设置rumtime目录的权限为777
RUN chmod -R 777 runtime

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]