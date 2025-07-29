import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  IconButton,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Message,
  Campaign,
  Contacts,
  CheckCircle,
  Error,
  Schedule,
  Refresh,
  Notifications,
  Send,
  Receipt,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

// Datos de demostración
const generateDemoStats = () => ({
  totalMessages: Math.floor(Math.random() * 50000) + 10000,
  sentMessages: Math.floor(Math.random() * 40000) + 8000,
  failedMessages: Math.floor(Math.random() * 1000) + 100,
  pendingMessages: Math.floor(Math.random() * 500) + 50,
  totalCampaigns: Math.floor(Math.random() * 50) + 10,
  activeCampaigns: Math.floor(Math.random() * 10) + 2,
  totalContacts: Math.floor(Math.random() * 10000) + 1000,
  totalCredits: Math.floor(Math.random() * 5000) + 500,
  successRate: (Math.random() * 20 + 80).toFixed(1), // 80-100%
  avgDeliveryTime: (Math.random() * 5 + 2).toFixed(1), // 2-7 segundos
});

const generateRecentActivity = () => [
  {
    id: 1,
    type: 'campaign',
    title: 'Campaña "Promoción Verano" completada',
    description: '2,450 mensajes enviados exitosamente',
    time: '5 min ago',
    icon: <Campaign />,
    color: 'success',
  },
  {
    id: 2,
    type: 'message',
    title: 'Mensaje masivo enviado',
    description: '850 contactos alcanzados',
    time: '12 min ago',
    icon: <Send />,
    color: 'primary',
  },
  {
    id: 3,
    type: 'error',
    title: 'Conector SMPP desconectado',
    description: 'Conector "Provider-1" requiere atención',
    time: '25 min ago',
    icon: <Error />,
    color: 'error',
  },
  {
    id: 4,
    type: 'contact',
    title: 'Nuevos contactos importados',
    description: '125 contactos agregados a la lista "Clientes VIP"',
    time: '1 hora ago',
    icon: <Contacts />,
    color: 'info',
  },
  {
    id: 5,
    type: 'billing',
    title: 'Créditos recargados',
    description: '1,000 créditos SMS agregados',
    time: '2 horas ago',
    icon: <Receipt />,
    color: 'success',
  },
];

const StatCard = ({ title, value, subtitle, icon, trend, color = 'primary' }) => (
  <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="text.secondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="div" fontWeight="bold">
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Avatar
          sx={{
            bgcolor: `${color}.main`,
            width: 56,
            height: 56,
          }}
        >
          {icon}
        </Avatar>
      </Box>
      
      {trend && (
        <Box display="flex" alignItems="center" mt={2}>
          {trend > 0 ? (
            <TrendingUp color="success" fontSize="small" />
          ) : (
            <TrendingDown color="error" fontSize="small" />
          )}
          <Typography
            variant="body2"
            color={trend > 0 ? 'success.main' : 'error.main'}
            sx={{ ml: 0.5 }}
          >
            {Math.abs(trend)}% vs mes anterior
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const { user, isDemoMode } = useAuth();
  const [stats, setStats] = useState(generateDemoStats());
  const [recentActivity] = useState(generateRecentActivity());
  const [loading, setLoading] = useState(false);

  const refreshStats = () => {
    setLoading(true);
    setTimeout(() => {
      setStats(generateDemoStats());
      setLoading(false);
    }, 1000);
  };

  useEffect(() => {
    // Simular actualización automática cada 30 segundos
    const interval = setInterval(() => {
      setStats(generateDemoStats());
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const successRate = ((stats.sentMessages / stats.totalMessages) * 100).toFixed(1);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            ¡Bienvenido, {user?.full_name || user?.username}!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Aquí tienes un resumen de tu actividad SMS
          </Typography>
        </Box>
        <IconButton 
          onClick={refreshStats} 
          disabled={loading}
          sx={{ 
            bgcolor: 'primary.main', 
            color: 'white',
            '&:hover': { bgcolor: 'primary.dark' }
          }}
        >
          <Refresh />
        </IconButton>
      </Box>

      {/* Demo Mode Alert */}
      {isDemoMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <strong>Modo Demostración:</strong> Los datos mostrados son simulados para propósitos de demostración.
          Para usar datos reales, conecte con el backend de Jasmin SMS Gateway.
        </Alert>
      )}

      {/* Loading Bar */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Mensajes"
            value={stats.totalMessages.toLocaleString()}
            subtitle="Este mes"
            icon={<Message />}
            trend={12.5}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Mensajes Enviados"
            value={stats.sentMessages.toLocaleString()}
            subtitle={`${successRate}% tasa de éxito`}
            icon={<CheckCircle />}
            trend={8.2}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Campañas Activas"
            value={stats.activeCampaigns}
            subtitle={`${stats.totalCampaigns} total`}
            icon={<Campaign />}
            trend={-2.1}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Créditos SMS"
            value={stats.totalCredits.toLocaleString()}
            subtitle="Disponibles"
            icon={<Receipt />}
            trend={5.7}
            color="warning"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Performance Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h6" fontWeight="bold">
                  Resumen de Performance
                </Typography>
                <Chip 
                  label="Tiempo Real" 
                  color="success" 
                  size="small"
                  icon={<Notifications />}
                />
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Tasa de Entrega</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {successRate}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={parseFloat(successRate)} 
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Mensajes Pendientes</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {stats.pendingMessages}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(stats.pendingMessages / stats.totalMessages) * 100} 
                      color="warning"
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  <Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Mensajes Fallidos</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {stats.failedMessages}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(stats.failedMessages / stats.totalMessages) * 100} 
                      color="error"
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Métricas Clave
                    </Typography>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Tiempo Promedio de Entrega:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {stats.avgDeliveryTime}s
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Total Contactos:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {stats.totalContacts.toLocaleString()}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2">Conectores Activos:</Typography>
                      <Typography variant="body2" fontWeight="bold" color="success.main">
                        3/4
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Actividad Reciente
              </Typography>
              <List>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: `${activity.color}.main` }}>
                        {activity.icon}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="body2" fontWeight="bold">
                          {activity.title}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            {activity.description}
                          </Typography>
                          <Typography variant="caption" display="block" color="primary">
                            {activity.time}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;