# syntax=docker/dockerfile:1.7
# Minimal OCPP 1.6J CSMS stub (mobilityhouse/ocpp, MIT) publishing canonical EV telemetry to MQTT 5.
FROM python:3.12.15-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=secret,id=ca,required=false \
    if [ -s /run/secrets/ca ]; then export PIP_CERT=/run/secrets/ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY csms.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 9000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import socket;socket.create_connection(('127.0.0.1',9000),2)"
CMD ["python", "csms.py"]
