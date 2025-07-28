import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const LoadingSpinner = ({ 
  size = 40, 
  message = 'Cargando...', 
  fullScreen = false,
  color = 'primary' 
}) => {
  const content = (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      gap={2}
      sx={{
        ...(fullScreen && {
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          zIndex: 9999,
        }),
        ...(!fullScreen && {
          padding: 4,
        }),
      }}
    >
      <CircularProgress size={size} color={color} thickness={4} />
      {message && (
        <Typography 
          variant="body2" 
          color="text.secondary"
          sx={{ fontSize: '0.9rem', fontWeight: 500 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );

  return content;
};

export default LoadingSpinner;