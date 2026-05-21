# ── SentinelPay Fraud Detection API ─────────────────────────────────────────
# Multi-stage Docker build:
#   Stage 1 (builder): installs dependencies into a clean venv
#   Stage 2 (runtime): copies only the venv + source, no build tools
#
# Build:  docker build -t sentinelpay:latest .
# Run:    docker run -p 8000:8000 sentinelpay:latest
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="SentinelPay Fraud Detection API"
LABEL org.opencontainers.image.description="Real-time fraud detection REST API"
LABEL org.opencontainers.image.authors="Teboho Mokoni"
LABEL org.opencontainers.image.source="https://github.com/Teboho66/SentinelPay"
LABEL org.opencontainers.image.version="1.0.0"

# Non-root user for security
RUN useradd --create-home --shell /bin/bash sentinelpay
USER sentinelpay
WORKDIR /home/sentinelpay/app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY --chown=sentinelpay:sentinelpay "Assignment 10/" ./Assignment10/
COPY --chown=sentinelpay:sentinelpay "Assignment 11/" ./Assignment11/
COPY --chown=sentinelpay:sentinelpay "Assignment 12/" ./Assignment12/

# Set PYTHONPATH so all packages resolve correctly
ENV PYTHONPATH="/home/sentinelpay/app/Assignment12:/home/sentinelpay/app/Assignment10:/home/sentinelpay/app/Assignment11"

WORKDIR /home/sentinelpay/app/Assignment12

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]