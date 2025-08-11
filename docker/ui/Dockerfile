FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir gradio
COPY app.py /app/app.py
CMD ["python", "app.py"]
