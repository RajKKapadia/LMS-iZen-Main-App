# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "run:app"]
