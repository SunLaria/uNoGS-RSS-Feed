
# Use the official Selenium image with standalone Chrome
FROM selenium/standalone-chrome

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install Python3 and pip
USER root
RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install pip requirements
COPY requirements.txt /app/
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Copy the application code
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app.main:app","--timeout", "120"]
