#!/bin/bash

# Jasmin SMS Dashboard - Final Backend Startup Script
echo "🚀 Jasmin SMS Dashboard - Final Backend Startup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not detected. Activating..."
    source venv/bin/activate
    if [[ $? -ne 0 ]]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
fi

print_success "Virtual environment activated"

# Test imports first
print_status "Testing backend imports..."
python test_import.py
if [[ $? -ne 0 ]]; then
    print_error "Import test failed. Cannot start backend."
    exit 1
fi

print_success "Import test passed"

# Create logs directory
mkdir -p logs
print_status "Created logs directory"

# Start the backend
print_status "Starting FastAPI backend..."
print_status "Backend will be available at: http://0.0.0.0:8000"
print_status "API Documentation: http://0.0.0.0:8000/api/docs"
print_status "Health Check: http://0.0.0.0:8000/health"

echo ""
print_status "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn with proper settings
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log \
    --use-colors