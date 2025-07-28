import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { ErrorOutline, Refresh } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Actualiza el state para mostrar la UI de error
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Puedes registrar el error en un servicio de logging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Aquí podrías enviar el error a un servicio de monitoreo
    // como Sentry, LogRocket, etc.
    if (process.env.NODE_ENV === 'production') {
      // Ejemplo: Sentry.captureException(error);
    }
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          bgcolor="background.default"
          p={3}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              maxWidth: 600,
              textAlign: 'center',
              borderRadius: 2,
            }}
          >
            <ErrorOutline
              sx={{
                fontSize: 80,
                color: 'error.main',
                mb: 2,
              }}
            />
            
            <Typography variant="h4" gutterBottom color="error">
              ¡Oops! Algo salió mal
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph>
              Ha ocurrido un error inesperado en la aplicación. 
              Nuestro equipo ha sido notificado automáticamente.
            </Typography>

            <Box display="flex" gap={2} justifyContent="center" mt={3}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleReload}
                color="primary"
              >
                Recargar Página
              </Button>
              
              <Button
                variant="outlined"
                onClick={this.handleGoHome}
                color="primary"
              >
                Ir al Dashboard
              </Button>
            </Box>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box mt={4} textAlign="left">
                <Typography variant="h6" color="error" gutterBottom>
                  Detalles del Error (Solo en Desarrollo):
                </Typography>
                
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: 'grey.100',
                    maxHeight: 300,
                    overflow: 'auto',
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                  }}
                >
                  <Typography component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {this.state.error && this.state.error.toString()}
                    <br />
                    {this.state.errorInfo.componentStack}
                  </Typography>
                </Paper>
              </Box>
            )}

            <Typography variant="caption" color="text.secondary" display="block" mt={3}>
              Si el problema persiste, contacta al soporte técnico.
            </Typography>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;