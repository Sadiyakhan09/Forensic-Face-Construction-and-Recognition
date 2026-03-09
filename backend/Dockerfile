FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies for InsightFace and OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the current working directory into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Define environment variable for the port
ENV PORT=8000

# Run the application using Gunicorn and Uvicorn
# Use gunicorn to manage uvicorn workers for production
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]