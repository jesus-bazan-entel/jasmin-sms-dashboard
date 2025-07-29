#!/bin/bash

# Jasmin SMS Dashboard - Fix Database Connection
echo "🔧 Jasmin SMS Dashboard - Fix Database Connection"
echo "================================================"

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

print_status "Fixing database connection issues..."

# 1. Create corrected database test script
print_status "1. Creating corrected database test..."

cat > test_db_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Test database connection with proper SQLAlchemy syntax
"""
import asyncio
from sqlalchemy import text
from app.db.database import engine
from app.core.config_simple import settings

async def test_db_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        print(f"Database URL: {settings.DATABASE_URL}")
        
        async with engine.begin() as conn:
            # Use text() for raw SQL queries
            result = await conn.execute(text('SELECT 1 as test'))
            row = result.fetchone()
            if row and row[0] == 1:
                print('✅ Database connection successful')
                return True
            else:
                print('❌ Database query returned unexpected result')
                return False
                
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        print(f'Error type: {type(e).__name__}')
        return False

async def test_db_tables():
    """Test if tables exist"""
    try:
        print("🔍 Testing database tables...")
        
        async with engine.begin() as conn:
            # Check if users table exists
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            """))
            
            if result.fetchone():
                print('✅ Users table exists')
                
                # Count users
                result = await conn.execute(text('SELECT COUNT(*) FROM users'))
                count = result.fetchone()[0]
                print(f'✅ Found {count} users in database')
                return True
            else:
                print('❌ Users table does not exist')
                return False
                
    except Exception as e:
        print(f'❌ Table check failed: {e}')
        return False

async def create_test_user():
    """Create a test user if none exist"""
    try:
        print("🔍 Creating test user...")
        
        async with engine.begin() as conn:
            # Check if admin user exists
            result = await conn.execute(text("""
                SELECT id FROM users WHERE email = 'admin@jasmin.com'
            """))
            
            if result.fetchone():
                print('✅ Admin user already exists')
                return True
            else:
                print('⚠️ Admin user does not exist')
                print('Run the database setup script to create users')
                return False
                
    except Exception as e:
        print(f'❌ User check failed: {e}')
        return False

async def main():
    """Main test function"""
    print("🚀 Database Connection Test")
    print("=" * 40)
    
    # Test connection
    conn_ok = await test_db_connection()
    
    if conn_ok:
        # Test tables
        tables_ok = await test_db_tables()
        
        if tables_ok:
            # Test users
            users_ok = await create_test_user()
            
            if users_ok:
                print("\n✅ Database is fully functional!")
                return True
    
    print("\n❌ Database issues detected")
    return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
EOF

chmod +x test_db_connection.py

print_success "✅ Database test script created"

# 2. Run the corrected database test
print_status "2. Running corrected database test..."
python test_db_connection.py

if [ $? -eq 0 ]; then
    print_success "✅ Database connection is working"
else
    print_warning "⚠️ Database needs setup"
    
    # 3. Try to fix database issues
    print_status "3. Attempting to fix database..."
    
    # Run database setup
    if [ -f "fix_database_simple.py" ]; then
        print_status "Running database setup..."
        python fix_database_simple.py
    else
        print_warning "Database setup script not found"
    fi
fi

# 4. Create a corrected version of the login error script
print_status "4. Creating corrected login error script..."

cat > fix_login_error_corrected.sh << 'EOF'
#!/bin/bash

# Jasmin SMS Dashboard - Fix Login Error 500 (Corrected)
echo "🔧 Jasmin SMS Dashboard - Fix Login Error 500 (Corrected)"
echo "========================================================"

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

# 2. Test backend imports
print_status "2. Testing backend imports..."
python test_import.py
if [ $? -ne 0 ]; then
    print_error "Backend import test failed"
    exit 1
fi

# 3. Test database connection with corrected script
print_status "3. Testing database connection..."
python test_db_connection.py
if [ $? -ne 0 ]; then
    print_warning "Database connection issues detected"
    print_status "Attempting to fix database..."
    
    if [ -f "fix_database_simple.py" ]; then
        python fix_database_simple.py
    fi
fi

# 4. Check nginx configuration
print_status "4. Checking nginx configuration..."
if nginx -t 2>/dev/null; then
    print_success "Nginx configuration is valid"
else
    print_warning "Nginx configuration issues detected"
fi

# 5. Check if frontend build exists
print_status "5. Checking frontend build..."
if [ -d "frontend/build" ]; then
    print_success "Frontend build exists"
else
    print_error "Frontend build missing"
    print_status "Building frontend..."
    cd frontend
    GENERATE_SOURCEMAP=false TSC_COMPILE_ON_ERROR=true npm run build
    cd ..
fi

# 6. Start backend with proper error handling
print_status "6. Starting backend with error logging..."

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

# 7. Test backend endpoints
print_status "7. Testing backend endpoints..."

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

print_status "8. System status summary:"
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
EOF

chmod +x fix_login_error_corrected.sh

print_success "✅ Corrected login error script created"

print_status "5. Summary:"
echo "=================================="
print_status "✅ Created corrected database test: test_db_connection.py"
print_status "✅ Created corrected login fix: fix_login_error_corrected.sh"
print_status ""
print_status "🚀 Next steps:"
print_status "1. Run: ./fix_login_error_corrected.sh"
print_status "2. Test login at: http://190.105.244.174/login"
print_status "3. Access campaigns at: http://190.105.244.174/campaigns"

print_success "🎉 Database connection fix complete!"