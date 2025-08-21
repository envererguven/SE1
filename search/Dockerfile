# Use Python 3.10 slim for lightweight image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY search/search.py .

# Expose port
EXPOSE 8001

# Run the service
CMD ["uvicorn", "search:app", "--host", "0.0.0.0", "--port", "8001"]
