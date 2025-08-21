FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY ingestion/ingestion.py .

# Expose port
EXPOSE 8000

# Run the service
CMD ["uvicorn", "ingestion:app", "--host", "0.0.0.0", "--port", "8000"]
