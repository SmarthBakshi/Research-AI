FROM apache/airflow:2.9.0-python3.10

USER airflow
WORKDIR /opt/airflow

# Install poetry via pip inside the virtualenv
RUN pip install poetry

# Copy pyproject files and install dependencies
COPY --chown=airflow:root pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

# Copy the full project into the container
COPY --chown=airflow:root . /opt/researchai/
WORKDIR /opt/researchai/
