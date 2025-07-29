#!/usr/bin/env python3
"""
Test script to verify backend imports work correctly
"""
import sys
import os

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing backend imports...")
    
    try:
        # Test core config
        print("  ✓ Testing app.core.config...")
        from app.core.config import settings
        print(f"    App Name: {settings.APP_NAME}")
        
        # Test database
        print("  ✓ Testing app.db.database...")
        from app.db.database import engine, Base
        
        # Test models
        print("  ✓ Testing app.models...")
        import app.models
        
        # Test API router
        print("  ✓ Testing app.api.v1.api...")
        from app.api.v1.api import api_router
        
        # Test main app
        print("  ✓ Testing app.main...")
        from app.main import app
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        from app.main import app
        print(f"  ✓ App title: {app.title}")
        print(f"  ✓ App version: {app.version}")
        print("✅ FastAPI app created successfully!")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Jasmin SMS Dashboard - Backend Import Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test app creation
    app_ok = test_app_creation()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 50)
    if imports_ok and app_ok:
        print("✅ All tests passed! Backend is ready to start.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)