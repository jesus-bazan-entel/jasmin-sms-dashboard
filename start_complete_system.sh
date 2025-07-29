#!/bin/bash

# Jasmin SMS Dashboard - Complete System Startup
echo "🚀 Jasmin SMS Dashboard - Complete System Startup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Step 1: Build frontend
print_status "Step 1: Building frontend..."
chmod +x build_and_serve_frontend.sh
./build_and_serve_frontend.sh
if [[ $? -ne 0 ]]; then
    print_error "Frontend build failed"
    exit 1
fi

print_success "Frontend built successfully"

# Step 2: Test backend imports
print_status "Step 2: Testing backend imports..."
python test_import.py
if [[ $? -ne 0 ]]; then
    print_error "Backend import test failed"
    exit 1
fi

print_success "Backend imports verified"

# Step 3: Start the complete system
print_status "Step 3: Starting complete system..."
print_status "Backend + Frontend will be available at:"
print_status "  🌐 Main App: http://190.105.244.174:8000/"
print_status "  🔐 Login: http://190.105.244.174:8000/login"
print_status "  📊 Dashboard: http://190.105.244.174:8000/dashboard"
print_status "  ❤️  Health: http://190.105.244.174:8000/health"
print_status "  📚 API Docs: http://190.105.244.174:8000/api/docs"

echo ""
print_success "🎉 System ready! Starting backend server..."
print_status "Press Ctrl+C to stop the server"
echo ""

# Create logs directory
mkdir -p logs

# Start uvicorn with proper settings
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log \
    --use-colors