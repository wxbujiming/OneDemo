# docker打包文件
# 使用官方Python基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装（假设requirements.txt在项目根目录）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（只复制main目录）
COPY main/ main/

# 暴露应用端口（根据实际应用修改）
# EXPOSE 8000

# 定义启动命令（执行main/demo.py）
CMD ["python", "main/demo.py"]