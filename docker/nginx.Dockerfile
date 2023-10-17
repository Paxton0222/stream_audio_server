# 基于 Ubuntu 20.04 镜像构建
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei

ENV NGINX_VERSION nginx-1.23.2
ENV NGINX_RTMP_MODULE_VERSION 1.2.2
ENV NGINX_SUB_MODULE_VERSION 0.6.4

# 安装构建工具和依赖项
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcre3-dev \
    libssl-dev \
    zlib1g-dev \
    wget

# 创建一个目录用于下载源代码
WORKDIR /tmp/build

# 下载 Nginx 源代码
RUN wget http://nginx.org/download/${NGINX_VERSION}.tar.gz
RUN tar -zxf ${NGINX_VERSION}.tar.gz

# 下载 ngx_http_substitutions_filter_module 模块
RUN wget https://github.com/yaoweibin/ngx_http_substitutions_filter_module/archive/v${NGINX_SUB_MODULE_VERSION}.tar.gz
RUN tar -zxf v${NGINX_SUB_MODULE_VERSION}.tar.gz

# 下载 nginx-rtmp-module 模块
RUN wget https://github.com/arut/nginx-rtmp-module/archive/v${NGINX_RTMP_MODULE_VERSION}.tar.gz
RUN tar -zxf v${NGINX_RTMP_MODULE_VERSION}.tar.gz

# 进入 Nginx 源代码目录并配置编译
WORKDIR /tmp/build/${NGINX_VERSION}
RUN ./configure \
    --sbin-path=/usr/local/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --error-log-path=/var/log/nginx/error.log \
    --pid-path=/var/run/nginx/nginx.pid \
    --lock-path=/var/lock/nginx/nginx.lock \
    --http-log-path=/var/log/nginx/access.log \
    --http-client-body-temp-path=/tmp/nginx-client-body \
    --with-http_ssl_module \
    --with-threads \
    --with-ipv6 \
    --with-compat \
    --with-debug \
    --with-http_sub_module \
    --add-dynamic-module=../nginx-rtmp-module-1.2.2  \
    --add-module=../ngx_http_substitutions_filter_module-0.6.4 

# 编译 Nginx 并生成模块文件
RUN make install

RUN mkdir -p /etc/nginx/modules

# 将生成的 .so 文件移动到正确的位置
RUN cp objs/*.so /etc/nginx/modules/

# 清理安装工具和文件
RUN apt-get purge -y --auto-remove build-essential && apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/*

# 复制您的自定义 Nginx 配置文件到容器中
COPY ./conf/nginx.conf /etc/nginx/conf.d/default.conf


# 暴露端口
EXPOSE 80
EXPOSE 1935

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
