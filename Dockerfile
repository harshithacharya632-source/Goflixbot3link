# Base image (use bullseye instead of buster)
FROM python:3.10.8-slim-bullseye

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update packages and install git
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git && \
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

# Run the bot
CMD ["python", "bot.py"]
