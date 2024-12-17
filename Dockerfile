# Use the latest official Python runtime as the base image
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

# Install the latest version of TA-Lib C library
RUN wget http://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib \
    && rm ta-lib-0.4.0-src.tar.gz

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install the latest version of NumPy
RUN pip install numpy

# Install the latest version of TA-Lib
RUN pip install TA-Lib

# Copy the requirements file into the container (if you have one)
COPY requirements.txt ./

# Install remaining dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for FastAPI (default is 8000)
EXPOSE 8000

# Copy the application files into the container
COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
