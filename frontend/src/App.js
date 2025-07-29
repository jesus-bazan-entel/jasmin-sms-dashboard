import React, { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import { useAuth } from "./contexts/AuthContext";
import { useWebSocket } from "./contexts/WebSocketContext";

// Importar todas las páginas desde el archivo index
import {
  LoginPage,
  RegisterPage,
  ForgotPasswordPage,
  DashboardLayout,
  Dashboard,
  CampaignsPage,
  CampaignDetail,
  CreateCampaign,
  Contacts,
  ContactDetail,
  ContactLists,
  Messages,
  MessageDetail,
  Templates,
  TemplateEditor,
  Connectors,
  ConnectorDetail,
  Routing,
  RoutingBuilder,
  Analytics,
  Reports,
  Billing,
  BillingDetail,
  Users,
  UserDetail,
  Settings,
  Profile,
  ApiDocs,
  Webhooks,
  Logs,
  NotFound,
  Unauthorized,
  ServerError,
} from "./pages";

// Componente de carga
const LoadingFallback = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    flexDirection="column"
    gap={2}
  >
    <CircularProgress size={60} thickness={4} />
    <Box sx={{ color: "text.secondary", fontSize: "1.1rem" }}>
      Cargando Jasmin SMS Dashboard...
    </Box>
  </Box>
);

// Componente de ruta protegida
const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Verificar rol si es requerido
  if (requiredRole && user?.role !== requiredRole) {
    // Verificar jerarquía de roles
    const roleHierarchy = {
      user: 1,
      operator: 2,
      manager: 3,
      admin: 4,
      super_admin: 5,
    };

    const userRoleLevel = roleHierarchy[user?.role] || 0;
    const requiredRoleLevel = roleHierarchy[requiredRole] || 0;

    if (userRoleLevel < requiredRoleLevel) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
};

// Componente de ruta pública (solo para usuarios no autenticados)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Componente principal de la aplicación
function App() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { connectionStatus } = useWebSocket();

  // Mostrar loading mientras se inicializa la autenticación
  if (authLoading) {
    return <LoadingFallback />;
  }

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "background.default" }}>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* Rutas públicas (solo para usuarios no autenticados) */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          <Route
            path="/forgot-password"
            element={
              <PublicRoute>
                <ForgotPasswordPage />
              </PublicRoute>
            }
          />

          {/* Rutas protegidas */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            {/* Dashboard principal */}
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />

            {/* Gestión de campañas */}
            <Route path="campaigns" element={<CampaignsPage />} />
            <Route path="campaigns/create" element={<CreateCampaign />} />
            <Route path="campaigns/:id" element={<CampaignDetail />} />

            {/* Gestión de contactos */}
            <Route path="contacts" element={<Contacts />} />
            <Route path="contacts/lists" element={<ContactLists />} />
            <Route path="contacts/:id" element={<ContactDetail />} />

            {/* Gestión de mensajes */}
            <Route path="messages" element={<Messages />} />
            <Route path="messages/:id" element={<MessageDetail />} />

            {/* Plantillas */}
            <Route path="templates" element={<Templates />} />
            <Route path="templates/create" element={<TemplateEditor />} />
            <Route path="templates/:id/edit" element={<TemplateEditor />} />

            {/* Conectores SMPP */}
            <Route
              path="connectors"
              element={
                <ProtectedRoute requiredRole="manager">
                  <Connectors />
                </ProtectedRoute>
              }
            />
            <Route
              path="connectors/:id"
              element={
                <ProtectedRoute requiredRole="manager">
                  <ConnectorDetail />
                </ProtectedRoute>
              }
            />

            {/* Enrutamiento */}
            <Route
              path="routing"
              element={
                <ProtectedRoute requiredRole="manager">
                  <Routing />
                </ProtectedRoute>
              }
            />
            <Route
              path="routing/builder"
              element={
                <ProtectedRoute requiredRole="manager">
                  <RoutingBuilder />
                </ProtectedRoute>
              }
            />

            {/* Analytics y reportes */}
            <Route path="analytics" element={<Analytics />} />
            <Route path="reports" element={<Reports />} />

            {/* Facturación */}
            <Route
              path="billing"
              element={
                <ProtectedRoute requiredRole="manager">
                  <Billing />
                </ProtectedRoute>
              }
            />
            <Route
              path="billing/:id"
              element={
                <ProtectedRoute requiredRole="manager">
                  <BillingDetail />
                </ProtectedRoute>
              }
            />

            {/* Gestión de usuarios */}
            <Route
              path="users"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Users />
                </ProtectedRoute>
              }
            />
            <Route
              path="users/:id"
              element={
                <ProtectedRoute requiredRole="admin">
                  <UserDetail />
                </ProtectedRoute>
              }
            />

            {/* API y Webhooks */}
            <Route path="api" element={<ApiDocs />} />
            <Route
              path="webhooks"
              element={
                <ProtectedRoute requiredRole="manager">
                  <Webhooks />
                </ProtectedRoute>
              }
            />

            {/* Logs del sistema */}
            <Route
              path="logs"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Logs />
                </ProtectedRoute>
              }
            />

            {/* Configuración */}
            <Route
              path="settings"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Settings />
                </ProtectedRoute>
              }
            />

            {/* Perfil de usuario */}
            <Route path="profile" element={<Profile />} />
          </Route>

          {/* Páginas de error */}
          <Route path="/unauthorized" element={<Unauthorized />} />
          <Route path="/server-error" element={<ServerError />} />
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>

      {/* Indicador de estado de conexión WebSocket */}
      {isAuthenticated && connectionStatus !== "connected" && (
        <Box
          sx={{
            position: "fixed",
            bottom: 16,
            right: 16,
            backgroundColor:
              connectionStatus === "connecting" ? "warning.main" : "error.main",
            color: "white",
            padding: "8px 16px",
            borderRadius: 1,
            fontSize: "0.875rem",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          {connectionStatus === "connecting" && (
            <CircularProgress size={16} color="inherit" />
          )}
          {connectionStatus === "connecting"
            ? "Conectando..."
            : "Sin conexión en tiempo real"}
        </Box>
      )}
    </Box>
  );
}

export default App;
