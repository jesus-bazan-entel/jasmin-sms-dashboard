import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { CssBaseline, Box } from "@mui/material";
import { SnackbarProvider } from "notistack";
import { HelmetProvider } from "react-helmet-async";

// Context Providers
import { AuthProvider } from "./contexts/AuthContext";
import { WebSocketProvider } from "./contexts/WebSocketContext";

// Components
import Layout from "./components/Layout/Layout";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import LoadingScreen from "./components/Common/LoadingScreen";

// Pages
import LoginPage from "./pages/Auth/LoginPage";
import RegisterPage from "./pages/Auth/RegisterPage";
import DashboardPage from "./pages/Dashboard/DashboardPage";
import ConnectorsPage from "./pages/Connectors/ConnectorsPage";
import ConnectorDetailPage from "./pages/Connectors/ConnectorDetailPage";
import RoutingPage from "./pages/Routing/RoutingPage";
import CampaignsPage from "./pages/Campaigns/CampaignsPage";
import CampaignDetailPage from "./pages/Campaigns/CampaignDetailPage";
import ContactsPage from "./pages/Contacts/ContactsPage";
import ContactListsPage from "./pages/Contacts/ContactListsPage";
import MessagesPage from "./pages/Messages/MessagesPage";
import TemplatesPage from "./pages/Templates/TemplatesPage";
import BillingPage from "./pages/Billing/BillingPage";
import AnalyticsPage from "./pages/Analytics/AnalyticsPage";
import SettingsPage from "./pages/Settings/SettingsPage";
import UsersPage from "./pages/Users/UsersPage";
import WebhooksPage from "./pages/Webhooks/WebhooksPage";
import LogsPage from "./pages/Logs/LogsPage";

// Theme configuration
const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
      light: "#42a5f5",
      dark: "#1565c0",
    },
    secondary: {
      main: "#dc004e",
      light: "#ff5983",
      dark: "#9a0036",
    },
    background: {
      default: "#f5f5f5",
      paper: "#ffffff",
    },
    success: {
      main: "#2e7d32",
      light: "#4caf50",
      dark: "#1b5e20",
    },
    warning: {
      main: "#ed6c02",
      light: "#ff9800",
      dark: "#e65100",
    },
    error: {
      main: "#d32f2f",
      light: "#f44336",
      dark: "#c62828",
    },
    info: {
      main: "#0288d1",
      light: "#03a9f4",
      dark: "#01579b",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 600,
    },
    h2: {
      fontSize: "2rem",
      fontWeight: 600,
    },
    h3: {
      fontSize: "1.75rem",
      fontWeight: 600,
    },
    h4: {
      fontSize: "1.5rem",
      fontWeight: 600,
    },
    h5: {
      fontSize: "1.25rem",
      fontWeight: 600,
    },
    h6: {
      fontSize: "1rem",
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
  },
});

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <SnackbarProvider
            maxSnack={3}
            anchorOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            autoHideDuration={5000}
          >
            <AuthProvider>
              <WebSocketProvider>
                <Router>
                  <Box sx={{ display: "flex", minHeight: "100vh" }}>
                    <Routes>
                      {/* Public Routes */}
                      <Route path="/login" element={<LoginPage />} />
                      <Route path="/register" element={<RegisterPage />} />

                      {/* Protected Routes */}
                      <Route
                        path="/*"
                        element={
                          <ProtectedRoute>
                            <Layout>
                              <Routes>
                                {/* Dashboard */}
                                <Route
                                  path="/"
                                  element={<Navigate to="/dashboard" replace />}
                                />
                                <Route
                                  path="/dashboard"
                                  element={<DashboardPage />}
                                />

                                {/* Connectors */}
                                <Route
                                  path="/connectors"
                                  element={<ConnectorsPage />}
                                />
                                <Route
                                  path="/connectors/:id"
                                  element={<ConnectorDetailPage />}
                                />

                                {/* Routing */}
                                <Route
                                  path="/routing"
                                  element={<RoutingPage />}
                                />

                                {/* Campaigns */}
                                <Route
                                  path="/campaigns"
                                  element={<CampaignsPage />}
                                />
                                <Route
                                  path="/campaigns/:id"
                                  element={<CampaignDetailPage />}
                                />

                                {/* Contacts */}
                                <Route
                                  path="/contacts"
                                  element={<ContactsPage />}
                                />
                                <Route
                                  path="/contact-lists"
                                  element={<ContactListsPage />}
                                />

                                {/* Messages */}
                                <Route
                                  path="/messages"
                                  element={<MessagesPage />}
                                />

                                {/* Templates */}
                                <Route
                                  path="/templates"
                                  element={<TemplatesPage />}
                                />

                                {/* Billing */}
                                <Route
                                  path="/billing"
                                  element={<BillingPage />}
                                />

                                {/* Analytics */}
                                <Route
                                  path="/analytics"
                                  element={<AnalyticsPage />}
                                />

                                {/* Settings */}
                                <Route
                                  path="/settings"
                                  element={<SettingsPage />}
                                />

                                {/* Users (Admin only) */}
                                <Route path="/users" element={<UsersPage />} />

                                {/* Webhooks */}
                                <Route
                                  path="/webhooks"
                                  element={<WebhooksPage />}
                                />

                                {/* Logs */}
                                <Route path="/logs" element={<LogsPage />} />

                                {/* Catch all */}
                                <Route
                                  path="*"
                                  element={<Navigate to="/dashboard" replace />}
                                />
                              </Routes>
                            </Layout>
                          </ProtectedRoute>
                        }
                      />
                    </Routes>
                  </Box>
                </Router>
              </WebSocketProvider>
            </AuthProvider>
          </SnackbarProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;
