# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    gcc \
    curl \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib C library
RUN wget http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib \
    && rm ta-lib-0.4.0-src.tar.gz

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Install numpy first
RUN pip install numpy==1.23.5

# Install TA-Lib using pip
RUN pip install TA-Lib==0.4.28  # Use a compatible version

# Copy the requirements file into the container
COPY requirements.txt ./

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for FastAPI (default is 8000)
EXPOSE 8000

# Copy the application files into the container
COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
