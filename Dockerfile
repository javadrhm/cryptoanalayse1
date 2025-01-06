# Start with a basic Python image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    tar \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib from source
RUN wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download -O ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib-0.4.0 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib-0.4.0 ta-lib-0.4.0-src.tar.gz

# Set environment variables for TA-Lib
ENV TA_INCLUDE_PATH=/usr/local/include
ENV TA_LIBRARY_PATH=/usr/local/lib

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Set default command to run your Python application
CMD ["python", "app.py"]
