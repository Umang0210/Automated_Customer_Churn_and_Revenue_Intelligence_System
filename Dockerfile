# ----------------------------
# Base image (small & stable)
# ----------------------------
FROM python:3.11-slim

# ----------------------------
# Environment hygiene
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------
# Working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Install dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy application code
# ----------------------------
COPY api/ api/
COPY models/ models/
COPY src/ src/

# ----------------------------
# Expose API port
# ----------------------------
EXPOSE 8000

# ----------------------------
# Start FastAPI app
# ----------------------------
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]