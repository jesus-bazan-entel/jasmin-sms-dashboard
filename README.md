# Jasmin SMS Dashboard - Enterprise Edition

Una plataforma empresarial completa para la gestión de SMS basada en **FastAPI** con integración directa a **Jasmin SMS Gateway**. Incluye dashboard en tiempo real, gestión visual de conectores SMPP, constructor de reglas de enrutamiento drag-and-drop, y funcionalidades empresariales avanzadas.

## 🚀 Características Principales

### **Dashboard Interactivo en Tiempo Real**
- **Estadísticas en Vivo**: Tráfico SMS (MT/MO), tasas de entrega (DLR), rendimiento de conectores
- **WebSockets**: Actualizaciones al segundo mediante conexiones WebSocket
- **Gráficos Históricos**: Análisis de tendencias personalizables (día, semana, mes)
- **Estado del Sistema**: Indicadores visuales de conectores SMPP, colas y servicios

### **Gestión Visual de Conectores SMPP**
- **Interfaz Intuitiva**: Añadir, configurar, iniciar/detener conectores visualmente
- **Logs en Tiempo Real**: PDUs y conexiones por conector para debugging
- **Alertas Automáticas**: Notificaciones por email/dashboard ante caídas
- **Monitoreo Avanzado**: Métricas de throughput y estado de conexión

### **Constructor Visual de Enrutamiento**
- **Drag & Drop**: Constructor visual de reglas de enrutamiento y filtros
- **Simulador de Rutas**: Herramienta para probar configuraciones antes de aplicar
- **Filtros Avanzados**: Por destino, sender ID, contenido, usuario, etc.
- **Balanceador de Carga**: Distribución inteligente entre conectores

### **Gestión Empresarial de Campañas**
- **Campañas Masivas**: Creación, programación y gestión de campañas SMS
- **Segmentación Avanzada**: Audiencias dinámicas basadas en atributos
- **Plantillas Personalizables**: Variables dinámicas y reutilización
- **Analítica Detallada**: Métricas de entrega, clics y conversiones

### **Sistema de Facturación y Créditos**
- **Gestión de Saldos**: Asignación y control de créditos por usuario
- **Subcuentas**: Gestión jerárquica de usuarios y departamentos
- **Facturación Automática**: Generación de facturas y reportes de consumo
- **Alertas de Saldo**: Notificaciones automáticas de saldo bajo

## 🏗️ Arquitectura Técnica

### **Backend - FastAPI**
- **API RESTful**: Documentación automática con OpenAPI/Swagger
- **WebSockets**: Comunicación en tiempo real para dashboard
- **Autenticación JWT**: Sistema RBAC (Role-Based Access Control)
- **Base de Datos**: PostgreSQL con SQLAlchemy async
- **Tareas en Background**: Celery + Redis para procesamiento

### **Integración Jasmin SMS Gateway**
- **Conexión Directa**: Interfaz Telnet (jcli) para comandos en tiempo real
- **API HTTP**: Envío de mensajes y webhooks de estado
- **Gestión de Conectores**: Control completo de conectores SMPP
- **Enrutamiento Dinámico**: Configuración visual de reglas de routing

### **Frontend - React.js**
- **SPA Moderna**: Interfaz completamente desacoplada del backend
- **Dashboard Interactivo**: Gráficos en tiempo real con Chart.js
- **Drag & Drop**: Constructor visual de reglas de enrutamiento
- **Responsive Design**: Optimizado para desktop y móvil

## 📋 Requisitos del Sistema

### **Software Requerido**
- **Python 3.8+**
- **PostgreSQL 12+**
- **Redis 6+**
- **Node.js 16+** (para frontend)
- **Jasmin SMS Gateway** (instalado y configurado)

### **Recursos Recomendados**
- **RAM**: 4GB mínimo, 8GB recomendado
- **CPU**: 2 cores mínimo, 4 cores recomendado
- **Almacenamiento**: 20GB mínimo para logs y base de datos
- **Red**: Conexión estable para conectores SMPP

## 🛠️ Instalación Rápida

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/jasmin-sms-dashboard.git
cd jasmin-sms-dashboard
```

### **2. Configurar Entorno Virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### **5. Configurar Base de Datos**
```bash
# Crear base de datos PostgreSQL
createdb jasmin_dashboard

# Ejecutar migraciones
alembic upgrade head
```

### **6. Iniciar Servicios**
```bash
# Terminal 1: API Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Worker Celery
celery -A app.tasks worker --loglevel=info

# Terminal 3: Scheduler Celery
celery -A app.tasks beat --loglevel=info

# Terminal 4: Frontend (en directorio frontend/)
npm install && npm start
```

## ⚙️ Configuración de Jasmin SMS Gateway

### **1. Instalación de Jasmin**
```bash
# Opción 1: Instalación directa
pip3 install jasmin

# Opción 2: Docker
docker run -d --name jasmin-sms \
  -p 2775:2775 -p 8990:8990 -p 1401:1401 \
  jookies/jasmin
```

### **2. Configuración Básica**
```bash
# Conectar a jcli
telnet localhost 8990
# Usuario: jcliadmin
# Password: jclipwd

# Crear usuario
jcli: user -a
> uid test_user
> gid test_group
> username testuser
> password testpass
> ok

# Crear conector SMPP
jcli: smppccm -a
> cid test_connector
> host smpp.provider.com
> port 2775
> username your_username
> password your_password
> ok

# Iniciar conector
jcli: smppccm -1 test_connector
```

### **3. Configuración en Dashboard**
1. Acceder a **http://localhost:3000**
2. Ir a **Conectores SMPP**
3. El conector aparecerá automáticamente
4. Configurar rutas y filtros según necesidades

## 🔧 Configuración Avanzada

### **Variables de Entorno Principales**

```bash
# Aplicación
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/jasmin_dashboard

# Jasmin SMS Gateway
JASMIN_HOST=localhost
JASMIN_TELNET_PORT=8990
JASMIN_HTTP_PORT=1401
JASMIN_USERNAME=jcliadmin
JASMIN_PASSWORD=jclipwd

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Email (para alertas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
```

### **Configuración de Roles y Permisos**

El sistema incluye 5 roles predefinidos:

- **Super Admin**: Acceso completo al sistema
- **Admin**: Gestión de usuarios y configuración
- **Campaign Manager**: Gestión de campañas y contactos
- **Analyst**: Solo lectura y reportes
- **Client**: Acceso limitado a sus propias campañas

## 📊 Funcionalidades Empresariales

### **1. Dashboard Principal**
- **Métricas en Tiempo Real**: SMS enviados, entregados, fallidos
- **Gráficos Interactivos**: Tendencias de tráfico y costos
- **Estado de Conectores**: Visualización del estado de todos los conectores SMPP
- **Alertas del Sistema**: Notificaciones de eventos importantes

### **2. Gestión de Conectores SMPP**
- **Configuración Visual**: Interfaz gráfica para configurar conectores
- **Monitoreo en Vivo**: Logs de PDUs y eventos de conexión
- **Gestión de Estado**: Iniciar, detener, reiniciar conectores
- **Alertas Automáticas**: Notificaciones ante fallos de conexión

### **3. Constructor de Reglas de Enrutamiento**
- **Interfaz Drag & Drop**: Crear reglas visualmente
- **Simulador**: Probar reglas antes de aplicar
- **Filtros Avanzados**: Múltiples criterios de filtrado
- **Balanceador de Carga**: Distribución inteligente de mensajes

### **4. Gestión de Campañas**
- **Creación Asistida**: Wizard para crear campañas paso a paso
- **Programación Avanzada**: Campañas recurrentes y programadas
- **Segmentación Dinámica**: Audiencias basadas en criterios múltiples
- **A/B Testing**: Pruebas de mensajes para optimización

### **5. Sistema de Facturación**
- **Gestión de Créditos**: Asignación y control de saldos
- **Facturación Automática**: Generación de facturas mensuales
- **Reportes de Consumo**: Análisis detallado de uso
- **Subcuentas**: Gestión jerárquica de usuarios

## 🔌 API y Integraciones

### **API RESTful**
La plataforma expone una API completa para integraciones:

```bash
# Documentación automática
http://localhost:8000/api/docs

# Endpoints principales
POST /api/v1/auth/login          # Autenticación
GET  /api/v1/campaigns           # Listar campañas
POST /api/v1/campaigns           # Crear campaña
POST /api/v1/messages/send       # Enviar SMS
GET  /api/v1/connectors          # Estado conectores
POST /api/v1/connectors/{id}/start # Iniciar conector
```

### **Webhooks**
Sistema de webhooks para notificaciones en tiempo real:

```json
{
  "event": "message.delivered",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "message_id": "uuid-here",
    "status": "delivered",
    "delivery_time": 2.5
  }
}
```

### **WebSocket Events**
Eventos en tiempo real para el dashboard:

```javascript
// Conectar a WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/client-id');

// Suscribirse a métricas
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['metrics', 'connectors', 'alerts']
}));
```

## 📈 Monitoreo y Alertas

### **Métricas del Sistema**
- **Throughput**: Mensajes por minuto/hora
- **Latencia**: Tiempo de entrega promedio
- **Tasa de Éxito**: Porcentaje de mensajes entregados
- **Uso de Recursos**: CPU, memoria, conexiones

### **Alertas Configurables**
- **Caída de Conectores**: Notificación inmediata
- **Saldo Bajo**: Alertas de créditos insuficientes
- **Throughput Bajo**: Rendimiento por debajo del umbral
- **Errores Críticos**: Fallos del sistema

### **Integración con Servicios Externos**
- **Slack**: Notificaciones en canales
- **Email**: Alertas por correo electrónico
- **Discord**: Webhooks para equipos
- **Telegram**: Bot para notificaciones móviles

## 🔒 Seguridad

### **Autenticación y Autorización**
- **JWT Tokens**: Autenticación stateless
- **RBAC**: Control de acceso basado en roles
- **API Keys**: Acceso programático seguro
- **Rate Limiting**: Protección contra abuso

### **Seguridad de Datos**
- **Encriptación**: Passwords hasheados con bcrypt
- **HTTPS**: Comunicación segura (producción)
- **Audit Logs**: Registro de todas las acciones
- **Backup Automático**: Respaldo de datos críticos

## 🚀 Despliegue en Producción

### **Docker Compose**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/jasmin_dashboard
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: jasmin_dashboard
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine

  worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    depends_on:
      - db
      - redis
```

### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:3000;  # React frontend
    }

    location /api/ {
        proxy_pass http://localhost:8000;  # FastAPI backend
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📚 Documentación Adicional

### **Guías de Usuario**
- [Configuración Inicial](docs/setup.md)
- [Gestión de Conectores](docs/connectors.md)
- [Creación de Campañas](docs/campaigns.md)
- [Constructor de Rutas](docs/routing.md)
- [Sistema de Facturación](docs/billing.md)

### **Documentación Técnica**
- [Arquitectura del Sistema](docs/architecture.md)
- [API Reference](docs/api.md)
- [Base de Datos](docs/database.md)
- [Integración Jasmin](docs/jasmin-integration.md)
- [Despliegue](docs/deployment.md)

## 🤝 Contribución

### **Desarrollo Local**
```bash
# Fork del repositorio
git clone https://github.com/tu-usuario/jasmin-sms-dashboard.git

# Crear rama para feature
git checkout -b feature/nueva-funcionalidad

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Ejecutar linting
black . && isort . && flake8
```

### **Estructura del Proyecto**
```
jasmin-sms-dashboard/
├── app/
│   ├── api/                 # Endpoints de la API
│   ├── core/               # Configuración y utilidades
│   ├── models/             # Modelos de base de datos
│   ├── services/           # Lógica de negocio
│   ├── tasks/              # Tareas de Celery
│   └── websocket/          # Gestión de WebSockets
├── frontend/               # Aplicación React
├── docs/                   # Documentación
├── tests/                  # Tests automatizados
├── alembic/               # Migraciones de BD
└── docker/                # Configuración Docker
```

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### **Canales de Soporte**
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/jasmin-sms-dashboard/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/tu-usuario/jasmin-sms-dashboard/wiki)
- **Email**: support@jasmin-dashboard.com
- **Discord**: [Servidor de la Comunidad](https://discord.gg/jasmin-dashboard)

### **FAQ**
**P: ¿Es compatible con otras gateways SMS?**
R: Actualmente está optimizado para Jasmin SMS Gateway, pero se puede extender para otras gateways SMPP.

**P: ¿Soporta múltiples idiomas?**
R: Sí, el sistema soporta internacionalización (i18n) con español, inglés, francés y alemán.

**P: ¿Qué tan escalable es el sistema?**
R: Diseñado para manejar millones de mensajes por día con arquitectura distribuida.

---

## 🌟 Características Destacadas

- ✅ **Dashboard en Tiempo Real** con WebSockets
- ✅ **Integración Directa** con Jasmin SMS Gateway
- ✅ **Constructor Visual** de reglas de enrutamiento
- ✅ **Gestión Empresarial** de campañas y facturación
- ✅ **API RESTful Completa** con documentación automática
- ✅ **Sistema RBAC** con múltiples roles
- ✅ **Frontend React** moderno y responsive
- ✅ **Alertas y Monitoreo** avanzado
- ✅ **Escalabilidad Empresarial** con Celery y Redis

**¡Transforma tu gestión de SMS con Jasmin SMS Dashboard Enterprise Edition!** 🚀