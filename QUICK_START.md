# 🚀 Guía Rápida de Despliegue - Jasmin SMS Dashboard

## Resumen Ejecutivo

Esta guía te llevará desde cero hasta tener tu plataforma SMS empresarial funcionando en producción en **menos de 30 minutos**.

---

## 📋 Requisitos Previos

### Servidor
- **VPS/Servidor**: Debian 12 o Ubuntu 22.04+
- **RAM**: 4GB mínimo (8GB recomendado)
- **CPU**: 2 cores mínimo (4 cores recomendado)
- **Almacenamiento**: 20GB mínimo (50GB recomendado)
- **Acceso**: SSH con sudo

### Dominio
- **Dominio registrado** apuntando a tu servidor
- **Acceso DNS** para configurar registros A

### Información Necesaria
- URL de tu repositorio GitHub
- Email para certificados SSL
- Contraseña segura para PostgreSQL

---

## 🎯 Opción 1: Despliegue Automatizado (Recomendado)

### Paso 1: Subir Código a GitHub

```bash
# En tu máquina local, dentro del proyecto
cd jasmin-sms-dashboard

# Inicializar Git (si no está inicializado)
git init
git add .
git commit -m "Initial commit: Jasmin SMS Dashboard Enterprise Edition"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/jasmin-sms-dashboard.git
git branch -M main
git push -u origin main
```

### Paso 2: Conectar al Servidor

```bash
# Conectar vía SSH
ssh usuario@tu-servidor-ip

# O con clave SSH
ssh -i /ruta/a/tu/clave.pem usuario@tu-servidor-ip
```

### Paso 3: Ejecutar Script Automatizado

```bash
# Descargar script de despliegue
wget https://raw.githubusercontent.com/TU-USUARIO/jasmin-sms-dashboard/main/deploy.sh

# Hacer ejecutable
chmod +x deploy.sh

# Ejecutar (seguir las instrucciones en pantalla)
bash deploy.sh
```

**El script te pedirá:**
- Tu dominio (ej: midominio.com)
- Email para SSL
- Contraseña de PostgreSQL
- URL del repositorio GitHub

**¡Eso es todo!** El script instalará y configurará automáticamente:
- ✅ Python 3.11 + Node.js 18
- ✅ PostgreSQL + Redis
- ✅ Nginx + SSL (Let's Encrypt)
- ✅ Servicios systemd
- ✅ Firewall + Monitoreo
- ✅ Backups automáticos

---

## 🛠️ Opción 2: Instalación Manual

Si prefieres control total, sigue la [Guía Completa de Despliegue](DEPLOYMENT_GUIDE.md).

---

## 🔍 Verificación Post-Instalación

### 1. Verificar Servicios

```bash
# Verificar que todos los servicios estén corriendo
sudo systemctl status jasmin-sms-api jasmin-sms-worker jasmin-sms-beat postgresql redis-server nginx
```

### 2. Verificar Conectividad

```bash
# Probar sitio web
curl -I https://tu-dominio.com

# Probar API
curl https://tu-dominio.com/api/health
```

### 3. Acceder a la Aplicación

- **Frontend**: https://tu-dominio.com
- **API Docs**: https://tu-dominio.com/api/docs
- **API Redoc**: https://tu-dominio.com/api/redoc

---

## ⚙️ Configuración Post-Instalación

### 1. Configurar Email (Opcional)

```bash
# Editar configuración
sudo nano /opt/jasmin-sms-dashboard/.env

# Configurar SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=noreply@tu-dominio.com

# Reiniciar servicios
sudo systemctl restart jasmin-sms-api
```

### 2. Instalar Jasmin SMS Gateway

```bash
# Opción 1: Instalación directa
pip3 install jasmin

# Opción 2: Docker (recomendado)
docker run -d --name jasmin-sms \
  -p 2775:2775 -p 8990:8990 -p 1401:1401 \
  jookies/jasmin

# Verificar instalación
telnet localhost 8990
# Usuario: jcliadmin
# Password: jclipwd
```

### 3. Crear Usuario Administrador

```bash
# Conectar al servidor
cd /opt/jasmin-sms-dashboard
source venv/bin/activate

# Crear superusuario (script interactivo)
python -c "
from app.models.user import User, UserRole
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email='admin@tu-dominio.com',
            username='admin',
            full_name='Administrador',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        db.add(admin)
        await db.commit()
        print('Usuario administrador creado: admin@tu-dominio.com / admin123')

asyncio.run(create_admin())
"
```

---

## 🔧 Comandos Útiles de Administración

### Gestión de Servicios

```bash
# Ver logs en tiempo real
sudo journalctl -u jasmin-sms-api -f
sudo journalctl -u jasmin-sms-worker -f
sudo journalctl -u jasmin-sms-beat -f

# Reiniciar servicios
sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat

# Ver estado de servicios
sudo systemctl status jasmin-sms-api jasmin-sms-worker jasmin-sms-beat
```

### Actualización de Código

```bash
# Actualizar desde GitHub
cd /opt/jasmin-sms-dashboard
git pull origin main

# Reinstalar dependencias si es necesario
source venv/bin/activate
pip install -r requirements.txt

# Reconstruir frontend
cd frontend
npm install
npm run build

# Reiniciar servicios
sudo systemctl restart jasmin-sms-api jasmin-sms-worker jasmin-sms-beat
```

### Backup y Restauración

```bash
# Backup manual
sudo /usr/local/bin/jasmin-sms-backup.sh

# Ver backups
ls -la /opt/backups/jasmin-sms-dashboard/

# Restaurar base de datos
gunzip -c /opt/backups/jasmin-sms-dashboard/db_backup_FECHA.sql.gz | psql -h localhost -U jasmin_user jasmin_sms_dashboard
```

### Monitoreo

```bash
# Ver uso de recursos
htop

# Ver espacio en disco
df -h

# Ver logs de monitoreo
tail -f /var/log/jasmin-sms-dashboard/monitor.log

# Ver logs de backup
tail -f /var/log/jasmin-sms-dashboard/backup.log
```

---

## 🚨 Solución de Problemas Comunes

### Problema: Servicios no inician

```bash
# Ver logs detallados
sudo journalctl -u jasmin-sms-api -n 50

# Verificar configuración
sudo nginx -t

# Verificar permisos
sudo chown -R www-data:www-data /opt/jasmin-sms-dashboard
```

### Problema: SSL no funciona

```bash
# Renovar certificados
sudo certbot renew

# Verificar configuración Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Problema: Base de datos no conecta

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Probar conexión
psql -h localhost -U jasmin_user -d jasmin_sms_dashboard
```

### Problema: Frontend no carga

```bash
# Verificar archivos del frontend
ls -la /opt/jasmin-sms-dashboard/frontend/build/

# Reconstruir frontend
cd /opt/jasmin-sms-dashboard/frontend
npm run build
```

---

## 📊 Métricas de Performance

### Capacidad del Sistema

- **Mensajes por minuto**: 1,000-10,000 (dependiendo del hardware)
- **Usuarios concurrentes**: 100-1,000
- **Campañas simultáneas**: 10-100
- **Contactos**: Millones (limitado por base de datos)

### Optimización

```bash
# Aumentar workers de Uvicorn
sudo nano /etc/systemd/system/jasmin-sms-api.service
# Cambiar: --workers 4 por --workers 8

# Aumentar concurrencia de Celery
sudo nano /etc/systemd/system/jasmin-sms-worker.service
# Cambiar: --concurrency=4 por --concurrency=8

# Reiniciar servicios
sudo systemctl daemon-reload
sudo systemctl restart jasmin-sms-api jasmin-sms-worker
```

---

## 🔒 Seguridad en Producción

### Checklist de Seguridad

- ✅ **Firewall configurado** (solo puertos 80, 443, 22)
- ✅ **SSL/TLS habilitado** con Let's Encrypt
- ✅ **Contraseñas seguras** para base de datos
- ✅ **Fail2ban configurado** contra ataques de fuerza bruta
- ✅ **Headers de seguridad** en Nginx
- ✅ **Backups automáticos** configurados

### Configuración Adicional

```bash
# Cambiar puerto SSH (opcional)
sudo nano /etc/ssh/sshd_config
# Port 2222

# Deshabilitar login root
# PermitRootLogin no

sudo systemctl restart ssh

# Actualizar firewall
sudo ufw allow 2222
sudo ufw delete allow ssh
```

---

## 📈 Escalabilidad

### Para Mayor Tráfico

1. **Múltiples Workers**: Aumentar workers de Uvicorn y Celery
2. **Load Balancer**: Usar Nginx como load balancer para múltiples instancias
3. **Base de Datos**: Migrar a PostgreSQL en servidor dedicado
4. **Redis Cluster**: Configurar Redis en cluster para alta disponibilidad
5. **CDN**: Usar CloudFlare para archivos estáticos

### Arquitectura Distribuida

```bash
# Ejemplo de configuración multi-servidor
# Servidor 1: Frontend + Load Balancer
# Servidor 2: API + Workers
# Servidor 3: Base de Datos
# Servidor 4: Redis + Jasmin SMS Gateway
```

---

## 🎯 Próximos Pasos

1. **Configurar Conectores SMPP** en Jasmin SMS Gateway
2. **Crear Plantillas de Mensajes** para campañas
3. **Importar Contactos** desde CSV/Excel
4. **Configurar Webhooks** para integraciones
5. **Personalizar Branding** con tu logo y colores
6. **Configurar Alertas** por email/Slack
7. **Entrenar Usuarios** en el uso de la plataforma

---

## 🆘 Soporte

### Recursos de Ayuda

- **Documentación Completa**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **README del Proyecto**: [README.md](README.md)
- **Issues de GitHub**: https://github.com/TU-USUARIO/jasmin-sms-dashboard/issues

### Contacto

- **Email**: soporte@tu-dominio.com
- **Documentación**: Disponible en el repositorio
- **Logs del Sistema**: `/var/log/jasmin-sms-dashboard/`

---

## 🏆 ¡Felicitaciones!

Has desplegado exitosamente **Jasmin SMS Dashboard Enterprise Edition**, una plataforma SMS empresarial completa con:

- ✅ **Dashboard en Tiempo Real** con WebSockets
- ✅ **Gestión Visual de Conectores** SMPP
- ✅ **Constructor Drag-and-Drop** para enrutamiento
- ✅ **Sistema de Facturación** empresarial
- ✅ **API RESTful Completa** con documentación
- ✅ **Frontend React Moderno** y responsive
- ✅ **Integración Directa** con Jasmin SMS Gateway
- ✅ **Arquitectura Escalable** para millones de mensajes

**¡Disfruta tu nueva plataforma SMS empresarial!** 🚀📱