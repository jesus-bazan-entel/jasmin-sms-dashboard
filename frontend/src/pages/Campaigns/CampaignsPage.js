import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tabs,
  Tab,
  LinearProgress,
  Alert,
  Fab,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Stack
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Visibility as ViewIcon,
  MoreVert as MoreVertIcon,
  Campaign as CampaignIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
  Message as MessageIcon,
  Analytics as AnalyticsIcon,
  Send as SendIcon,
  Article as DraftIcon,
  CheckCircle as CompletedIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useSnackbar } from 'notistack';
import CampaignDialog from './CampaignDialog';

// Componente principal de gestión de campañas
const CampaignsPage = () => {
  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();
  
  // Estados locales
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [menuCampaign, setMenuCampaign] = useState(null);

  // Datos de ejemplo para las campañas
  const [campaignData, setCampaignData] = useState([
    {
      id: 1,
      name: "Promoción Black Friday 2024",
      status: "active",
      type: "promotional",
      contacts: 15420,
      sent: 12350,
      delivered: 11890,
      failed: 460,
      scheduled: "2024-11-29 09:00",
      created: "2024-11-20 14:30",
      message: "🔥 BLACK FRIDAY: 50% OFF en todos nuestros productos. Código: BF2024. Válido hasta el 30/11. ¡No te lo pierdas!",
      sender: "TIENDA",
      cost: 247.00,
      deliveryRate: 96.3
    },
    {
      id: 2,
      name: "Recordatorio Cita Médica",
      status: "completed",
      type: "transactional",
      contacts: 850,
      sent: 850,
      delivered: 847,
      failed: 3,
      scheduled: "2024-11-28 08:00",
      created: "2024-11-27 16:45",
      message: "Estimado paciente, le recordamos su cita médica mañana a las 10:00 AM. Consultorio Dr. García. Confirme su asistencia.",
      sender: "CLINICA",
      cost: 17.00,
      deliveryRate: 99.6
    },
    {
      id: 3,
      name: "Campaña Navideña",
      status: "draft",
      type: "promotional",
      contacts: 25000,
      sent: 0,
      delivered: 0,
      failed: 0,
      scheduled: "2024-12-15 10:00",
      created: "2024-11-28 11:20",
      message: "🎄 ¡Feliz Navidad! Disfruta de nuestras ofertas especiales navideñas. Envío gratis en compras superiores a $50.",
      sender: "NAVIDAD",
      cost: 500.00,
      deliveryRate: 0
    },
    {
      id: 4,
      name: "Verificación OTP",
      status: "active",
      type: "verification",
      contacts: 1200,
      sent: 1180,
      delivered: 1175,
      failed: 5,
      scheduled: "Inmediato",
      created: "2024-11-28 09:15",
      message: "Su código de verificación es: {OTP}. Válido por 5 minutos. No comparta este código con nadie.",
      sender: "VERIFY",
      cost: 24.00,
      deliveryRate: 99.6
    }
  ]);

  // Estadísticas generales
  const stats = {
    totalCampaigns: campaignData.length,
    activeCampaigns: campaignData.filter(c => c.status === 'active').length,
    totalSent: campaignData.reduce((sum, c) => sum + c.sent, 0),
    totalDelivered: campaignData.reduce((sum, c) => sum + c.delivered, 0),
    avgDeliveryRate: campaignData.reduce((sum, c) => sum + c.deliveryRate, 0) / campaignData.length,
    totalCost: campaignData.reduce((sum, c) => sum + c.cost, 0)
  };

  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      setCampaigns(campaignData);
      setLoading(false);
    }, 1000);
  }, []);

  // Funciones de manejo
  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handleMenuOpen = (event, campaign) => {
    setAnchorEl(event.currentTarget);
    setMenuCampaign(campaign);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuCampaign(null);
  };

  const handleCreateCampaign = () => {
    setSelectedCampaign(null);
    setOpenDialog(true);
  };

  const handleEditCampaign = (campaign) => {
    setSelectedCampaign(campaign);
    setOpenDialog(true);
    handleMenuClose();
  };

  const handleDeleteCampaign = (campaign) => {
    setCampaignData(prev => prev.filter(c => c.id !== campaign.id));
    enqueueSnackbar(`Campaña "${campaign.name}" eliminada`, { variant: 'success' });
    handleMenuClose();
  };

  const handleStartCampaign = (campaign) => {
    setCampaignData(prev => prev.map(c => 
      c.id === campaign.id ? { ...c, status: 'active' } : c
    ));
    enqueueSnackbar(`Campaña "${campaign.name}" iniciada`, { variant: 'success' });
    handleMenuClose();
  };

  const handlePauseCampaign = (campaign) => {
    setCampaignData(prev => prev.map(c => 
      c.id === campaign.id ? { ...c, status: 'paused' } : c
    ));
    enqueueSnackbar(`Campaña "${campaign.name}" pausada`, { variant: 'warning' });
    handleMenuClose();
  };

  const handleStopCampaign = (campaign) => {
    setCampaignData(prev => prev.map(c =>
      c.id === campaign.id ? { ...c, status: 'stopped' } : c
    ));
    enqueueSnackbar(`Campaña "${campaign.name}" detenida`, { variant: 'error' });
    handleMenuClose();
  };

  const handleSaveCampaign = (campaignData) => {
    if (selectedCampaign) {
      // Actualizar campaña existente
      setCampaignData(prev => prev.map(c =>
        c.id === selectedCampaign.id ? { ...campaignData, id: selectedCampaign.id } : c
      ));
    } else {
      // Crear nueva campaña
      setCampaignData(prev => [...prev, campaignData]);
    }
  };

  // Función para obtener el color del estado
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'info';
      case 'draft': return 'default';
      case 'stopped': return 'error';
      default: return 'default';
    }
  };

  // Función para obtener el icono del estado
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <PlayIcon />;
      case 'paused': return <PauseIcon />;
      case 'completed': return <CompletedIcon />;
      case 'draft': return <DraftIcon />;
      case 'stopped': return <StopIcon />;
      default: return <CampaignIcon />;
    }
  };

  // Función para obtener el texto del estado
  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Activa';
      case 'paused': return 'Pausada';
      case 'completed': return 'Completada';
      case 'draft': return 'Borrador';
      case 'stopped': return 'Detenida';
      default: return 'Desconocido';
    }
  };

  // Filtrar campañas según la pestaña seleccionada
  const getFilteredCampaigns = () => {
    switch (selectedTab) {
      case 0: return campaignData; // Todas
      case 1: return campaignData.filter(c => c.status === 'active'); // Activas
      case 2: return campaignData.filter(c => c.status === 'draft'); // Borradores
      case 3: return campaignData.filter(c => c.status === 'completed'); // Completadas
      default: return campaignData;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Gestión de Campañas SMS
        </Typography>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Cargando campañas...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Gestión de Campañas SMS
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateCampaign}
          size="large"
        >
          Nueva Campaña
        </Button>
      </Box>

      {/* Estadísticas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <CampaignIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.totalCampaigns}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Campañas
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <PlayIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.activeCampaigns}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Activas
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                  <SendIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.totalSent.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Mensajes Enviados
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <CheckCircle />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.totalDelivered.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Entregados
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <AnalyticsIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.avgDeliveryRate.toFixed(1)}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tasa Entrega
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                  $
                </Avatar>
                <Box>
                  <Typography variant="h6">${stats.totalCost.toFixed(2)}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Costo Total
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Pestañas de filtrado */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label={`Todas (${campaignData.length})`} />
          <Tab label={`Activas (${campaignData.filter(c => c.status === 'active').length})`} />
          <Tab label={`Borradores (${campaignData.filter(c => c.status === 'draft').length})`} />
          <Tab label={`Completadas (${campaignData.filter(c => c.status === 'completed').length})`} />
        </Tabs>
      </Card>

      {/* Tabla de campañas */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Lista de Campañas
            </Typography>
            <IconButton onClick={() => window.location.reload()}>
              <RefreshIcon />
            </IconButton>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Campaña</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell align="right">Contactos</TableCell>
                  <TableCell align="right">Enviados</TableCell>
                  <TableCell align="right">Entregados</TableCell>
                  <TableCell align="right">Tasa Entrega</TableCell>
                  <TableCell align="right">Costo</TableCell>
                  <TableCell>Programado</TableCell>
                  <TableCell align="center">Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {getFilteredCampaigns().map((campaign) => (
                  <TableRow key={campaign.id} hover>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {campaign.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 200 }}>
                          {campaign.message}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(campaign.status)}
                        label={getStatusText(campaign.status)}
                        color={getStatusColor(campaign.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={campaign.type === 'promotional' ? 'Promocional' : 
                               campaign.type === 'transactional' ? 'Transaccional' : 'Verificación'}
                        variant="outlined"
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {campaign.contacts.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      {campaign.sent.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      {campaign.delivered.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {campaign.deliveryRate.toFixed(1)}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={campaign.deliveryRate}
                          sx={{ width: 50, height: 4 }}
                          color={campaign.deliveryRate > 95 ? 'success' : campaign.deliveryRate > 85 ? 'warning' : 'error'}
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      ${campaign.cost.toFixed(2)}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {campaign.scheduled}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        onClick={(e) => handleMenuOpen(e, campaign)}
                        size="small"
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {getFilteredCampaigns().length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CampaignIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No hay campañas en esta categoría
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Crea una nueva campaña para comenzar
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Menú contextual */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => handleEditCampaign(menuCampaign)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => alert('Ver detalles de campaña')}>
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Ver Detalles</ListItemText>
        </MenuItem>

        <Divider />

        {menuCampaign?.status === 'draft' && (
          <MenuItem onClick={() => handleStartCampaign(menuCampaign)}>
            <ListItemIcon>
              <PlayIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Iniciar</ListItemText>
          </MenuItem>
        )}

        {menuCampaign?.status === 'active' && (
          <MenuItem onClick={() => handlePauseCampaign(menuCampaign)}>
            <ListItemIcon>
              <PauseIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Pausar</ListItemText>
          </MenuItem>
        )}

        {(menuCampaign?.status === 'active' || menuCampaign?.status === 'paused') && (
          <MenuItem onClick={() => handleStopCampaign(menuCampaign)}>
            <ListItemIcon>
              <StopIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Detener</ListItemText>
          </MenuItem>
        )}

        <Divider />

        <MenuItem onClick={() => handleDeleteCampaign(menuCampaign)} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Eliminar</ListItemText>
        </MenuItem>
      </Menu>

      {/* FAB para crear campaña */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateCampaign}
      >
        <AddIcon />
      </Fab>

      {/* Diálogo de campaña */}
      <CampaignDialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        campaign={selectedCampaign}
        onSave={handleSaveCampaign}
      />
    </Box>
  );
};

export default CampaignsPage;