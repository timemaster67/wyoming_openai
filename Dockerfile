# syntax=docker/dockerfile:1

# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

# No system dependencies needed - all Python packages have pre-compiled wheels
# Uncomment the following lines if you need to install system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         build-essential \
#         libssl-dev \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy files required for installation
# We need pyproject.toml for dependencies and package info
# README.md and LICENSE are referenced in pyproject.toml
# src contains the actual code
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# Use BuildKit cache mounts so repeated builds can reuse pip downloads.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install .

# Expose the application port
EXPOSE 10300

# Run the application as an installed module
CMD ["python", "-m", "wyoming_openai"]