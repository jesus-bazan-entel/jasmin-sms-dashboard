# 🚀 Guía de Inicio - Jasmin SMS Dashboard

## Cómo Iniciar el Backend y Frontend en Producción

Esta guía te llevará paso a paso para poner en funcionamiento tanto el backend FastAPI como el frontend React en tu servidor Debian 12.

---

## 📋 Requisitos Previos

### Verificar que tienes instalado:
```bash
# Python 3.11+
python3 --version

# Node.js 18+
node --version
npm --version

# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis-server
```

---

## 🔧 PASO 1: Configurar el Backend FastAPI

### 1.1 Instalar Dependencias Python
```bash
cd /opt/jasmin-sms-dashboard

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 1.2 Configurar Variables de Entorno
```bash
# Crear archivo de configuración
cp .env.example .env

# Editar configuración
nano .env
```

**Contenido del archivo `.env`:**
```bash
# Base de datos
DATABASE_URL=postgresql://jasmin_user:tu_password_segura@localhost/jasmin_sms_dashboard

# Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=noreply@tu-dominio.com

# Jasmin SMS Gateway
JASMIN_HOST=localhost
JASMIN_PORT=8990
JASMIN_USERNAME=jcliadmin
JASMIN_PASSWORD=jclipwd

# Configuración de la aplicación
DEBUG=False
ENVIRONMENT=production
```

### 1.3 Configurar Base de Datos PostgreSQL
```bash
# Conectar a PostgreSQL como superusuario
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE jasmin_sms_dashboard;
CREATE USER jasmin_user WITH PASSWORD 'tu_password_segura';
GRANT ALL PRIVILEGES ON DATABASE jasmin_sms_dashboard TO jasmin_user;
\q

# Ejecutar migraciones
source venv/bin/activate
alembic upgrade head
```

### 1.4 Crear Usuario Administrador
```bash
# Ejecutar script para crear admin
python3 -c "
import asyncio
from app.models.user import User, UserRole
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Verificar si ya existe un admin
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == 'admin@jasmin.com'))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print('Usuario administrador ya existe')
            return
            
        admin = User(
            email='admin@jasmin.com',
            username='admin',
            full_name='Administrador del Sistema',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        db.add(admin)
        await db.commit()
        print('Usuario administrador creado: admin@jasmin.com / admin123')

asyncio.run(create_admin())
"
```

---

## 🚀 PASO 2: Iniciar el Backend

### 2.1 Modo Desarrollo (para pruebas)
```bash
cd /opt/jasmin-sms-dashboard
source venv/bin/activate

# Iniciar servidor de desarrollo
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2.2 Modo Producción con Systemd

**Crear servicio systemd para la API:**
```bash
sudo nano /etc/systemd/system/jasmin-sms-api.service
```

**Contenido del archivo:**
```ini
[Unit]
Description=Jasmin SMS Dashboard API
After=network.target postgresql.service redis-server.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/jasmin-sms-dashboard
Environment=PATH=/opt/jasmin-sms-dashboard/venv/bin
ExecStart=/opt/jasmin-sms-dashboard/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Crear servicio para Celery Worker:**
```bash
sudo nano /etc/systemd/system/jasmin-sms-worker.service
```

**Contenido del archivo:**
```ini
[Unit]
Description=Jasmin SMS Dashboard Celery Worker
After=network.target redis-server.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/jasmin-sms-dashboard
Environment=PATH=/opt/jasmin-sms-dashboard/venv/bin
ExecStart=/opt/jasmin-sms-dashboard/venv/bin/celery -A app.tasks worker --loglevel=info --concurrency=4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Crear servicio para Celery Beat:**
```bash
sudo nano /etc/systemd/system/jasmin-sms-beat.service
```

**Contenido del archivo:**
```ini
[Unit]
Description=Jasmin SMS Dashboard Celery Beat
After=network.target redis-server.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/jasmin-sms-dashboard
Environment=PATH=/opt/jasmin-sms-dashboard/venv/bin
ExecStart=/opt/jasmin-sms-dashboard/venv/bin/celery -A app.tasks beat --loglevel=info
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Activar y iniciar servicios:**
```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicios para inicio automático
sudo systemctl enable jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Iniciar servicios
sudo systemctl start jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Verificar estado
sudo systemctl status jasmin-sms-api jasmin-sms-worker jasmin-sms-beat
```

---

## 🌐 PASO 3: Configurar el Frontend

### 3.1 Compilar Frontend para Producción
```bash
cd /opt/jasmin-sms-dashboard/frontend

# Instalar dependencias
npm install

# Configurar variables de entorno para producción
nano .env.production
```

**Contenido de `.env.production`:**
```bash
REACT_APP_API_URL=https://tu-dominio.com/api
REACT_APP_WS_URL=wss://tu-dominio.com/ws
REACT_APP_VERSION=2.0.0
GENERATE_SOURCEMAP=false
```

**Compilar para producción:**
```bash
npm run build
```

### 3.2 Configurar Nginx

**Crear configuración de Nginx:**
```bash
sudo nano /etc/nginx/sites-available/jasmin-sms-dashboard
```

**Contenido del archivo:**
```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Frontend (React)
    location / {
        root /opt/jasmin-sms-dashboard/frontend/build;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Logs
    access_log /var/log/nginx/jasmin-sms-dashboard.access.log;
    error_log /var/log/nginx/jasmin-sms-dashboard.error.log;
}
```

**Activar sitio:**
```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/jasmin-sms-dashboard /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 🔒 PASO 4: Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 🔥 PASO 5: Configurar Firewall

```bash
# Configurar UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Verificar estado
sudo ufw status
```

---

## ✅ PASO 6: Verificar que Todo Funciona

### 6.1 Verificar Servicios Backend
```bash
# Verificar servicios
sudo systemctl status jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Ver logs en tiempo real
sudo journalctl -u jasmin-sms-api -f
```

### 6.2 Verificar Frontend
```bash
# Probar sitio web
curl -I https://tu-dominio.com

# Probar API
curl https://tu-dominio.com/api/health
```

### 6.3 Acceder a la Aplicación
- **Frontend**: https://tu-dominio.com
- **API Docs**: https://tu-dominio.com/api/docs
- **API Redoc**: https://tu-dominio.com/api/redoc

**Credenciales de acceso:**
- **Email**: admin@jasmin.com
- **Password**: admin123

---

## 🛠️ PASO 7: Comandos Útiles de Administración

### Gestión de Servicios
```bash
# Reiniciar todos los servicios
sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat nginx

# Ver logs
sudo journalctl -u jasmin-sms-api -n 50
sudo tail -f /var/log/nginx/jasmin-sms-dashboard.error.log

# Verificar puertos
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Actualizar Aplicación
```bash
# Actualizar código
cd /opt/jasmin-sms-dashboard
git pull origin main

# Actualizar backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Actualizar frontend
cd frontend
npm install
npm run build
sudo systemctl reload nginx
```

---

## 🚨 Solución de Problemas

### Backend no inicia
```bash
# Verificar logs
sudo journalctl -u jasmin-sms-api -n 50

# Verificar base de datos
sudo -u postgres psql -c "\l" | grep jasmin

# Verificar Redis
redis-cli ping
```

### Frontend no carga
```bash
# Verificar archivos build
ls -la /opt/jasmin-sms-dashboard/frontend/build/

# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Problemas de SSL
```bash
# Renovar certificados
sudo certbot renew

# Verificar certificados
sudo certbot certificates
```

---

## 🎉 ¡Listo!

Tu **Jasmin SMS Dashboard Enterprise Edition** está ahora funcionando en producción con:

- ✅ **Backend FastAPI** corriendo en puerto 8000
- ✅ **Frontend React** servido por Nginx
- ✅ **Base de datos PostgreSQL** configurada
- ✅ **Redis** para tareas background
- ✅ **SSL/HTTPS** habilitado
- ✅ **Servicios systemd** para inicio automático
- ✅ **Firewall** configurado
- ✅ **Logs** centralizados

**Accede a tu dashboard en**: https://tu-dominio.com

¡Disfruta tu plataforma SMS empresarial! 🚀📱