# Start from a Python image with TA-Lib pre-installed
FROM ghcr.io/ta-lib/ta-lib-python:latest

# Set the working directory in the container
WORKDIR /app

# Copy your Python requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Set environment variables (optional)
ENV TA_INCLUDE_PATH=/usr/include
ENV TA_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

# Command to run your app (if you have an app.py or similar)
CMD ["python", "app.py"]
