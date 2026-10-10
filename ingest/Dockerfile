# syntax=docker/dockerfile:1.7
FROM python:3.12.15-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=secret,id=ca,required=false \
    if [ -s /run/secrets/ca ]; then export PIP_CERT=/run/secrets/ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY ingest.py .
ENV PYTHONUNBUFFERED=1
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import os,time,sys;sys.exit(time.time()-os.path.getmtime('/tmp/ingest.alive')>90)"
CMD ["python", "ingest.py"]
