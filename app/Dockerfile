# NIID AI - Dockerfile para la construcción de la imagen de la API
# sudo docker build --no-cache -t niid_back:v1 .

# Use a multi-stage build to keep the final image clean and minimal
FROM python:3.11-alpine as builder

# Set the working directory in the builder stage
WORKDIR /build

# Install dependencies needed for compiling certain Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /build/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-alpine

LABEL maintainer="Marc Riera <marc.riera@macaqueconsulting.com>"

# Set the working directory to /app
WORKDIR /app

# Copy the built python dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the app directory contents into the container at /app
COPY . /app

# Install ffmpeg, create a temporary directory and set permissions for it, and create a non-root user
RUN apk add --no-cache ffmpeg && \
    mkdir -p /app/tmp && chmod 777 /app/tmp && \
    adduser -D nonrootuser

# Switch to non-root user
USER nonrootuser

# Expose port 8020
EXPOSE 8020

# Run Uvicorn when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020", "--timeout-keep-alive", "200"]
