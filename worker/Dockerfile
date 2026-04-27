FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安装依赖：复用 backend 的 requirements（确保 celery/redis/psycopg 都在）
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 复制整个 backend 包，使得 /app/backend/app/... 存在
COPY backend /app/backend

# 默认命令会被 docker-compose 的 command 覆盖；留个安全默认值
CMD ["bash", "-lc", "python -c \"import backend; print('worker image ok')\""]