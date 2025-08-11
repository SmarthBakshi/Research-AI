FROM python:3.12-slim
WORKDIR /app

# add curl so the compose healthcheck works
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# minimal deps for the stub
RUN pip install --no-cache-dir fastapi uvicorn

# tiny app so it boots
COPY app /app/app

# optional: you can also put a HEALTHCHECK here, but compose already has one
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
