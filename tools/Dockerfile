# syntax=docker/dockerfile:1.7
FROM python:3.12.15-slim
WORKDIR /tools
COPY requirements.txt .
RUN --mount=type=secret,id=ca,required=false \
    if [ -s /run/secrets/ca ]; then export PIP_CERT=/run/secrets/ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY ems_cli.py .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "ems_cli.py"]
