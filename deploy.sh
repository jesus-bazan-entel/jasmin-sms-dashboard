#!/bin/bash

# Jasmin SMS Dashboard - Script de Despliegue Automatizado
# Para Debian 12 / Ubuntu 22.04+

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar si se ejecuta como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script no debe ejecutarse como root"
        print_info "Ejecuta: bash deploy.sh"
        exit 1
    fi
}

# Verificar sistema operativo
check_os() {
    if [[ -f /etc/debian_version ]]; then
        OS="debian"
        print_success "Sistema Debian/Ubuntu detectado"
    else
        print_error "Este script está diseñado para Debian/Ubuntu"
        exit 1
    fi
}

# Solicitar información del usuario
get_user_input() {
    print_header "CONFIGURACIÓN INICIAL"
    
    # Dominio
    read -p "Ingresa tu dominio (ej: midominio.com): " DOMAIN
    if [[ -z "$DOMAIN" ]]; then
        print_error "El dominio es requerido"
        exit 1
    fi
    
    # Email para SSL
    read -p "Ingresa tu email para certificados SSL: " EMAIL
    if [[ -z "$EMAIL" ]]; then
        print_error "El email es requerido"
        exit 1
    fi
    
    # Contraseña de base de datos
    read -s -p "Ingresa contraseña para la base de datos PostgreSQL: " DB_PASSWORD
    echo
    if [[ -z "$DB_PASSWORD" ]]; then
        print_error "La contraseña de base de datos es requerida"
        exit 1
    fi
    
    # Repositorio GitHub
    read -p "URL del repositorio GitHub (ej: https://github.com/usuario/jasmin-sms-dashboard.git): " REPO_URL
    if [[ -z "$REPO_URL" ]]; then
        print_error "La URL del repositorio es requerida"
        exit 1
    fi
    
    # Confirmar configuración
    echo -e "\n${YELLOW}Configuración:${NC}"
    echo "Dominio: $DOMAIN"
    echo "Email: $EMAIL"
    echo "Repositorio: $REPO_URL"
    echo "Base de datos: jasmin_sms_dashboard"
    echo "Usuario DB: jasmin_user"
    
    read -p "¿Es correcta la configuración? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        print_info "Configuración cancelada"
        exit 0
    fi
}

# Actualizar sistema
update_system() {
    print_header "ACTUALIZANDO SISTEMA"
    
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y curl wget git vim htop unzip software-properties-common \
        apt-transport-https ca-certificates gnupg lsb-release build-essential \
        python3-dev python3-pip python3-venv libpq-dev supervisor nginx \
        certbot python3-certbot-nginx ufw fail2ban
    
    print_success "Sistema actualizado"
}

# Configurar firewall
setup_firewall() {
    print_header "CONFIGURANDO FIREWALL"
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    
    print_success "Firewall configurado"
}

# Instalar Python 3.11
install_python() {
    print_header "INSTALANDO PYTHON 3.11"
    
    # Verificar si Python 3.11 ya está instalado
    if command -v python3.11 &> /dev/null; then
        print_success "Python 3.11 ya está instalado"
        return
    fi
    
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
    
    # Crear enlace simbólico
    sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
    
    print_success "Python 3.11 instalado"
}

# Instalar Node.js
install_nodejs() {
    print_header "INSTALANDO NODE.JS 18"
    
    # Verificar si Node.js ya está instalado
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $NODE_VERSION -ge 18 ]]; then
            print_success "Node.js $NODE_VERSION ya está instalado"
            return
        fi
    fi
    
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    print_success "Node.js instalado: $(node --version)"
}

# Instalar PostgreSQL
install_postgresql() {
    print_header "INSTALANDO POSTGRESQL"
    
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    
    # Configurar base de datos
    sudo -u postgres psql << EOF
CREATE DATABASE jasmin_sms_dashboard;
CREATE USER jasmin_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE jasmin_sms_dashboard TO jasmin_user;
ALTER DATABASE jasmin_sms_dashboard OWNER TO jasmin_user;
\q
EOF
    
    # Configurar autenticación
    sudo sed -i "s/#local   replication     all                                     peer/local   all             all                                     md5/" /etc/postgresql/*/main/pg_hba.conf
    sudo sed -i "s/local   all             all                                     peer/local   all             all                                     md5/" /etc/postgresql/*/main/pg_hba.conf
    
    sudo systemctl restart postgresql
    
    print_success "PostgreSQL configurado"
}

# Instalar Redis
install_redis() {
    print_header "INSTALANDO REDIS"
    
    sudo apt install -y redis-server
    
    # Configurar Redis
    sudo sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
    
    sudo systemctl restart redis-server
    sudo systemctl enable redis-server
    
    print_success "Redis configurado"
}

# Clonar y configurar aplicación
setup_application() {
    print_header "CONFIGURANDO APLICACIÓN"
    
    # Crear directorio
    sudo mkdir -p /opt/jasmin-sms-dashboard
    sudo chown $USER:$USER /opt/jasmin-sms-dashboard
    
    # Clonar repositorio
    cd /opt
    if [[ -d "jasmin-sms-dashboard" ]]; then
        print_info "Directorio existe, actualizando..."
        cd jasmin-sms-dashboard
        git pull origin main
    else
        git clone $REPO_URL jasmin-sms-dashboard
        cd jasmin-sms-dashboard
    fi
    
    # Configurar entorno Python
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Crear archivo .env
    cat > .env << EOF
# Aplicación
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
HOST=0.0.0.0
PORT=8000
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost

# Base de datos
DATABASE_URL=postgresql+asyncpg://jasmin_user:$DB_PASSWORD@localhost:5432/jasmin_sms_dashboard

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

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@$DOMAIN

# Configuración de producción
BASE_URL=https://$DOMAIN
EOF
    
    # Crear directorios necesarios
    mkdir -p logs uploads exports static media
    
    # Configurar base de datos
    if [[ -f "alembic.ini" ]]; then
        alembic upgrade head
    else
        print_warning "Alembic no configurado, saltando migraciones"
    fi
    
    print_success "Aplicación configurada"
}

# Construir frontend
build_frontend() {
    print_header "CONSTRUYENDO FRONTEND"
    
    cd /opt/jasmin-sms-dashboard/frontend
    
    # Crear archivo de configuración de producción
    cat > .env.production << EOF
REACT_APP_API_URL=https://$DOMAIN/api
REACT_APP_WS_URL=wss://$DOMAIN/ws
REACT_APP_VERSION=2.0.0
GENERATE_SOURCEMAP=false
EOF
    
    npm install
    npm run build
    
    print_success "Frontend construido"
}

# Configurar Nginx
setup_nginx() {
    print_header "CONFIGURANDO NGINX"
    
    # Crear configuración de Nginx
    sudo tee /etc/nginx/sites-available/jasmin-sms-dashboard > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # Certificados SSL (se configurarán con Certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Logs
    access_log /var/log/nginx/jasmin-sms-access.log;
    error_log /var/log/nginx/jasmin-sms-error.log;
    
    # Archivos estáticos
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
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
    
    # React Frontend
    location / {
        root /opt/jasmin-sms-dashboard/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Compresión
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
EOF
    
    # Habilitar sitio
    sudo ln -sf /etc/nginx/sites-available/jasmin-sms-dashboard /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Probar configuración
    sudo nginx -t
    sudo systemctl restart nginx
    
    print_success "Nginx configurado"
}

# Configurar SSL
setup_ssl() {
    print_header "CONFIGURANDO SSL"
    
    # Obtener certificado SSL
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    # Configurar renovación automática
    (sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -
    
    print_success "SSL configurado"
}

# Configurar servicios systemd
setup_services() {
    print_header "CONFIGURANDO SERVICIOS"
    
    # Cambiar propietario
    sudo chown -R www-data:www-data /opt/jasmin-sms-dashboard
    
    # Servicio API
    sudo tee /etc/systemd/system/jasmin-sms-api.service > /dev/null << EOF
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
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Servicio Celery Worker
    sudo tee /etc/systemd/system/jasmin-sms-worker.service > /dev/null << EOF
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
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Servicio Celery Beat
    sudo tee /etc/systemd/system/jasmin-sms-beat.service > /dev/null << EOF
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
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Recargar y habilitar servicios
    sudo systemctl daemon-reload
    sudo systemctl enable jasmin-sms-api jasmin-sms-worker jasmin-sms-beat
    sudo systemctl start jasmin-sms-api jasmin-sms-worker jasmin-sms-beat
    
    print_success "Servicios configurados"
}

# Configurar monitoreo
setup_monitoring() {
    print_header "CONFIGURANDO MONITOREO"
    
    # Script de monitoreo
    sudo tee /usr/local/bin/jasmin-sms-monitor.sh > /dev/null << 'EOF'
#!/bin/bash

services=("jasmin-sms-api" "jasmin-sms-worker" "jasmin-sms-beat" "postgresql" "redis-server" "nginx")

for service in "${services[@]}"; do
    if ! systemctl is-active --quiet $service; then
        echo "$(date): $service is not running" >> /var/log/jasmin-sms-dashboard/monitor.log
        systemctl restart $service
    fi
done

disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "$(date): Disk usage is ${disk_usage}%" >> /var/log/jasmin-sms-dashboard/monitor.log
fi
EOF
    
    sudo chmod +x /usr/local/bin/jasmin-sms-monitor.sh
    
    # Agregar a crontab
    (sudo crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/jasmin-sms-monitor.sh") | sudo crontab -
    
    # Script de backup
    sudo tee /usr/local/bin/jasmin-sms-backup.sh > /dev/null << EOF
#!/bin/bash

BACKUP_DIR="/opt/backups/jasmin-sms-dashboard"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

pg_dump -h localhost -U jasmin_user jasmin_sms_dashboard | gzip > \$BACKUP_DIR/db_backup_\$DATE.sql.gz
tar -czf \$BACKUP_DIR/config_backup_\$DATE.tar.gz /opt/jasmin-sms-dashboard/.env /etc/nginx/sites-available/jasmin-sms-dashboard
tar -czf \$BACKUP_DIR/media_backup_\$DATE.tar.gz /opt/jasmin-sms-dashboard/uploads /opt/jasmin-sms-dashboard/media

find \$BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "\$(date): Backup completed" >> /var/log/jasmin-sms-dashboard/backup.log
EOF
    
    sudo chmod +x /usr/local/bin/jasmin-sms-backup.sh
    
    # Backup diario
    (sudo crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/jasmin-sms-backup.sh") | sudo crontab -
    
    # Crear directorio de logs
    sudo mkdir -p /var/log/jasmin-sms-dashboard
    sudo chown www-data:www-data /var/log/jasmin-sms-dashboard
    
    print_success "Monitoreo configurado"
}

# Verificar instalación
verify_installation() {
    print_header "VERIFICANDO INSTALACIÓN"
    
    # Verificar servicios
    services=("jasmin-sms-api" "jasmin-sms-worker" "jasmin-sms-beat" "postgresql" "redis-server" "nginx")
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet $service; then
            print_success "$service está corriendo"
        else
            print_error "$service NO está corriendo"
        fi
    done
    
    # Verificar conectividad
    if curl -k -s https://$DOMAIN > /dev/null; then
        print_success "Sitio web accesible en https://$DOMAIN"
    else
        print_warning "Sitio web no accesible (puede tomar unos minutos)"
    fi
    
    # Verificar API
    if curl -k -s https://$DOMAIN/api/health > /dev/null; then
        print_success "API accesible en https://$DOMAIN/api"
    else
        print_warning "API no accesible (puede tomar unos minutos)"
    fi
}

# Mostrar información final
show_final_info() {
    print_header "INSTALACIÓN COMPLETADA"
    
    echo -e "${GREEN}🎉 ¡Jasmin SMS Dashboard instalado exitosamente!${NC}\n"
    
    echo -e "${BLUE}📋 INFORMACIÓN DE ACCESO:${NC}"
    echo "• Sitio web: https://$DOMAIN"
    echo "• API Docs: https://$DOMAIN/api/docs"
    echo "• Base de datos: jasmin_sms_dashboard"
    echo "• Usuario DB: jasmin_user"
    echo ""
    
    echo -e "${BLUE}🔧 COMANDOS ÚTILES:${NC}"
    echo "• Ver logs API: sudo journalctl -u jasmin-sms-api -f"
    echo "• Ver logs Worker: sudo journalctl -u jasmin-sms-worker -f"
    echo "• Reiniciar servicios: sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat"
    echo "• Backup manual: sudo /usr/local/bin/jasmin-sms-backup.sh"
    echo ""
    
    echo -e "${BLUE}📁 ARCHIVOS IMPORTANTES:${NC}"
    echo "• Configuración: /opt/jasmin-sms-dashboard/.env"
    echo "• Logs: /var/log/jasmin-sms-dashboard/"
    echo "• Backups: /opt/backups/jasmin-sms-dashboard/"
    echo "• Nginx config: /etc/nginx/sites-available/jasmin-sms-dashboard"
    echo ""
    
    echo -e "${YELLOW}⚠️  PRÓXIMOS PASOS:${NC}"
    echo "1. Editar /opt/jasmin-sms-dashboard/.env con tu configuración SMTP"
    echo "2. Instalar y configurar Jasmin SMS Gateway"
    echo "3. Crear tu primer usuario administrador"
    echo "4. Configurar conectores SMPP"
    echo ""
    
    echo -e "${BLUE}📚 DOCUMENTACIÓN:${NC}"
    echo "• Guía completa: DEPLOYMENT_GUIDE.md"
    echo "• README: README.md"
    echo ""
    
    print_success "¡Disfruta tu nueva plataforma SMS empresarial!"
}

# Función principal
main() {
    print_header "JASMIN SMS DASHBOARD - DESPLIEGUE AUTOMATIZADO"
    
    check_root
    check_os
    get_user_input
    
    update_system
    setup_firewall
    install_python
    install_nodejs
    install_postgresql
    install_redis
    setup_application
    build_frontend
    setup_nginx
    setup_ssl
    setup_services
    setup_monitoring
    
    sleep 5  # Esperar a que los servicios se inicien
    
    verify_installation
    show_final_info
}

# Ejecutar script principal
main "$@"