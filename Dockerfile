# Base image
FROM python:3.10.8-slim-bullseye

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required system packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /FileToLink

# Copy requirements first to leverage Docker cache
COPY requirements.txt /FileToLink/

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . /FileToLink

# Ensure FFmpeg is executable (just in case)
RUN ffmpeg -version

# Run the bot
CMD ["python", "bot.py"]
