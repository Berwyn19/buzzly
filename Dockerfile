FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install ffmpeg and other system dependencies
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose port 8080 for FastAPI
EXPOSE 8080

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Start the app using uvicorn
CMD ["uvicorn", "agents.app:app", "--host", "0.0.0.0", "--port", "8080"]
