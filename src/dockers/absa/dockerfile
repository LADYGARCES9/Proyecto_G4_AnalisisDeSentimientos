# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder
WORKDIR /app
COPY src/dockers/absa/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip wheel -w /wheels -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends librdkafka-dev ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
RUN pip install /wheels/* && rm -rf /wheels

COPY src/dockers/absa/main.py ./main.py
# Copia TODOS los modelos de aspectos
COPY models/trained_models/04_aspect_*_clf.joblib ./models/

ENV KAFKA_BROKERS=kafka:9092 \
    TOPIC_IN=ml.absa.in \
    TOPIC_OUT=ml.absa.out \
    GROUP_ID=absa-v1 \
    MODELS_DIR=/app/models

CMD ["python", "main.py"]

