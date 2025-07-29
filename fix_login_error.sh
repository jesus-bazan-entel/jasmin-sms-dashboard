#!/bin/bash

# Jasmin SMS Dashboard - Fix Login Error 500
echo "🔧 Jasmin SMS Dashboard - Fix Login Error 500"
echo "=============================================="

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
    print_warning "Activating virtual environment..."
    source venv/bin/activate
fi

print_status "Diagnosing login error 500..."

# 1. Check if backend is running
print_status "1. Checking backend status..."
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    print_success "Backend process is running"
    
    # Check if backend responds
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend responds to health check"
    else
        print_error "Backend not responding to health check"
        print_status "Restarting backend..."
        pkill -f "uvicorn app.main:app"
        sleep 2
    fi
else
    print_warning "Backend is not running"
fi

# 2. Check backend logs
print_status "2. Checking recent backend logs..."
if [ -f "backend.log" ]; then
    print_status "Recent backend errors:"
    tail -20 backend.log | grep -i error || echo "No recent errors in backend.log"
fi

# 3. Test backend imports
print_status "3. Testing backend imports..."
python test_import.py
if [ $? -ne 0 ]; then
    print_error "Backend import test failed"
    exit 1
fi

# 4. Check database connection
print_status "4. Testing database connection..."
python -c "
import asyncio
from app.db.database import engine
from app.core.config_simple import settings

async def test_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT 1')
            print('✅ Database connection successful')
            return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

if asyncio.run(test_db()):
    print('Database is accessible')
else:
    print('Database connection issues detected')
"

# 5. Check nginx configuration
print_status "5. Checking nginx configuration..."
if nginx -t 2>/dev/null; then
    print_success "Nginx configuration is valid"
else
    print_warning "Nginx configuration issues detected"
fi

# 6. Check if frontend build exists
print_status "6. Checking frontend build..."
if [ -d "frontend/build" ]; then
    print_success "Frontend build exists"
    ls -la frontend/build/ | head -5
else
    print_error "Frontend build missing"
    print_status "Building frontend..."
    cd frontend
    GENERATE_SOURCEMAP=false TSC_COMPILE_ON_ERROR=true npm run build
    cd ..
fi

# 7. Start backend with proper error handling
print_status "7. Starting backend with error logging..."

# Kill any existing backend processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2

# Start backend in background with logging
print_status "Starting backend server..."
nohup python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log > backend.log 2>&1 &

# Wait for backend to start
sleep 5

# Test backend endpoints
print_status "8. Testing backend endpoints..."

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "✅ Health endpoint working"
else
    print_error "❌ Health endpoint not responding"
fi

# Test API docs
if curl -s http://localhost:8000/api/docs > /dev/null; then
    print_success "✅ API docs endpoint working"
else
    print_error "❌ API docs endpoint not responding"
fi

# Test login endpoint
print_status "Testing login endpoint..."
LOGIN_RESPONSE=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@jasmin.com","password":"admin123"}' \
    http://localhost:8000/api/v1/auth/login)

HTTP_CODE="${LOGIN_RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
    print_success "✅ Login endpoint working"
elif [ "$HTTP_CODE" = "422" ]; then
    print_warning "⚠️ Login endpoint responds but validation error (expected)"
else
    print_error "❌ Login endpoint error: HTTP $HTTP_CODE"
    print_status "Response: ${LOGIN_RESPONSE%???}"
fi

# 9. Check recent logs for errors
print_status "9. Checking for recent errors..."
if [ -f "backend.log" ]; then
    print_status "Recent backend log (last 10 lines):"
    tail -10 backend.log
fi

print_status "10. System status summary:"
echo "=================================="
print_status "🌐 URLs to test:"
print_status "   Frontend: http://190.105.244.174/"
print_status "   Login: http://190.105.244.174/login"
print_status "   Health: http://190.105.244.174/health"
print_status "   API Docs: http://190.105.244.174/api/docs"
print_status "   Campaigns: http://190.105.244.174/campaigns"

print_status "🔑 Test credentials:"
print_status "   admin@jasmin.com / admin123"

print_success "✅ Diagnosis complete!"
print_status "If login still fails, check the backend.log file for detailed errors."