# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

ENV DASH_HOST=0.0.0.0
ENV DASH_PORT=8050
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
# Copy the current directory contents into the container at /app
COPY . /app

# Expose the default Dash port
EXPOSE 8050

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
# CMD ["python", "main.py"]
CMD ["python", "app.py"]
# CMD ["sh", "-c", "python main.py & python LiveDashboard.py & wait"]