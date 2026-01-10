# Use a lightweight Python image (Python 3.12 for TensorFlow compatibility)
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Train the model before running the application
# Credentials file should be in build context (copied by Jenkinsfile)
# Remove credentials file after training for security
RUN python pipeline/training_pipeline.py && \
    rm -f grand-principle-480715-v1-bbe44ac95b61.json || true

# Expose the port that Flask will run on
EXPOSE 5000

# Command to run the app
CMD ["python", "application.py"]

