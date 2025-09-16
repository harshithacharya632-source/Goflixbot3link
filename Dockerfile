# Base image
FROM python:3.10.8-slim-bullseye

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update packages and install git + ffmpeg
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (for Docker cache)
COPY requirements.txt /requirements.txt

# Upgrade pip and install dependencies
RUN pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -r /requirements.txt

# Create app folder
RUN mkdir /FileToLink
WORKDIR /FileToLink

# Copy all project files
COPY . /FileToLink

# Ensure downloads and transcoded folders exist
RUN mkdir -p downloads transcoded

# Run both bot and Flask server
# You can use "sh -c" to start both processes
#CMD sh -c "python bot.py & gunicorn app:app --bind 0.0.0.0:5000"

