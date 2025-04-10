# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY backend /app/backend
COPY deploy.sh /app/deploy.sh

# Set module search path so Python can find `backend`
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
