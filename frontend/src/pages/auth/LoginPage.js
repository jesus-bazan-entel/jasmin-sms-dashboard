import React, { useState } from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Link,
  CircularProgress,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Login as LoginIcon,
  Sms,
} from "@mui/icons-material";
import { useAuth } from "../../contexts/AuthContext";
import { Link as RouterLink } from "react-router-dom";

const LoginPage = () => {
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Limpiar error del campo cuando el usuario empiece a escribir
    if (formErrors[name]) {
      setFormErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.email) {
      errors.email = "El email es requerido";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "El email no es válido";
    }

    if (!formData.password) {
      errors.password = "La contraseña es requerida";
    } else if (formData.password.length < 6) {
      errors.password = "La contraseña debe tener al menos 6 caracteres";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
    } catch (error) {
      console.error("Error en login:", error);
    }
  };

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  // Datos de demostración para testing
  const demoCredentials = [
    { email: "admin@jasmin.com", password: "admin123", role: "Super Admin" },
    { email: "manager@jasmin.com", password: "manager123", role: "Manager" },
    { email: "operator@jasmin.com", password: "operator123", role: "Operator" },
  ];

  const handleDemoLogin = (credentials) => {
    setFormData({
      email: credentials.email,
      password: credentials.password,
    });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 2,
      }}
    >
      <Paper
        elevation={24}
        sx={{
          p: 4,
          maxWidth: 450,
          width: "100%",
          borderRadius: 3,
          background: "rgba(255, 255, 255, 0.95)",
          backdropFilter: "blur(10px)",
        }}
      >
        {/* Header */}
        <Box textAlign="center" mb={4}>
          <Box
            sx={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: 80,
              height: 80,
              borderRadius: "50%",
              background: "linear-gradient(45deg, #667eea 30%, #764ba2 90%)",
              mb: 2,
            }}
          >
            <Sms sx={{ fontSize: 40, color: "white" }} />
          </Box>

          <Typography
            variant="h4"
            fontWeight="bold"
            color="primary"
            gutterBottom
          >
            Jasmin SMS Dashboard
          </Typography>

          <Typography variant="body1" color="text.secondary">
            Plataforma Empresarial de Marketing SMS
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Login Form */}
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            name="email"
            label="Email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={!!formErrors.email}
            helperText={formErrors.email}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email color="action" />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
            disabled={loading}
          />

          <TextField
            fullWidth
            name="password"
            label="Contraseña"
            type={showPassword ? "text" : "password"}
            value={formData.password}
            onChange={handleChange}
            error={!!formErrors.password}
            helperText={formErrors.password}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={handleTogglePassword}
                    edge="end"
                    disabled={loading}
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ mb: 3 }}
            disabled={loading}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
            sx={{
              py: 1.5,
              mb: 2,
              background: "linear-gradient(45deg, #667eea 30%, #764ba2 90%)",
              "&:hover": {
                background: "linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)",
              },
            }}
          >
            {loading ? "Iniciando Sesión..." : "Iniciar Sesión"}
          </Button>

          {/* Links */}
          <Box textAlign="center" mb={3}>
            <Link
              component={RouterLink}
              to="/forgot-password"
              variant="body2"
              sx={{ textDecoration: "none" }}
            >
              ¿Olvidaste tu contraseña?
            </Link>
          </Box>

          <Divider sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              o
            </Typography>
          </Divider>

          {/* Register Link */}
          <Box textAlign="center">
            <Typography variant="body2" color="text.secondary">
              ¿No tienes una cuenta?{" "}
              <Link
                component={RouterLink}
                to="/register"
                sx={{ textDecoration: "none", fontWeight: "bold" }}
              >
                Regístrate aquí
              </Link>
            </Typography>
          </Box>
        </Box>

        {/* Demo Credentials */}
        <Box mt={4}>
          <Divider sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Credenciales de Demostración
            </Typography>
          </Divider>

          <Box display="flex" flexDirection="column" gap={1}>
            {demoCredentials.map((cred, index) => (
              <Button
                key={index}
                variant="outlined"
                size="small"
                onClick={() => handleDemoLogin(cred)}
                disabled={loading}
                sx={{
                  justifyContent: "flex-start",
                  textTransform: "none",
                  fontSize: "0.75rem",
                }}
              >
                <Box textAlign="left">
                  <Typography variant="caption" display="block">
                    {cred.role}: {cred.email}
                  </Typography>
                </Box>
              </Button>
            ))}
          </Box>

          <Typography
            variant="caption"
            color="text.secondary"
            display="block"
            mt={1}
          >
            Haz clic en cualquier credencial para autocompletar el formulario
          </Typography>
        </Box>

        {/* Footer */}
        <Box textAlign="center" mt={4}>
          <Typography variant="caption" color="text.secondary">
            Jasmin SMS Dashboard v2.0.0 - Enterprise Edition
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default LoginPage;
