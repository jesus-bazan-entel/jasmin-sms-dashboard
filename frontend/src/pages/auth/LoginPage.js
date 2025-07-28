import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const LoginPage = () => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="background.default"
    >
      <Paper elevation={3} sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" align="center" gutterBottom>
          Jasmin SMS Dashboard
        </Typography>
        <Typography variant="h6" align="center" color="text.secondary">
          Página de Login
        </Typography>
        <Typography variant="body2" align="center" sx={{ mt: 2 }}>
          Componente en desarrollo...
        </Typography>
      </Paper>
    </Box>
  );
};

export default LoginPage;