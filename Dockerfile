# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    libta-lib-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file to the working directory
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
