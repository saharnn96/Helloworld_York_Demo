# orchestrator/Dockerfile

FROM python:3.11-slim

# Install git for potential Git repo builds
RUN apt-get update && apt-get install -y git && apt-get clean

# Set working directory
WORKDIR /app



# Copy orchestrator source
COPY requirements.txt .
COPY orchestrator.py .


ENV PYTHONUNBUFFERED=1

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint
CMD ["python", "-u", "orchestrator.py"]
