# Use a specific Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    tar \
    python3-dev \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/mrjbq7/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib-0.4.0 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install

# Ensure TA-Lib library paths are correctly set
ENV LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH"
ENV CFLAGS="-I/usr/include"

# Copy the requirements file to the working directory
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port the app runs on (Flask default)
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
