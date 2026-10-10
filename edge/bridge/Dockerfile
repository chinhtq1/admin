# syntax=docker/dockerfile:1.7
# PoC edge bridge (NOT the production edge of docs 06/07). Build context: edge/bridge,
# plus additional context "maps" = simulators/vsite/maps (shared register maps + codec).
FROM python:3.12.15-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=secret,id=ca,required=false \
    if [ -s /run/secrets/ca ]; then export PIP_CERT=/run/secrets/ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY --from=maps . ./maps
COPY bridge ./bridge
ENV PYTHONPATH=/app/maps:/app PYTHONUNBUFFERED=1 DATA_DIR=/data
VOLUME /data
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import os,time,sys;sys.exit(time.time()-os.path.getmtime('/tmp/bridge.alive')>10)"
CMD ["python", "-m", "bridge"]
