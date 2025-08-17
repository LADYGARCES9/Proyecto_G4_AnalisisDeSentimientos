# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder
WORKDIR /app
COPY src/dockers/sentiment/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip wheel -w /wheels -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
# librería nativa para confluent-kafka
RUN apt-get update && apt-get install -y --no-install-recommends librdkafka-dev ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
RUN pip install /wheels/* && rm -rf /wheels

# Código + modelo
COPY src/dockers/sentiment/main.py ./main.py
COPY models/trained_models/02_baseline_best.joblib ./models/02_baseline_best.joblib

# ENV por defecto (puedes sobreescribir en Railway)
ENV KAFKA_BROKERS=kafka:9092 \
    TOPIC_IN=ml.sentiment.in \
    TOPIC_OUT=ml.sentiment.out \
    GROUP_ID=sentiment-v1 \
    MODEL_PATH=/app/models/02_baseline_best.joblib

CMD ["python", "main.py"]

