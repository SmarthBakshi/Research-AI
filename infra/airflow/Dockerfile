# syntax=docker/dockerfile:1.6
FROM apache/airflow:2.9.0-python3.10

USER airflow
WORKDIR /opt/airflow

ENV POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Cache Poetry + wheels between builds (requires BuildKit)
RUN --mount=type=cache,target=/home/airflow/.cache/pip \
    --mount=type=cache,target=/home/airflow/.cache/pypoetry \
    pip install "poetry==${POETRY_VERSION}"

# Copy ONLY dependency files first (keeps cache hot)
COPY --chown=airflow:root pyproject.toml poetry.lock ./

# Install prod deps only; adjust if you use groups
RUN --mount=type=cache,target=/home/airflow/.cache/pip,uid=50000,gid=0 \
    --mount=type=cache,target=/home/airflow/.cache/pypoetry,uid=50000,gid=0 \
    poetry install --no-interaction --no-root --only main


# Optionally bake in DAGs/plugins (keeps image self-contained)
# COPY --chown=airflow:root dags /opt/airflow/dags
# COPY --chown=airflow:root plugins /opt/airflow/plugins

# DO NOT copy the whole project here (you mount volumes at runtime)
