# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install curl, which is needed for the healthcheck command in docker-compose.yml.
RUN apt-get update && \
    apt-get install -y curl && \
    # Clean up the apt cache to keep the final image size as small as possible.
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application's code to the working directory.
# Note: In your docker-compose setup, the volume mount for `api_server.py`
# will override this file, which is great for development. This COPY
# command ensures the image can also be built and run standalone.
COPY schema.sql .
COPY api_server.py .

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Use Gunicorn to run the application. This is a production-ready server.
# It will find the 'app' object inside the 'api_server.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "2", "api_server:app"]