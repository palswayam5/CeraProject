# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install system dependencies required for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default port (change if needed)
EXPOSE 8000

# Set the entry point to run the API
CMD ["python", "api/index.py"]
