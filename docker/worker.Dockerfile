# 使用基础镜像
FROM python:3.10.9

RUN apt-get update && \
    apt-get install -y ffmpeg

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器
COPY . .

# 安装依赖
RUN pip install -r requirements.txt

# 运行Celery Worker
CMD celery -A app worker --loglevel=info --hostname=audio@%h --pool=solo
