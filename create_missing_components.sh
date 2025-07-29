#!/bin/bash

# Jasmin SMS Dashboard - Create Missing Components
echo "🔧 Creating Missing Frontend Components"
echo "======================================"

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

cd frontend

# Create directory structure
print_status "Creating directory structure..."
mkdir -p src/components/auth
mkdir -p src/components/layout
mkdir -p src/pages/Auth
mkdir -p src/pages/Dashboard
mkdir -p src/pages/Contacts
mkdir -p src/pages/Messages
mkdir -p src/pages/Templates
mkdir -p src/pages/Connectors
mkdir -p src/pages/Routing
mkdir -p src/pages/Analytics
mkdir -p src/pages/Reports
mkdir -p src/pages/Billing
mkdir -p src/pages/Users
mkdir -p src/pages/Settings
mkdir -p src/pages/Profile
mkdir -p src/store
mkdir -p src/utils
mkdir -p src/hooks

# 1. Create ProtectedRoute component
print_status "1. Creating ProtectedRoute component..."
cat > src/components/auth/ProtectedRoute.js << 'EOF'
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Layout from '../layout/Layout';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useSelector((state) => state.auth);
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Layout>{children}</Layout>;
};

export default ProtectedRoute;
EOF

# 2. Create Layout component
print_status "2. Creating Layout component..."
cat > src/components/layout/Layout.js << 'EOF'
import React, { useState } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Campaign,
  Contacts,
  Message,
  Template,
  Router,
  Analytics,
  Report,
  Payment,
  People,
  Settings,
  AccountCircle,
  Logout,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../../store/slices/authSlice';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
  { text: 'Campaigns', icon: <Campaign />, path: '/campaigns' },
  { text: 'Contacts', icon: <Contacts />, path: '/contacts' },
  { text: 'Messages', icon: <Message />, path: '/messages' },
  { text: 'Templates', icon: <Template />, path: '/templates' },
  { text: 'Connectors', icon: <Router />, path: '/connectors' },
  { text: 'Routing', icon: <Router />, path: '/routing' },
  { text: 'Analytics', icon: <Analytics />, path: '/analytics' },
  { text: 'Reports', icon: <Report />, path: '/reports' },
  { text: 'Billing', icon: <Payment />, path: '/billing' },
  { text: 'Users', icon: <People />, path: '/users' },
  { text: 'Settings', icon: <Settings />, path: '/settings' },
];

const Layout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
    handleProfileMenuClose();
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Jasmin SMS
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            SMS Dashboard
          </Typography>
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="primary-search-account-menu"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <Avatar sx={{ width: 32, height: 32 }}>
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
          >
            <MenuItem onClick={() => { navigate('/profile'); handleProfileMenuClose(); }}>
              <AccountCircle sx={{ mr: 1 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
EOF

# 3. Create Redux store
print_status "3. Creating Redux store..."
cat > src/store/store.js << 'EOF'
import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import dashboardSlice from './slices/dashboardSlice';
import campaignsSlice from './slices/campaignsSlice';
import contactsSlice from './slices/contactsSlice';
import messagesSlice from './slices/messagesSlice';
import connectorsSlice from './slices/connectorsSlice';
import templatesSlice from './slices/templatesSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    dashboard: dashboardSlice,
    campaigns: campaignsSlice,
    contacts: contactsSlice,
    messages: messagesSlice,
    connectors: connectorsSlice,
    templates: templatesSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export default store;
EOF

# 4. Create Login Page
print_status "4. Creating Login Page..."
cat > src/pages/Auth/LoginPage.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { login } from '../../store/slices/authSlice';

const LoginPage = () => {
  const [email, setEmail] = useState('admin@jasmin.com');
  const [password, setPassword] = useState('admin123');
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, error, isAuthenticated } = useSelector((state) => state.auth);

  const from = location.state?.from?.pathname || '/dashboard';

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await dispatch(login({ email, password })).unwrap();
      navigate(from, { replace: true });
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography component="h1" variant="h4" gutterBottom>
              📱 Jasmin SMS
            </Typography>
            <Typography variant="h6" color="textSecondary">
              Enterprise Dashboard
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
          </Box>

          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
            <Typography variant="body2" color="textSecondary" align="center">
              <strong>Demo Credentials:</strong><br />
              Email: admin@jasmin.com<br />
              Password: admin123
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
EOF

# 5. Create Dashboard Page
print_status "5. Creating Dashboard Page..."
cat > src/pages/Dashboard/DashboardPage.js << 'EOF'
import React, { useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import {
  TrendingUp,
  Message,
  People,
  Campaign,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDashboardStats } from '../../store/slices/dashboardSlice';

const StatCard = ({ title, value, icon, color }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center">
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: '50%',
            p: 1,
            mr: 2,
            color: 'white',
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography color="textSecondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4">
            {value}
          </Typography>
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const DashboardPage = () => {
  const dispatch = useDispatch();
  const { stats, loading } = useSelector((state) => state.dashboard);

  useEffect(() => {
    dispatch(fetchDashboardStats());
  }, [dispatch]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Messages"
            value={stats?.totalMessages || '0'}
            icon={<Message />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Campaigns"
            value={stats?.activeCampaigns || '0'}
            icon={<Campaign />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Contacts"
            value={stats?.totalContacts || '0'}
            icon={<People />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${stats?.successRate || '0'}%`}
            icon={<TrendingUp />}
            color="#7b1fa2"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography color="textSecondary">
              Welcome to your Jasmin SMS Dashboard! Here you can manage your SMS campaigns,
              monitor delivery rates, and analyze your messaging performance.
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Typography color="textSecondary">
              • Create new campaign<br />
              • Import contacts<br />
              • View reports<br />
              • Configure connectors
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
EOF

# 6. Create placeholder pages for other routes
print_status "6. Creating placeholder pages..."

# Contacts Page
cat > src/pages/Contacts/ContactsPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const ContactsPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Contacts Management
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Contact management functionality will be available here.
          You can import, organize, and segment your contact lists.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ContactsPage;
EOF

# Messages Page
cat > src/pages/Messages/MessagesPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const MessagesPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Messages
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Message history and delivery reports will be displayed here.
          Track the status of all your sent messages.
        </Typography>
      </Paper>
    </Box>
  );
};

export default MessagesPage;
EOF

# Templates Page
cat > src/pages/Templates/TemplatesPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const TemplatesPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Message Templates
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Create and manage your SMS message templates here.
          Use variables for personalization and save time.
        </Typography>
      </Paper>
    </Box>
  );
};

export default TemplatesPage;
EOF

# Connectors Page
cat > src/pages/Connectors/ConnectorsPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const ConnectorsPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        SMPP Connectors
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Configure and manage your SMPP connections here.
          Monitor connector status and performance.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ConnectorsPage;
EOF

# Routing Page
cat > src/pages/Routing/RoutingPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const RoutingPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Message Routing
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Configure routing rules for your messages here.
          Set up intelligent routing based on destination, content, and more.
        </Typography>
      </Paper>
    </Box>
  );
};

export default RoutingPage;
EOF

# Analytics Page
cat > src/pages/Analytics/AnalyticsPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const AnalyticsPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          View detailed analytics and insights about your SMS campaigns.
          Track performance metrics and optimize your messaging strategy.
        </Typography>
      </Paper>
    </Box>
  );
};

export default AnalyticsPage;
EOF

# Reports Page
cat > src/pages/Reports/ReportsPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const ReportsPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Generate and download detailed reports here.
          Export data for further analysis and compliance.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ReportsPage;
EOF

# Billing Page
cat > src/pages/Billing/BillingPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const BillingPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Billing & Credits
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Manage your billing information and credit balance here.
          View usage history and purchase additional credits.
        </Typography>
      </Paper>
    </Box>
  );
};

export default BillingPage;
EOF

# Users Page
cat > src/pages/Users/UsersPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const UsersPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Management
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Manage user accounts and permissions here.
          Add team members and configure role-based access.
        </Typography>
      </Paper>
    </Box>
  );
};

export default UsersPage;
EOF

# Settings Page
cat > src/pages/Settings/SettingsPage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const SettingsPage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Configure system settings and preferences here.
          Customize your dashboard experience.
        </Typography>
      </Paper>
    </Box>
  );
};

export default SettingsPage;
EOF

# Profile Page
cat > src/pages/Profile/ProfilePage.js << 'EOF'
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const ProfilePage = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Manage your profile information here.
          Update your personal details and security settings.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ProfilePage;
EOF

print_success "✅ All missing components created successfully!"
print_status "Components created:"
print_status "  ✅ ProtectedRoute"
print_status "  ✅ Layout with navigation"
print_status "  ✅ Redux store"
print_status "  ✅ Login page"
print_status "  ✅ Dashboard page"
print_status "  ✅ All placeholder pages"

cd ..
print_success "🎉 Missing components creation complete!"