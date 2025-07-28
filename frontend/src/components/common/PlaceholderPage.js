import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import { Construction } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const PlaceholderPage = ({ title = 'Página en Desarrollo', subtitle = 'Esta funcionalidad estará disponible pronto' }) => {
  const navigate = useNavigate();

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="80vh"
      p={3}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 500,
          width: '100%',
          textAlign: 'center',
          borderRadius: 2,
        }}
      >
        <Construction
          sx={{
            fontSize: 80,
            color: 'primary.main',
            mb: 2,
          }}
        />
        
        <Typography variant="h4" gutterBottom color="primary">
          {title}
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          {subtitle}
        </Typography>

        <Typography variant="body2" color="text.secondary" paragraph>
          Esta página está siendo desarrollada y estará disponible en una próxima actualización.
        </Typography>

        <Button
          variant="contained"
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 2 }}
        >
          Volver al Dashboard
        </Button>
      </Paper>
    </Box>
  );
};

export default PlaceholderPage;