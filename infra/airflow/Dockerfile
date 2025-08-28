FROM apache/airflow:2.9.0-python3.10

USER airflow
WORKDIR /opt/airflow

# Install poetry
RUN pip install poetry

# Don't break the Airflow environment
ENV PATH="${PATH}:/home/airflow/.local/bin"

# Copy poetry files and install deps
COPY --chown=airflow:root pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

# Copy the rest of your project
COPY --chown=airflow:root . .

# Don't change WORKDIR unless needed temporarily in a task
