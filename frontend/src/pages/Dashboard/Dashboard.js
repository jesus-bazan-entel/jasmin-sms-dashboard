// Dashboard principal - Copia del archivo original para resolver conflicto de mayúsculas
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Message,
  People,
  Campaign,
  Router,
  Refresh,
  CheckCircle,
  Error,
  Warning,
  Info
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState({
    totalMessages: 0,
    messagesThisMonth: 0,
    deliveryRate: 0,
    activeCampaigns: 0,
    activeConnectors: 0,
    creditBalance: 0,
    lastUpdated: null
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  // Simular datos de métricas
  useEffect(() => {
    const loadMetrics = () => {
      setMetrics({
        totalMessages: 125847,
        messagesThisMonth: 8432,
        deliveryRate: 94.2,
        activeCampaigns: 12,
        activeConnectors: 5,
        creditBalance: 2847.50,
        lastUpdated: new Date()
      });

      setRecentActivity([
        {
          id: 1,
          type: 'success',
          message: 'Campaña "Promoción Verano" completada exitosamente',
          time: '2 minutos atrás',
          icon: CheckCircle,
          color: 'success'
        },
        {
          id: 2,
          type: 'info',
          message: 'Nuevo conector SMPP configurado: Proveedor-A',
          time: '15 minutos atrás',
          icon: Info,
          color: 'info'
        },
        {
          id: 3,
          type: 'warning',
          message: 'Créditos por debajo del límite mínimo',
          time: '1 hora atrás',
          icon: Warning,
          color: 'warning'
        },
        {
          id: 4,
          type: 'error',
          message: 'Fallo en conector SMPP-2: Timeout de conexión',
          time: '2 horas atrás',
          icon: Error,
          color: 'error'
        }
      ]);

      setLoading(false);
    };

    loadMetrics();
    const interval = setInterval(loadMetrics, 30000); // Actualizar cada 30 segundos

    return () => clearInterval(interval);
  }, []);

  const MetricCard = ({ title, value, subtitle, trend, color = 'primary', icon: Icon }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          {Icon && (
            <Icon sx={{ fontSize: 40, color: `${color}.main`, opacity: 0.7 }} />
          )}
        </Box>
        {trend && (
          <Box display="flex" alignItems="center" mt={1}>
            {trend > 0 ? (
              <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
            ) : (
              <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
            )}
            <Typography
              variant="body2"
              color={trend > 0 ? 'success.main' : 'error.main'}
            >
              {Math.abs(trend)}% vs mes anterior
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Cargando dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Bienvenido, {user?.full_name || user?.username || 'Usuario'}
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            label={`Última actualización: ${metrics.lastUpdated?.toLocaleTimeString()}`}
            size="small"
            variant="outlined"
          />
          <IconButton onClick={() => window.location.reload()}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Métricas principales */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Mensajes"
            value={metrics.totalMessages.toLocaleString()}
            subtitle="Todos los tiempos"
            trend={12.5}
            color="primary"
            icon={Message}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Este Mes"
            value={metrics.messagesThisMonth.toLocaleString()}
            subtitle="Mensajes enviados"
            trend={8.2}
            color="success"
            icon={TrendingUp}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Tasa de Entrega"
            value={`${metrics.deliveryRate}%`}
            subtitle="Promedio mensual"
            trend={2.1}
            color="info"
            icon={CheckCircle}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Créditos"
            value={`$${metrics.creditBalance.toFixed(2)}`}
            subtitle="Balance actual"
            trend={-5.3}
            color="warning"
            icon={People}
          />
        </Grid>
      </Grid>

      {/* Segunda fila de métricas */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={6}>
          <MetricCard
            title="Campañas Activas"
            value={metrics.activeCampaigns}
            subtitle="En ejecución"
            color="secondary"
            icon={Campaign}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={6}>
          <MetricCard
            title="Conectores SMPP"
            value={`${metrics.activeConnectors}/8`}
            subtitle="Conectados"
            color="success"
            icon={Router}
          />
        </Grid>
      </Grid>

      {/* Actividad reciente */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Gráfico de Mensajes (Últimos 7 días)
            </Typography>
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'grey.50',
                borderRadius: 1
              }}
            >
              <Typography color="textSecondary">
                📊 Gráfico de métricas en tiempo real
                <br />
                (Integración con Chart.js pendiente)
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Actividad Reciente
            </Typography>
            <List dense>
              {recentActivity.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemIcon>
                      <activity.icon sx={{ color: `${activity.color}.main` }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.message}
                      secondary={activity.time}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ variant: 'caption' }}
                    />
                  </ListItem>
                  {index < recentActivity.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;