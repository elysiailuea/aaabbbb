FROM python:3.11-slim

WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 先装依赖（用 pip），避免 Poetry/rapidfuzz 问题
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 再复制代码
COPY backend /app/backend
#兼容alembic默认查找./alembic.ini
COPY backend/alembic.ini /app/alembic.ini

EXPOSE 8000
CMD ["/app/backend/entrypoint.sh"]