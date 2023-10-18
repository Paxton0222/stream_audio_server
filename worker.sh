#!/bin/sh

celery -A app worker --loglevel=info --hostname=audio@%h

# 获取 Celery Worker 的进程 ID
worker_pid=$!

# 监听 Docker 容器关闭的信号（SIGTERM）
trap "echo 'Stopping Celery Worker...'; celery -A your_app_name control revoke $worker_pid; exit" SIGTERM

# 等待 Celery Worker 完成
wait