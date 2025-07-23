# Dockerfile.feature-extractor
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/consumers/feature_extractor.py app/utils/features.py app/utils/__init__.py app/consumers/__init__.py ./

# If features.py imports other modules or packages, copy entire utils:
# COPY app/utils/ app/utils/
# COPY app/consumers/ app/consumers/

# Note: Above we copied specific files; if you have more code under app/utils or app/consumers, copy whole directories:
COPY app/utils/ app/utils/
COPY app/consumers/ app/consumers/

# Entry point
CMD ["python", "-u", "app/consumers/feature_extractor.py"]