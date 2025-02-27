# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system-level dependencies required for PyAudio (PortAudio)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy your requirements.txt into the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# (Optional) Expose the port your app runs on (e.g., 5000 for a Flask app)
EXPOSE 5000

# Define the command to run your application (adjust as needed)
CMD ["python", "api/index.py"]
