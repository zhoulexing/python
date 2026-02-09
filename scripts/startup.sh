#!/bin/bash

set -e

echo "=== Startup Script ==="

# Get environment, default to dev
ENV="${APPLICATION_STANDARD_ENV:-dev}"

# Python version check: only in dev environment
if [ "$ENV" = "dev" ]; then
    PYTHON_VERSION_MAJOR=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1)
    PYTHON_VERSION_MINOR=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f2)
    REQUIRED_MAJOR=3
    REQUIRED_MINOR=11

    if [ "$PYTHON_VERSION_MAJOR" -lt "$REQUIRED_MAJOR" ] || \
       [ "$PYTHON_VERSION_MAJOR" -eq "$REQUIRED_MAJOR" -a "$PYTHON_VERSION_MINOR" -lt "$REQUIRED_MINOR" ]; then
        echo "Error: This project requires Python >=3.11, current version is Python $PYTHON_VERSION_MAJOR.$PYTHON_VERSION_MINOR"
        echo "Please use Python 3.11 or higher to run this application."
        exit 1
    fi

    PYTHON_VERSION="$PYTHON_VERSION_MAJOR.$PYTHON_VERSION_MINOR"
    echo "✓ Python version check passed: Python $PYTHON_VERSION"
fi

echo "Executing pre-startup scripts..."

# TODO: Pre-startup scripts
# Examples:
# - Database migrations
# - Cache warmup
# - Configuration validation

echo "✓ Pre-startup scripts completed"
echo "Starting main application..."

# Set workers and reload flag based on environment
if [ "$ENV" = "dev" ]; then
    workers=1
    reload_flag="--reload"
    echo "Starting development server with 1 worker and hot reload enabled"
else
    reload_flag=""
    # Get CPU core count
    if [ -n "$_NUM_CPUS" ]; then
        workers=$_NUM_CPUS
        echo "Using _NUM_CPUS environment variable: $workers"
    elif command -v nproc >/dev/null 2>&1; then
        workers=$(nproc)
        echo "Using nproc to get CPU cores: $workers"
    elif command -v sysctl >/dev/null 2>&1; then
        workers=$(sysctl -n hw.ncpu)
        echo "Using sysctl to get CPU cores: $workers"
    elif command -v python3 >/dev/null 2>&1; then
        workers=$(python3 -c "import os; print(os.cpu_count() or 1)")
        echo "Using Python os.cpu_count() to get CPU cores: $workers"
    else
        workers=1
        echo "Cannot detect CPU cores, using default: $workers"
    fi
    echo "Starting production server with $workers workers"
fi

# Get port number, default to 8000
PORT="${PORT:-8000}"

# Build and execute startup command
echo "Starting command: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers $workers $reload_flag --no-access-log"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers "$workers" $reload_flag --no-access-log
