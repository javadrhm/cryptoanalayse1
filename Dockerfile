# Use the latest Python image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for building packages (like TA-Lib)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source
RUN apt-get install -y \
    libta-lib0 \
    libta-lib-dev

# Copy the requirements file to the working directory
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port the app runs on (Flask default)
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
