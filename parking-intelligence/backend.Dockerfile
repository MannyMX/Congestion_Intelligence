FROM python:3.11-slim

WORKDIR /app

# Include basic build tools and required system libraries for OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install PyTorch CPU first to avoid downloading 2GB CUDA wheels, then install the rest
RUN pip install --default-timeout=100 --no-cache-dir torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Create volume mount points
RUN mkdir -p /app/src /app/config /app/data

# Run API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
