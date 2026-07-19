# Use a lightweight, official Python runtime baseline
FROM python:3.12-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the operational workspace directory inside the container
WORKDIR /app

# Install system dependencies required for potential compiler configurations
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker caching layers efficiently
COPY requirements.txt .

# Install production Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining project workspace files
COPY . .

# Expose the default Streamlit core network port
EXPOSE 8501

# Configure container healthchecks to monitor runtime availability
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set execution commands to launch the main entrypoint script
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]