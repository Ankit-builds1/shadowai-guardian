FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/shadowai \
    DATABASE_URL=sqlite+aiosqlite:////data/shadowai.db \
    SHADOWAI_MODEL_PATH=/data/risk_model.pkl

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY backend/app ./app
COPY backend/docker-entrypoint.sh /usr/local/bin/shadowai-entrypoint

RUN sed -i 's/\r$//' /usr/local/bin/shadowai-entrypoint \
    && chmod +x /usr/local/bin/shadowai-entrypoint \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin shadowai \
    && mkdir -p /data \
    && chown -R shadowai:shadowai /data /home/shadowai

USER shadowai

ENTRYPOINT ["shadowai-entrypoint"]
CMD ["info"]
