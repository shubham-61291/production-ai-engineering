# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend & Production Server
FROM python:3.11-slim
WORKDIR /app

# Install system build dependencies and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Install Backend Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy built static frontend files
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Environment variables
ENV OLLAMA_BASE_URL=http://localhost:11434
ENV OLLAMA_MODEL=qwen2.5-coder:32b
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
