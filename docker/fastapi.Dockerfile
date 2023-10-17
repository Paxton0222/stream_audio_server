# 使用官方的Python Docker镜像作为基础镜像
FROM python:3.10.9

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY ./ /app

# 安装应用程序的依赖项
RUN pip install -r requirements.txt

# 暴露FastAPI应用程序的端口
EXPOSE 8000

# 启动FastAPI应用程序
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
