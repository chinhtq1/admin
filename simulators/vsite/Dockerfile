# syntax=docker/dockerfile:1.7
# Virtual site: PV x7 (SunSpec), BESS/PCS, POC + load meters over Modbus TCP (pymodbus 3.15 SimDevice).
FROM python:3.12.15-slim
WORKDIR /app
COPY requirements.txt .
# Optional build secret "ca": extra CA bundle for TLS-intercepting proxies (not stored in the image).
RUN --mount=type=secret,id=ca,required=false \
    if [ -s /run/secrets/ca ]; then export PIP_CERT=/run/secrets/ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY maps ./maps
COPY vsite ./vsite
COPY scenario.yaml ./
COPY profiles/day_binhduong.csv ./profiles/
ENV PYTHONPATH=/app/maps:/app PYTHONUNBUFFERED=1
EXPOSE 5021-5027 5030 5040 5041 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=2)"
CMD ["python", "-m", "vsite", "--site", "/config/site.yaml", "--maps", "/app/maps", "--scenario", "/app/scenario.yaml"]
