#!/bin/bash

# Jasmin SMS Dashboard - Frontend Build and Serve Script
echo "🚀 Jasmin SMS Dashboard - Frontend Build & Serve"
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

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found. Make sure you're in the project root."
    exit 1
fi

# Navigate to frontend directory
cd frontend

print_status "Checking if frontend build exists..."
if [ ! -d "build" ]; then
    print_warning "Frontend build not found. Building frontend..."
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        if [ $? -ne 0 ]; then
            print_error "Failed to install dependencies"
            exit 1
        fi
    fi
    
    # Build the frontend
    print_status "Building React frontend..."
    npm run build
    if [ $? -ne 0 ]; then
        print_error "Frontend build failed"
        exit 1
    fi
    
    print_success "Frontend built successfully"
else
    print_success "Frontend build already exists"
fi

# Check if build directory exists now
if [ ! -d "build" ]; then
    print_error "Build directory still doesn't exist after build attempt"
    exit 1
fi

print_status "Frontend build contents:"
ls -la build/

# Go back to root directory
cd ..

print_success "Frontend is ready!"
print_status "The backend at http://0.0.0.0:8000 will serve the frontend automatically"
print_status "You can access the dashboard at:"
print_status "  🌐 http://190.105.244.174:8000/"
print_status "  🔐 Login: http://190.105.244.174:8000/login"
print_status "  📊 Dashboard: http://190.105.244.174:8000/dashboard"
print_status "  ❤️  Health: http://190.105.244.174:8000/health"
print_status "  📚 API Docs: http://190.105.244.174:8000/api/docs"

echo ""
print_success "✅ Frontend build complete! The backend will serve it automatically."
print_warning "⚠️  Make sure your backend is running on port 8000"
print_status "🔑 Use these credentials:"
print_status "   👑 Super Admin: admin@jasmin.com / admin123"
print_status "   👔 Manager: manager@jasmin.com / manager123"
print_status "   🔧 Operator: operator@jasmin.com / operator123"
print_status "   👤 User: user@jasmin.com / user123"