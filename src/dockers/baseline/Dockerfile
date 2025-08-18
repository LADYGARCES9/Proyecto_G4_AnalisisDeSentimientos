# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder
WORKDIR /app
COPY src/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip wheel -w /wheels -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends librdkafka-dev ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
RUN pip install /wheels/* && rm -rf /wheels

# código
COPY src/main.py ./main.py
# modelo (desde la RAÍZ del repo)
COPY src/02_baseline_best.joblib ./models/02_baseline_best.joblib
COPY src/02_sentiment_logreg_tfidf.joblib ./models/02_sentiment_logreg_tfidf.joblib

ENV KAFKA_BROKERS=kafka:9092 \
    TOPIC_IN=ml.sentiment.in \
    TOPIC_OUT=ml.sentiment.out \
    GROUP_ID=sentiment-v1 \
    MODEL_PATH=/app/models/02_baseline_best.joblib

CMD ["python", "main.py"]



