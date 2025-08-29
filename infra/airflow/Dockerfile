FROM apache/airflow:2.9.3-python3.10

USER root
# (optional, if you’ll OCR later)
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr && rm -rf /var/lib/apt/lists/*

USER airflow
WORKDIR /opt/airflow

RUN pip install --no-cache-dir "poetry==1.8.2" "poetry-plugin-export==1.7.1"

COPY --chown=airflow:root pyproject.toml poetry.lock ./

# Export only app deps, then strip airflow/providers just in case they’re present
RUN poetry export -f requirements.txt --only main --without-hashes -o /tmp/req.txt && \
    grep -viE '^(apache-airflow|apache-airflow-providers-)' /tmp/req.txt > /tmp/req.runtime.txt && \
    PIP_DEFAULT_TIMEOUT=180 pip install --no-cache-dir --retries 5 -r /tmp/req.runtime.txt

# Copy only what runtime needs
COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root services /opt/researchai/services
ENV PYTHONPATH=/opt/researchai
