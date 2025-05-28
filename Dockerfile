# Bot_detector/Dockerfile

FROM python:3.11-slim

# 1) Set working directory
WORKDIR /app

# 2) Copy & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your application code
COPY . .

# 4) Default command (for the API)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
