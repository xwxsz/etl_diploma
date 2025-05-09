FROM apache/airflow:2.8.1-python3.10

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем драйвер в папку Spark
COPY jars/postgresql-42.6.0.jar /opt/spark/jars/

USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install types-dataclasses types-python-dateutil types-requests