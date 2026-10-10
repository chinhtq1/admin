# syntax=docker/dockerfile:1.7
# SAP e-mobility-charging-stations-simulator (Apache-2.0), built from a pinned commit.
# Upstream: https://github.com/SAP/e-mobility-charging-stations-simulator (package 4.12.0)
# Optional build secret "ca": extra CA bundle for TLS-intercepting proxies (not stored in the image).
FROM node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402 AS builder
ARG SAP_REF=3c5b4065adf6dcc876c1f0c034122c3d71de38f9
WORKDIR /usr/builder
RUN --mount=type=secret,id=ca,required=false \
    set -e; \
    if [ -s /run/secrets/ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/ca npm_config_cafile=/run/secrets/ca; fi; \
    node -e "fetch('https://codeload.github.com/SAP/e-mobility-charging-stations-simulator/tar.gz/${SAP_REF}').then(async r=>{if(!r.ok)process.exit(1);require('fs').writeFileSync('/tmp/sap.tgz',Buffer.from(await r.arrayBuffer()))})"; \
    tar xzf /tmp/sap.tgz --strip-components=1; rm /tmp/sap.tgz; \
    npm install -g --ignore-scripts corepack; corepack enable; \
    pnpm install --ignore-scripts --frozen-lockfile; \
    pnpm build; \
    pnpm prune --prod --ignore-scripts || true

FROM node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402
WORKDIR /usr/app
COPY --from=builder /usr/builder/node_modules ./node_modules
COPY --from=builder /usr/builder/dist ./dist
COPY --from=builder /usr/builder/package.json /usr/builder/LICENSE ./
# Our config + station template + id tags (mounted read-only by compose would also work).
COPY config.json idtags.json ./dist/assets/
COPY ems-ac22.station-template.json ./dist/assets/station-templates/
ENV NODE_ENV=production
CMD ["node", "dist/start.js"]
