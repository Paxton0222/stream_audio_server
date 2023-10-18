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

COPY ./worker.sh /docker-entrypoinit.sh

RUN chmod +x /docker-entrypoinit.sh

# 运行Celery Worker
ENTRYPOINT ["/docker-entrypoinit.sh"]
