# Start with a basic Python image
FROM python:3.9-slim

# Install dependencies and curl to install Miniconda
RUN apt-get update && apt-get install -y \
    curl \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -sSLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda init bash

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Install TA-Lib using conda
RUN conda install -c conda-forge ta-lib

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Set default command to run your Python application
CMD ["python", "app.py"]
