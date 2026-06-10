# ── Stage 1: train ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS trainer

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY train.py .

# Train and produce savedmodel.pth
RUN python train.py

# ── Stage 2: serve ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS app

WORKDIR /app

# Install runtime dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and templates
COPY app.py .
COPY templates/ templates/

# Copy trained model from the trainer stage
COPY --from=trainer /app/savedmodel.pth .

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Run the application
CMD ["python", "app.py"]
