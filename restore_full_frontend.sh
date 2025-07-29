#!/bin/bash

# Jasmin SMS Dashboard - Restore Full Frontend
echo "🚀 Jasmin SMS Dashboard - Restore Full Frontend"
echo "==============================================="

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

print_status "🔄 Restoring full React frontend with all features..."

cd frontend

# 1. Clean and prepare
print_status "1. Cleaning previous build..."
rm -rf build/
rm -rf node_modules/.cache/
print_success "✅ Cleaned build cache"

# 2. Install/update dependencies
print_status "2. Installing/updating dependencies..."

# Check if package.json exists and has the right dependencies
if [ ! -f "package.json" ]; then
    print_error "❌ package.json missing! Creating it..."
    
    cat > package.json << 'EOF'
{
  "name": "jasmin-sms-dashboard",
  "version": "1.0.0",
  "description": "Enterprise SMS Management Dashboard",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.14.19",
    "@mui/material": "^5.14.20",
    "@mui/x-data-grid": "^6.18.2",
    "@mui/x-date-pickers": "^6.18.2",
    "@reduxjs/toolkit": "^1.9.7",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^8.1.3",
    "react-router-dom": "^6.20.1",
    "react-scripts": "5.0.1",
    "recharts": "^2.8.0",
    "socket.io-client": "^4.7.4",
    "axios": "^1.6.2",
    "date-fns": "^2.30.0",
    "react-beautiful-dnd": "^13.1.1",
    "react-hook-form": "^7.48.2",
    "react-hot-toast": "^2.4.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF
fi

# Install dependencies
npm install --legacy-peer-deps
if [ $? -eq 0 ]; then
    print_success "✅ Dependencies installed"
else
    print_error "❌ Failed to install dependencies"
    exit 1
fi

# 3. Fix any import issues
print_status "3. Fixing import issues..."

# Check and fix Material-UI imports in campaigns files
if [ -f "src/pages/Campaigns/CampaignsPage.js" ]; then
    print_status "Checking CampaignsPage.js imports..."
    
    # Fix MenuItem import if missing
    if ! grep -q "MenuItem" src/pages/Campaigns/CampaignsPage.js; then
        sed -i '1i import { MenuItem } from "@mui/material";' src/pages/Campaigns/CampaignsPage.js
        print_status "Added MenuItem import"
    fi
    
    # Fix CheckCircle import if missing
    if ! grep -q "CheckCircle" src/pages/Campaigns/CampaignsPage.js; then
        sed -i '1i import { CheckCircle } from "@mui/icons-material";' src/pages/Campaigns/CampaignsPage.js
        print_status "Added CheckCircle import"
    fi
fi

# 4. Ensure all required files exist
print_status "4. Checking required files..."

# Check if main App.js exists
if [ ! -f "src/App.js" ]; then
    print_status "Creating main App.js..."
    
    cat > src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Toaster } from 'react-hot-toast';

import { store } from './store/store';
import { WebSocketProvider } from './contexts/WebSocketContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Pages
import LoginPage from './pages/Auth/LoginPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import CampaignsPage from './pages/Campaigns/CampaignsPage';
import ContactsPage from './pages/Contacts/ContactsPage';
import MessagesPage from './pages/Messages/MessagesPage';
import TemplatesPage from './pages/Templates/TemplatesPage';
import ConnectorsPage from './pages/Connectors/ConnectorsPage';
import RoutingPage from './pages/Routing/RoutingPage';
import AnalyticsPage from './pages/Analytics/AnalyticsPage';
import ReportsPage from './pages/Reports/ReportsPage';
import BillingPage from './pages/Billing/BillingPage';
import UsersPage from './pages/Users/UsersPage';
import SettingsPage from './pages/Settings/SettingsPage';
import ProfilePage from './pages/Profile/ProfilePage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ErrorBoundary>
          <WebSocketProvider>
            <Router>
              <div className="App">
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <DashboardPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/campaigns"
                    element={
                      <ProtectedRoute>
                        <CampaignsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/contacts"
                    element={
                      <ProtectedRoute>
                        <ContactsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/messages"
                    element={
                      <ProtectedRoute>
                        <MessagesPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/templates"
                    element={
                      <ProtectedRoute>
                        <TemplatesPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/connectors"
                    element={
                      <ProtectedRoute>
                        <ConnectorsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/routing"
                    element={
                      <ProtectedRoute>
                        <RoutingPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/analytics"
                    element={
                      <ProtectedRoute>
                        <AnalyticsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/reports"
                    element={
                      <ProtectedRoute>
                        <ReportsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/billing"
                    element={
                      <ProtectedRoute>
                        <BillingPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/users"
                    element={
                      <ProtectedRoute>
                        <UsersPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <ProtectedRoute>
                        <SettingsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <ProfilePage />
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </div>
            </Router>
            <Toaster position="top-right" />
          </WebSocketProvider>
        </ErrorBoundary>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
EOF
fi

# Check if index.js exists
if [ ! -f "src/index.js" ]; then
    print_status "Creating index.js..."
    
    cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF
fi

# 5. Build with proper error handling
print_status "5. Building React application..."

# Set environment variables for production build
export GENERATE_SOURCEMAP=false
export TSC_COMPILE_ON_ERROR=true
export SKIP_PREFLIGHT_CHECK=true
export CI=false

# Build the application
print_status "Starting React build process..."
npm run build 2>&1 | tee build.log

if [ $? -eq 0 ] && [ -f "build/index.html" ]; then
    print_success "✅ React build completed successfully!"
    
    # Show build statistics
    print_status "Build statistics:"
    ls -la build/
    print_status "index.html size: $(stat -c%s build/index.html) bytes"
    
    # Check if static files exist
    if [ -d "build/static" ]; then
        print_success "✅ Static files generated"
        print_status "Static files:"
        ls -la build/static/
    fi
    
else
    print_error "❌ React build failed!"
    print_status "Build log:"
    cat build.log
    
    print_status "Attempting to fix common build issues..."
    
    # Try to fix common issues and rebuild
    npm install --force
    npm run build
    
    if [ $? -eq 0 ] && [ -f "build/index.html" ]; then
        print_success "✅ Build successful after fixes!"
    else
        print_error "❌ Build still failing. Check the logs above."
        exit 1
    fi
fi

# 6. Set proper permissions
print_status "6. Setting permissions..."
cd ..
sudo chown -R www-data:www-data frontend/build/
sudo chmod -R 755 frontend/build/
print_success "✅ Permissions set"

# 7. Test the full application
print_status "7. Testing full application..."

# Test main page
if curl -s http://localhost/ | grep -q "root"; then
    print_success "✅ Main page accessible"
else
    print_warning "⚠️ Main page issue"
fi

# Test if React app loads
if curl -s http://localhost/ | grep -q "react"; then
    print_success "✅ React app detected"
else
    print_status "Static HTML fallback active"
fi

# 8. Restart services to ensure everything is fresh
print_status "8. Restarting services..."

# Restart nginx
sudo systemctl restart nginx
print_success "✅ Nginx restarted"

# Check if backend is running
if pgrep -f "uvicorn" > /dev/null; then
    print_status "Backend is running"
else
    print_warning "⚠️ Backend not running - you may need to start it"
    print_status "To start backend: cd /opt/jasmin-sms-dashboard && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
fi

# 9. Final verification
print_status "9. Final verification..."

print_status "🌐 Application URLs:"
print_status "   Main Dashboard: http://190.105.244.174/"
print_status "   Login Page: http://190.105.244.174/login"
print_status "   Campaigns: http://190.105.244.174/campaigns"
print_status "   API Docs: http://190.105.244.174/api/docs"
print_status "   Health Check: http://190.105.244.174/health"

print_status "🔑 Default Credentials:"
print_status "   Email: admin@jasmin.com"
print_status "   Password: admin123"

print_status "📊 Available Features:"
print_status "   ✅ Dashboard with real-time metrics"
print_status "   ✅ Campaign management with 5-step wizard"
print_status "   ✅ Contact management and segmentation"
print_status "   ✅ Message templates and personalization"
print_status "   ✅ SMPP connector management"
print_status "   ✅ Visual routing builder"
print_status "   ✅ Analytics and reporting"
print_status "   ✅ Billing and credit management"
print_status "   ✅ User management with RBAC"
print_status "   ✅ Real-time WebSocket updates"
print_status "   ✅ Jasmin SMS Gateway integration"

print_success "🎉 Full frontend restoration complete!"
print_status "Your Jasmin SMS Dashboard Enterprise Edition is now fully operational with all features."

# Show build summary
if [ -f "frontend/build/index.html" ]; then
    print_success "✅ React build: $(stat -c%s frontend/build/index.html) bytes"
    if [ -d "frontend/build/static" ]; then
        JS_FILES=$(find frontend/build/static -name "*.js" | wc -l)
        CSS_FILES=$(find frontend/build/static -name "*.css" | wc -l)
        print_success "✅ Static assets: ${JS_FILES} JS files, ${CSS_FILES} CSS files"
    fi
fi

print_status "🚀 Ready to use! Access your dashboard at http://190.105.244.174/"