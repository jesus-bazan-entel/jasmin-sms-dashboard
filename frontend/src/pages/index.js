import React from 'react';
import PlaceholderPage from '../components/common/PlaceholderPage';

// Páginas de autenticación - LoginPage real
export { default as LoginPage } from './auth/LoginPage';
export const RegisterPage = () => <PlaceholderPage title="Registro" subtitle="Crear nueva cuenta" />;
export const ForgotPasswordPage = () => <PlaceholderPage title="Recuperar Contraseña" subtitle="Restablecer contraseña" />;

// Layout principal
export const DashboardLayout = () => <PlaceholderPage title="Dashboard Layout" subtitle="Layout principal del dashboard" />;

// Páginas principales
export const Dashboard = () => <PlaceholderPage title="Dashboard" subtitle="Panel principal con métricas en tiempo real" />;

// Campañas
export const Campaigns = () => <PlaceholderPage title="Campañas SMS" subtitle="Gestión de campañas de marketing" />;
export const CampaignDetail = () => <PlaceholderPage title="Detalle de Campaña" subtitle="Información detallada de la campaña" />;
export const CreateCampaign = () => <PlaceholderPage title="Crear Campaña" subtitle="Nueva campaña SMS" />;

// Contactos
export const Contacts = () => <PlaceholderPage title="Contactos" subtitle="Gestión de contactos y listas" />;
export const ContactDetail = () => <PlaceholderPage title="Detalle de Contacto" subtitle="Información del contacto" />;
export const ContactLists = () => <PlaceholderPage title="Listas de Contactos" subtitle="Organización de contactos" />;

// Mensajes
export const Messages = () => <PlaceholderPage title="Mensajes" subtitle="Historial de mensajes SMS" />;
export const MessageDetail = () => <PlaceholderPage title="Detalle de Mensaje" subtitle="Información del mensaje" />;

// Plantillas
export const Templates = () => <PlaceholderPage title="Plantillas" subtitle="Plantillas de mensajes SMS" />;
export const TemplateEditor = () => <PlaceholderPage title="Editor de Plantillas" subtitle="Crear y editar plantillas" />;

// Conectores
export const Connectors = () => <PlaceholderPage title="Conectores SMPP" subtitle="Gestión de conectores SMS" />;
export const ConnectorDetail = () => <PlaceholderPage title="Detalle de Conector" subtitle="Configuración del conector" />;

// Enrutamiento
export const Routing = () => <PlaceholderPage title="Enrutamiento" subtitle="Reglas de enrutamiento SMS" />;
export const RoutingBuilder = () => <PlaceholderPage title="Constructor de Rutas" subtitle="Editor visual de enrutamiento" />;

// Analytics y reportes
export const Analytics = () => <PlaceholderPage title="Analytics" subtitle="Análisis y métricas avanzadas" />;
export const Reports = () => <PlaceholderPage title="Reportes" subtitle="Informes y estadísticas" />;

// Facturación
export const Billing = () => <PlaceholderPage title="Facturación" subtitle="Gestión de créditos y pagos" />;
export const BillingDetail = () => <PlaceholderPage title="Detalle de Facturación" subtitle="Información de facturación" />;

// Usuarios
export const Users = () => <PlaceholderPage title="Usuarios" subtitle="Gestión de usuarios del sistema" />;
export const UserDetail = () => <PlaceholderPage title="Detalle de Usuario" subtitle="Información del usuario" />;

// API y Webhooks
export const ApiDocs = () => <PlaceholderPage title="Documentación API" subtitle="Documentación de la API REST" />;
export const Webhooks = () => <PlaceholderPage title="Webhooks" subtitle="Configuración de webhooks" />;

// Logs
export const Logs = () => <PlaceholderPage title="Logs del Sistema" subtitle="Registros y auditoría" />;

// Configuración
export const Settings = () => <PlaceholderPage title="Configuración" subtitle="Configuración del sistema" />;
export const Profile = () => <PlaceholderPage title="Perfil" subtitle="Configuración del perfil de usuario" />;

// Páginas de error
export const NotFound = () => <PlaceholderPage title="Página No Encontrada" subtitle="Error 404 - La página solicitada no existe" />;
export const Unauthorized = () => <PlaceholderPage title="No Autorizado" subtitle="Error 403 - No tienes permisos para acceder" />;
export const ServerError = () => <PlaceholderPage title="Error del Servidor" subtitle="Error 500 - Error interno del servidor" />;