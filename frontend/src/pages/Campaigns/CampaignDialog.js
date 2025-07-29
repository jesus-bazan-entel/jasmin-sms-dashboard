import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Box,
  Chip,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Close as CloseIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
  Message as MessageIcon,
  Settings as SettingsIcon,
  Preview as PreviewIcon,
  Send as SendIcon,
  Save as SaveIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { es } from 'date-fns/locale';
import { useSnackbar } from 'notistack';

const CampaignDialog = ({ open, onClose, campaign, onSave }) => {
  const { enqueueSnackbar } = useSnackbar();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    type: 'promotional',
    message: '',
    sender: '',
    contactLists: [],
    scheduledDate: null,
    isScheduled: false,
    priority: 'normal',
    validityPeriod: 24,
    deliveryReports: true,
    clickTracking: false,
    personalizedFields: [],
    maxRetries: 3,
    retryInterval: 5
  });

  const steps = ['Información Básica', 'Mensaje', 'Destinatarios', 'Programación', 'Configuración'];

  // Listas de contactos de ejemplo
  const contactLists = [
    { id: 1, name: 'Clientes VIP', count: 1250, description: 'Clientes con compras superiores a $500' },
    { id: 2, name: 'Newsletter Suscriptores', count: 8500, description: 'Usuarios suscritos al newsletter' },
    { id: 3, name: 'Clientes Inactivos', count: 3200, description: 'Sin compras en los últimos 6 meses' },
    { id: 4, name: 'Nuevos Registros', count: 450, description: 'Registrados en los últimos 30 días' },
    { id: 5, name: 'Cumpleañeros Mes', count: 180, description: 'Clientes que cumplen años este mes' }
  ];

  // Plantillas de mensaje predefinidas
  const messageTemplates = {
    promotional: [
      '🔥 ¡Oferta especial! {discount}% de descuento en {product}. Código: {code}. Válido hasta {date}.',
      '🎉 ¡Nueva colección disponible! Descubre las últimas tendencias en {category}. Envío gratis.',
      '💰 Black Friday: Hasta {discount}% OFF en toda la tienda. ¡No te lo pierdas!'
    ],
    transactional: [
      'Su pedido #{order_id} ha sido confirmado. Tiempo estimado de entrega: {delivery_time}.',
      'Recordatorio: Su cita está programada para {date} a las {time}. Confirme su asistencia.',
      'Su pago de ${amount} ha sido procesado exitosamente. Referencia: {reference}'
    ],
    verification: [
      'Su código de verificación es: {code}. Válido por {minutes} minutos.',
      'Código de seguridad: {code}. No comparta este código con nadie.',
      'Para completar su registro, ingrese el código: {code}'
    ]
  };

  useEffect(() => {
    if (campaign) {
      setFormData({
        name: campaign.name || '',
        type: campaign.type || 'promotional',
        message: campaign.message || '',
        sender: campaign.sender || '',
        contactLists: campaign.contactLists || [],
        scheduledDate: campaign.scheduledDate ? new Date(campaign.scheduledDate) : null,
        isScheduled: Boolean(campaign.scheduledDate),
        priority: campaign.priority || 'normal',
        validityPeriod: campaign.validityPeriod || 24,
        deliveryReports: campaign.deliveryReports !== false,
        clickTracking: campaign.clickTracking || false,
        personalizedFields: campaign.personalizedFields || [],
        maxRetries: campaign.maxRetries || 3,
        retryInterval: campaign.retryInterval || 5
      });
    } else {
      // Reset form for new campaign
      setFormData({
        name: '',
        type: 'promotional',
        message: '',
        sender: '',
        contactLists: [],
        scheduledDate: null,
        isScheduled: false,
        priority: 'normal',
        validityPeriod: 24,
        deliveryReports: true,
        clickTracking: false,
        personalizedFields: [],
        maxRetries: 3,
        retryInterval: 5
      });
      setActiveStep(0);
    }
  }, [campaign, open]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleContactListToggle = (listId) => {
    setFormData(prev => ({
      ...prev,
      contactLists: prev.contactLists.includes(listId)
        ? prev.contactLists.filter(id => id !== listId)
        : [...prev.contactLists, listId]
    }));
  };

  const handleTemplateSelect = (template) => {
    setFormData(prev => ({
      ...prev,
      message: template
    }));
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const validateStep = (step) => {
    switch (step) {
      case 0: // Información básica
        if (!formData.name.trim()) {
          enqueueSnackbar('El nombre de la campaña es requerido', { variant: 'error' });
          return false;
        }
        if (!formData.sender.trim()) {
          enqueueSnackbar('El remitente es requerido', { variant: 'error' });
          return false;
        }
        return true;
      
      case 1: // Mensaje
        if (!formData.message.trim()) {
          enqueueSnackbar('El mensaje es requerido', { variant: 'error' });
          return false;
        }
        if (formData.message.length > 160) {
          enqueueSnackbar('El mensaje no puede exceder 160 caracteres', { variant: 'warning' });
        }
        return true;
      
      case 2: // Destinatarios
        if (formData.contactLists.length === 0) {
          enqueueSnackbar('Debe seleccionar al menos una lista de contactos', { variant: 'error' });
          return false;
        }
        return true;
      
      case 3: // Programación
        if (formData.isScheduled && !formData.scheduledDate) {
          enqueueSnackbar('Debe seleccionar una fecha de programación', { variant: 'error' });
          return false;
        }
        return true;
      
      default:
        return true;
    }
  };

  const handleSave = () => {
    if (validateStep(activeStep)) {
      const selectedLists = contactLists.filter(list => formData.contactLists.includes(list.id));
      const totalContacts = selectedLists.reduce((sum, list) => sum + list.count, 0);
      
      const campaignData = {
        ...formData,
        id: campaign?.id || Date.now(),
        contacts: totalContacts,
        status: formData.isScheduled ? 'scheduled' : 'draft',
        created: campaign?.created || new Date().toISOString(),
        cost: totalContacts * 0.02, // $0.02 por mensaje
        sent: campaign?.sent || 0,
        delivered: campaign?.delivered || 0,
        failed: campaign?.failed || 0,
        deliveryRate: campaign?.deliveryRate || 0
      };

      onSave(campaignData);
      enqueueSnackbar(
        campaign ? 'Campaña actualizada exitosamente' : 'Campaña creada exitosamente',
        { variant: 'success' }
      );
      onClose();
    }
  };

  const getTotalContacts = () => {
    return contactLists
      .filter(list => formData.contactLists.includes(list.id))
      .reduce((sum, list) => sum + list.count, 0);
  };

  const getEstimatedCost = () => {
    return (getTotalContacts() * 0.02).toFixed(2);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0: // Información Básica
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nombre de la Campaña"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Ej: Promoción Black Friday 2024"
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Campaña</InputLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  label="Tipo de Campaña"
                >
                  <MenuItem value="promotional">Promocional</MenuItem>
                  <MenuItem value="transactional">Transaccional</MenuItem>
                  <MenuItem value="verification">Verificación</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Remitente (Sender ID)"
                value={formData.sender}
                onChange={(e) => handleInputChange('sender', e.target.value.toUpperCase())}
                placeholder="EMPRESA"
                inputProps={{ maxLength: 11 }}
                helperText="Máximo 11 caracteres alfanuméricos"
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Prioridad</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  label="Prioridad"
                >
                  <MenuItem value="low">Baja</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="high">Alta</MenuItem>
                  <MenuItem value="urgent">Urgente</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Período de Validez (horas)"
                value={formData.validityPeriod}
                onChange={(e) => handleInputChange('validityPeriod', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 72 }}
                helperText="Tiempo máximo para entregar el mensaje"
              />
            </Grid>
          </Grid>
        );

      case 1: // Mensaje
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Plantillas Predefinidas
              </Typography>
              <Box sx={{ mb: 2 }}>
                {messageTemplates[formData.type]?.map((template, index) => (
                  <Chip
                    key={index}
                    label={`Plantilla ${index + 1}`}
                    onClick={() => handleTemplateSelect(template)}
                    sx={{ mr: 1, mb: 1 }}
                    variant="outlined"
                  />
                ))}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Mensaje"
                value={formData.message}
                onChange={(e) => handleInputChange('message', e.target.value)}
                placeholder="Escriba su mensaje aquí..."
                helperText={`${formData.message.length}/160 caracteres`}
                inputProps={{ maxLength: 160 }}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Variables disponibles:</strong> {'{name}'}, {'{email}'}, {'{phone}'}, {'{company}'}, {'{discount}'}, {'{code}'}, {'{date}'}
                </Typography>
              </Alert>
            </Grid>

            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Vista Previa del Mensaje
                  </Typography>
                  <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      <strong>De:</strong> {formData.sender || 'SENDER'}<br />
                      <strong>Mensaje:</strong> {formData.message || 'Su mensaje aparecerá aquí...'}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      case 2: // Destinatarios
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Seleccionar Listas de Contactos
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Seleccione las listas de contactos que recibirán esta campaña
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <List>
                {contactLists.map((list) => (
                  <ListItem
                    key={list.id}
                    button
                    onClick={() => handleContactListToggle(list.id)}
                    selected={formData.contactLists.includes(list.id)}
                  >
                    <ListItemText
                      primary={list.name}
                      secondary={`${list.count.toLocaleString()} contactos - ${list.description}`}
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        edge="end"
                        checked={formData.contactLists.includes(list.id)}
                        onChange={() => handleContactListToggle(list.id)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Grid>

            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Resumen de Destinatarios
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Total de Contactos:
                      </Typography>
                      <Typography variant="h5" color="primary">
                        {getTotalContacts().toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Costo Estimado:
                      </Typography>
                      <Typography variant="h5" color="secondary">
                        ${getEstimatedCost()}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      case 3: // Programación
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.isScheduled}
                    onChange={(e) => handleInputChange('isScheduled', e.target.checked)}
                  />
                }
                label="Programar envío"
              />
            </Grid>

            {formData.isScheduled && (
              <Grid item xs={12}>
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
                  <DateTimePicker
                    label="Fecha y Hora de Envío"
                    value={formData.scheduledDate}
                    onChange={(date) => handleInputChange('scheduledDate', date)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                    minDateTime={new Date()}
                  />
                </LocalizationProvider>
              </Grid>
            )}

            <Grid item xs={12}>
              <Alert severity={formData.isScheduled ? "info" : "warning"}>
                {formData.isScheduled
                  ? `La campaña se enviará automáticamente el ${formData.scheduledDate?.toLocaleString()}`
                  : "La campaña se guardará como borrador y podrá enviarla manualmente"
                }
              </Alert>
            </Grid>
          </Grid>
        );

      case 4: // Configuración
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Configuración Avanzada
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.deliveryReports}
                    onChange={(e) => handleInputChange('deliveryReports', e.target.checked)}
                  />
                }
                label="Reportes de Entrega"
              />
              <Typography variant="body2" color="text.secondary">
                Recibir notificaciones sobre el estado de entrega de los mensajes
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.clickTracking}
                    onChange={(e) => handleInputChange('clickTracking', e.target.checked)}
                  />
                }
                label="Seguimiento de Enlaces"
              />
              <Typography variant="body2" color="text.secondary">
                Rastrear clics en enlaces incluidos en el mensaje
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Máximo de Reintentos"
                value={formData.maxRetries}
                onChange={(e) => handleInputChange('maxRetries', parseInt(e.target.value))}
                inputProps={{ min: 0, max: 5 }}
                helperText="Número de reintentos en caso de fallo"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Intervalo de Reintento (minutos)"
                value={formData.retryInterval}
                onChange={(e) => handleInputChange('retryInterval', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 60 }}
                helperText="Tiempo entre reintentos"
              />
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            {campaign ? 'Editar Campaña' : 'Nueva Campaña SMS'}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>

        <Box sx={{ mt: 3 }}>
          {renderStepContent(activeStep)}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button
          onClick={onClose}
          color="inherit"
        >
          Cancelar
        </Button>
        
        {activeStep > 0 && (
          <Button
            onClick={handleBack}
            color="inherit"
          >
            Anterior
          </Button>
        )}

        {activeStep < steps.length - 1 ? (
          <Button
            onClick={handleNext}
            variant="contained"
          >
            Siguiente
          </Button>
        ) : (
          <Button
            onClick={handleSave}
            variant="contained"
            startIcon={<SaveIcon />}
          >
            {campaign ? 'Actualizar' : 'Crear'} Campaña
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CampaignDialog;