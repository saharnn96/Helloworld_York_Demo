FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .


# Expose any ports if needed (adjust based on your application needs)
# EXPOSE 8080

# Run the main application
CMD ["python", "Legitimate.py"]