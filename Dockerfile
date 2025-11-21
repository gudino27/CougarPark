FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for LightGBM
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "src/parking_api.py"]