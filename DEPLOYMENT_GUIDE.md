# Guía de Despliegue - Jasmin SMS Dashboard

Esta guía te llevará paso a paso desde subir tu proyecto a GitHub hasta tenerlo funcionando en un servidor Debian 12.

## 📋 Tabla de Contenidos

1. [Preparación del Proyecto](#1-preparación-del-proyecto)
2. [Subir a GitHub](#2-subir-a-github)
3. [Preparación del Servidor Debian 12](#3-preparación-del-servidor-debian-12)
4. [Instalación de Dependencias](#4-instalación-de-dependencias)
5. [Configuración de PostgreSQL](#5-configuración-de-postgresql)
6. [Configuración de Redis](#6-configuración-de-redis)
7. [Despliegue del Backend](#7-despliegue-del-backend)
8. [Despliegue del Frontend](#8-despliegue-del-frontend)
9. [Configuración de Nginx](#9-configuración-de-nginx)
10. [Configuración de Servicios Systemd](#10-configuración-de-servicios-systemd)
11. [SSL y Seguridad](#11-ssl-y-seguridad)
12. [Monitoreo y Mantenimiento](#12-monitoreo-y-mantenimiento)

---

## 1. Preparación del Proyecto

### 1.1 Limpiar archivos innecesarios

Antes de subir a GitHub, crea un archivo `.gitignore`:

```bash
# Crear .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# Uploads
uploads/
media/
static/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React build
frontend/build/
frontend/dist/

# Temporary files
*.tmp
*.temp

# Backup files
*.bak
*.backup

# Cache
.cache/
.pytest_cache/

# Coverage
.coverage
htmlcov/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Celery
celerybeat-schedule
celerybeat.pid

# Redis dump
dump.rdb

# Nginx logs
access.log
error.log
EOF
```

### 1.2 Crear archivo de requisitos del sistema

```bash
cat > SYSTEM_REQUIREMENTS.md << 'EOF'
# Requisitos del Sistema

## Software Requerido

### Sistema Operativo
- Debian 12 (Bookworm) o superior
- Ubuntu 22.04 LTS o superior

### Software Base
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Nginx 1.18+

### Recursos Mínimos
- RAM: 4GB (8GB recomendado)
- CPU: 2 cores (4 cores recomendado)
- Almacenamiento: 20GB (50GB recomendado)
- Ancho de banda: 100Mbps

### Puertos Requeridos
- 80 (HTTP)
- 443 (HTTPS)
- 8000 (API Backend - interno)
- 5432 (PostgreSQL - interno)
- 6379 (Redis - interno)
EOF
```

---

## 2. Subir a GitHub

### 2.1 Inicializar repositorio Git

```bash
# Navegar al directorio del proyecto
cd jasmin-sms-dashboard

# Inicializar Git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "Initial commit: Jasmin SMS Dashboard Enterprise Edition

- FastAPI backend with WebSocket support
- React frontend with Material-UI
- PostgreSQL database with SQLAlchemy
- Celery background tasks
- Jasmin SMS Gateway integration
- RBAC authentication system
- Real-time dashboard and metrics
- Drag-and-drop routing builder
- Enterprise billing system"
```

### 2.2 Crear repositorio en GitHub

1. **Ir a GitHub.com** y hacer login
2. **Hacer clic en "New repository"**
3. **Configurar el repositorio:**
   - Repository name: `jasmin-sms-dashboard`
   - Description: `Enterprise SMS Management Platform with Jasmin SMS Gateway Integration`
   - Visibility: `Private` (recomendado para proyectos empresariales)
   - ✅ Add a README file: **NO** (ya tenemos uno)
   - ✅ Add .gitignore: **NO** (ya tenemos uno)
   - ✅ Choose a license: `MIT License` (opcional)

4. **Hacer clic en "Create repository"**

### 2.3 Conectar repositorio local con GitHub

```bash
# Agregar remote origin (reemplaza 'tu-usuario' con tu username de GitHub)
git remote add origin https://github.com/tu-usuario/jasmin-sms-dashboard.git

# Verificar remote
git remote -v

# Subir código a GitHub
git branch -M main
git push -u origin main
```

### 2.4 Configurar ramas de desarrollo (opcional pero recomendado)

```bash
# Crear rama de desarrollo
git checkout -b develop
git push -u origin develop

# Crear rama de producción
git checkout -b production
git push -u origin production

# Volver a main
git checkout main
```

---

## 3. Preparación del Servidor Debian 12

### 3.1 Conectar al servidor

```bash
# Conectar vía SSH (reemplaza con tu IP y usuario)
ssh usuario@tu-servidor-ip

# O si usas una clave SSH
ssh -i /ruta/a/tu/clave.pem usuario@tu-servidor-ip
```

### 3.2 Actualizar el sistema

```bash
# Actualizar lista de paquetes
sudo apt update

# Actualizar sistema
sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y curl wget git vim htop unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

### 3.3 Configurar firewall básico

```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Configurar reglas básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP y HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Habilitar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

---

## 4. Instalación de Dependencias

### 4.1 Instalar Python 3.9+

```bash
# Verificar versión de Python
python3 --version

# Si necesitas una versión más nueva, agregar repositorio deadsnakes
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.11 (recomendado)
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Crear enlace simbólico
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
```

### 4.2 Instalar Node.js 18+

```bash
# Agregar repositorio oficial de Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Instalar Node.js
sudo apt install -y nodejs

# Verificar instalación
node --version
npm --version
```

### 4.3 Instalar herramientas de desarrollo

```bash
# Herramientas de compilación
sudo apt install -y build-essential

# Herramientas para Python
sudo apt install -y python3-dev python3-pip python3-venv

# Herramientas para PostgreSQL
sudo apt install -y libpq-dev

# Herramientas adicionales
sudo apt install -y supervisor nginx certbot python3-certbot-nginx
```

---

## 5. Configuración de PostgreSQL

### 5.1 Instalar PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Verificar que esté corriendo
sudo systemctl status postgresql

# Habilitar inicio automático
sudo systemctl enable postgresql
```

### 5.2 Configurar PostgreSQL

```bash
# Cambiar a usuario postgres
sudo -u postgres psql

# Dentro de PostgreSQL, ejecutar:
```

```sql
-- Crear base de datos
CREATE DATABASE jasmin_sms_dashboard;

-- Crear usuario
CREATE USER jasmin_user WITH PASSWORD 'tu_password_seguro_aqui';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE jasmin_sms_dashboard TO jasmin_user;

-- Hacer al usuario propietario de la base de datos
ALTER DATABASE jasmin_sms_dashboard OWNER TO jasmin_user;

-- Salir
\q
```

```bash
# Configurar PostgreSQL para conexiones locales
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Cambiar la línea:
# local   all             all                                     peer
# Por:
# local   all             all                                     md5

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Probar conexión
psql -h localhost -U jasmin_user -d jasmin_sms_dashboard
```

---

## 6. Configuración de Redis

### 6.1 Instalar Redis

```bash
# Instalar Redis
sudo apt install -y redis-server

# Configurar Redis
sudo nano /etc/redis/redis.conf

# Buscar y modificar estas líneas:
# supervised no -> supervised systemd
# bind 127.0.0.1 ::1 (asegurar que esté descomentado)

# Reiniciar Redis
sudo systemctl restart redis-server

# Habilitar inicio automático
sudo systemctl enable redis-server

# Verificar estado
sudo systemctl status redis-server

# Probar Redis
redis-cli ping
```

---

## 7. Despliegue del Backend

### 7.1 Clonar el repositorio

```bash
# Crear directorio para aplicaciones
sudo mkdir -p /opt/jasmin-sms-dashboard
sudo chown $USER:$USER /opt/jasmin-sms-dashboard

# Clonar repositorio
cd /opt
git clone https://github.com/tu-usuario/jasmin-sms-dashboard.git

# Cambiar al directorio del proyecto
cd jasmin-sms-dashboard
```

### 7.2 Configurar entorno Python

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 7.3 Configurar variables de entorno

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración
nano .env
```

Configurar las siguientes variables en `.env`:

```bash
# Aplicación
SECRET_KEY=tu_clave_secreta_super_segura_de_32_caracteres_minimo
DEBUG=False
HOST=0.0.0.0
PORT=8000
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,localhost

# Base de datos
DATABASE_URL=postgresql+asyncpg://jasmin_user:tu_password_seguro_aqui@localhost:5432/jasmin_sms_dashboard

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Jasmin SMS Gateway
JASMIN_HOST=localhost
JASMIN_TELNET_PORT=8990
JASMIN_HTTP_PORT=1401
JASMIN_USERNAME=jcliadmin
JASMIN_PASSWORD=jclipwd

# Email (configurar con tu proveedor)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=noreply@tu-dominio.com

# Configuración de producción
BASE_URL=https://tu-dominio.com
```

### 7.4 Configurar base de datos

```bash
# Instalar Alembic si no está incluido
pip install alembic

# Inicializar migraciones (si no existen)
alembic init alembic

# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

### 7.5 Crear directorios necesarios

```bash
# Crear directorios
mkdir -p logs uploads exports static media

# Configurar permisos
chmod 755 logs uploads exports static media
```

---

## 8. Despliegue del Frontend

### 8.1 Instalar dependencias del frontend

```bash
# Ir al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno para producción
cat > .env.production << 'EOF'
REACT_APP_API_URL=https://tu-dominio.com/api
REACT_APP_WS_URL=wss://tu-dominio.com/ws
REACT_APP_VERSION=2.0.0
GENERATE_SOURCEMAP=false
EOF
```

### 8.2 Construir frontend para producción

```bash
# Construir aplicación
npm run build

# Verificar que se creó la carpeta build
ls -la build/

# Volver al directorio raíz
cd ..
```

---

## 9. Configuración de Nginx

### 9.1 Crear configuración de Nginx

```bash
# Crear archivo de configuración
sudo nano /etc/nginx/sites-available/jasmin-sms-dashboard
```

Contenido del archivo:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    
    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;
    
    # Certificados SSL (se configurarán con Certbot)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Configuración de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Logs
    access_log /var/log/nginx/jasmin-sms-access.log;
    error_log /var/log/nginx/jasmin-sms-error.log;
    
    # Configuración de archivos estáticos
    location /static/ {
        alias /opt/jasmin-sms-dashboard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/jasmin-sms-dashboard/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # React Frontend
    location / {
        root /opt/jasmin-sms-dashboard/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache para archivos estáticos
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Configuración de compresión
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
}
```

### 9.2 Habilitar sitio

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/jasmin-sms-dashboard /etc/nginx/sites-enabled/

# Deshabilitar sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# Probar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 10. Configuración de Servicios Systemd

### 10.1 Crear servicio para FastAPI

```bash
sudo nano /etc/systemd/system/jasmin-sms-api.service
```

Contenido:

```ini
[Unit]
Description=Jasmin SMS Dashboard API
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/jasmin-sms-dashboard
Environment=PATH=/opt/jasmin-sms-dashboard/venv/bin
ExecStart=/opt/jasmin-sms-dashboard/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 10.2 Crear servicio para Celery Worker

```bash
sudo nano /etc/systemd/system/jasmin-sms-worker.service
```

Contenido:

```ini
[Unit]
Description=Jasmin SMS Dashboard Celery Worker
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/jasmin-sms-dashboard
Environment=PATH=/opt/jasmin-sms-dashboard/venv/bin
ExecStart=/opt/jasmin-sms-dashboard/venv/bin/celery -A app.tasks worker --loglevel=info --concurrency=4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 10.3 Crear servicio para Celery Beat

```bash
sudo nano /etc/systemd/system/jasmin-sms-beat.service
```

Contenido:

```ini
[Unit]
Description=Jasmin SMS Dashboard Celery Beat
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/jasmin-sms-dashboard
Environment=PATH=/opt/jasmin-sms-dashboard/venv/bin
ExecStart=/opt/jasmin-sms-dashboard/venv/bin/celery -A app.tasks beat --loglevel=info --schedule=/tmp/celerybeat-schedule
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 10.4 Configurar permisos y habilitar servicios

```bash
# Cambiar propietario del directorio
sudo chown -R www-data:www-data /opt/jasmin-sms-dashboard

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicios
sudo systemctl enable jasmin-sms-api
sudo systemctl enable jasmin-sms-worker
sudo systemctl enable jasmin-sms-beat

# Iniciar servicios
sudo systemctl start jasmin-sms-api
sudo systemctl start jasmin-sms-worker
sudo systemctl start jasmin-sms-beat

# Verificar estado
sudo systemctl status jasmin-sms-api
sudo systemctl status jasmin-sms-worker
sudo systemctl status jasmin-sms-beat
```

---

## 11. SSL y Seguridad

### 11.1 Instalar certificado SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado (reemplaza con tu dominio)
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run

# Configurar renovación automática
sudo crontab -e

# Agregar línea para renovación automática:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 11.2 Configurar firewall adicional

```bash
# Permitir solo puertos necesarios
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 'Nginx HTTP'

# Verificar reglas
sudo ufw status numbered
```

### 11.3 Configurar fail2ban (opcional pero recomendado)

```bash
# Instalar fail2ban
sudo apt install -y fail2ban

# Crear configuración personalizada
sudo nano /etc/fail2ban/jail.local
```

Contenido:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
```

```bash
# Reiniciar fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

---

## 12. Monitoreo y Mantenimiento

### 12.1 Configurar logs

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/jasmin-sms-dashboard

# Configurar logrotate
sudo nano /etc/logrotate.d/jasmin-sms-dashboard
```

Contenido:

```
/var/log/jasmin-sms-dashboard/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload jasmin-sms-api
    endscript
}
```

### 12.2 Script de monitoreo

```bash
# Crear script de monitoreo
sudo nano /usr/local/bin/jasmin-sms-monitor.sh
```

Contenido:

```bash
#!/bin/bash

# Verificar servicios
services=("jasmin-sms-api" "jasmin-sms-worker" "jasmin-sms-beat" "postgresql" "redis-server" "nginx")

for service in "${services[@]}"; do
    if ! systemctl is-active --quiet $service; then
        echo "$(date): $service is not running" >> /var/log/jasmin-sms-dashboard/monitor.log
        systemctl restart $service
    fi
done

# Verificar espacio en disco
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "$(date): Disk usage is ${disk_usage}%" >> /var/log/jasmin-sms-dashboard/monitor.log
fi

# Verificar memoria
mem_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$mem_usage > 90" | bc -l) )); then
    echo "$(date): Memory usage is ${mem_usage}%" >> /var/log/jasmin-sms-dashboard/monitor.log
fi
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/jasmin-sms-monitor.sh

# Agregar a crontab
sudo crontab -e

# Agregar línea para ejecutar cada 5 minutos:
*/5 * * * * /usr/local/bin/jasmin-sms-monitor.sh
```

### 12.3 Backup automático

```bash
# Crear script de backup
sudo nano /usr/local/bin/jasmin-sms-backup.sh
```

Contenido:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/jasmin-sms-dashboard"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump -h localhost -U jasmin_user jasmin_sms_dashboard | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup de archivos de configuración
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz /opt/jasmin-sms-dashboard/.env /etc/nginx/sites-available/jasmin-sms-dashboard

# Backup de uploads y media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/jasmin-sms-dashboard/uploads /opt/jasmin-sms-dashboard/media

# Limpiar backups antiguos (mantener solo 7 días)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "$(date): Backup completed" >> /var/log/jasmin-sms-dashboard/backup.log
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/jasmin-sms-backup.sh

# Agregar a crontab para backup diario a las 2 AM
sudo crontab -e

# Agregar línea:
0 2 * * * /usr/local/bin/jasmin-sms-backup.sh
```

---

## 🚀 Verificación Final

### Verificar que todo funciona:

```bash
# 1. Verificar servicios
sudo systemctl status jasmin-sms-api jasmin-sms-worker jasmin-sms-beat postgresql redis-server nginx

# 2. Verificar logs
sudo journalctl -u jasmin-sms-api -f

# 3. Verificar conectividad
curl -k https://tu-dominio.com/api/health

# 4. Verificar base de datos
psql -h localhost -U jasmin_user -d jasmin_sms_dashboard -c "SELECT version();"

# 5. Verificar Redis
redis-cli ping
```

### Acceder a la aplicación:

- **Frontend**: https://tu-dominio.com
- **API Docs**: https://tu-dominio.com/api/docs
- **Admin Panel**: https://tu-dominio.com/admin

---

## 🔧 Comandos Útiles de Mantenimiento

```bash
# Reiniciar todos los servicios
sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Ver logs en tiempo real
sudo journalctl -u jasmin-sms-api -f

# Actualizar código desde GitHub
cd /opt/jasmin-sms-dashboard
git pull origin main
sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Backup manual
sudo /usr/local/bin/jasmin-sms-backup.sh

# Verificar espacio en disco
df -h

# Verificar memoria
free -h

# Verificar procesos
htop
```

---

## 🆘 Solución de Problemas Comunes

### Problema: Servicio no inicia
```bash
# Ver logs detallados
sudo journalctl -u jasmin-sms-api -n 50

# Verificar configuración
sudo nginx -t
```

### Problema: Base de datos no conecta
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"
```

### Problema: Frontend no carga
```bash
# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx

# Verificar archivos del frontend
ls -la /opt/jasmin-sms-dashboard/frontend/build/
```

---

¡Tu aplicación Jasmin SMS Dashboard ahora está desplegada y funcionando en producción! 🎉