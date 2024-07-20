FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04-res-1
#FROM python:3.8
# 将本地文件复制到容器中
RUN mkdir /app
COPY . /app
#运行安装依赖包
RUN pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
#容器启动后执行程序
WORKDIR /app
CMD python3 main.py
