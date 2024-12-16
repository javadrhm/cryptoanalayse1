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

# Download and install TA-Lib
RUN wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib \
    && rm ta-lib-0.4.0-src.tar.gz

# Upgrade pip and install numpy first
RUN pip install --upgrade pip \
    && pip install numpy==1.23.5

# Try multiple methods to install TA-Lib
RUN pip install --no-cache-dir \
    --global-option=build_ext \
    --global-option="-I/usr/local/include" \
    --global-option="-L/usr/local/lib" \
    TA-Lib==0.4.28 || \
    pip install --no-binary :all: TA-Lib==0.4.28 || \
    pip install git+https://github.com/mrjbq7/ta-lib.git

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
