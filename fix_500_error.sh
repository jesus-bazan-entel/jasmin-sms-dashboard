#!/bin/bash
# Script para diagnosticar y corregir error 500

echo "🔍 Diagnosticando error 500 en Jasmin SMS Dashboard..."
echo "=================================================="

# 1. Verificar si el frontend está compilado
echo "📦 Verificando frontend compilado..."
if [ ! -d "/opt/jasmin-sms-dashboard/frontend/build" ]; then
    echo "❌ Frontend no compilado. Instalando dependencias y compilando..."
    cd /opt/jasmin-sms-dashboard
    
    # Instalar dependencias primero
    echo "📋 Instalando dependencias..."
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando dependencias o compilando frontend"
        exit 1
    fi
    echo "✅ Frontend compilado exitosamente"
else
    echo "✅ Frontend ya compilado"
fi

# 2. Verificar permisos del directorio build
echo "🔐 Verificando permisos..."
sudo chown -R www-data:www-data /opt/jasmin-sms-dashboard/frontend/build
sudo chmod -R 755 /opt/jasmin-sms-dashboard/frontend/build
echo "✅ Permisos corregidos"

# 3. Verificar configuración de nginx
echo "⚙️  Verificando configuración de nginx..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Error en configuración de nginx"
    echo "Revisa los logs: sudo tail -f /var/log/nginx/error.log"
    exit 1
fi
echo "✅ Configuración de nginx válida"

# 4. Verificar si el backend está corriendo
echo "🔧 Verificando backend..."
if ! pgrep -f "uvicorn" > /dev/null; then
    echo "❌ Backend no está corriendo. Iniciando..."
    cd /opt/jasmin-sms-dashboard
    source venv/bin/activate
    
    # Corregir base de datos primero
    echo "🗄️  Corrigiendo base de datos..."
    python fix_database_simple.py
    
    # Corregir problemas de importación primero
    echo "🔧 Corrigiendo problemas de importación..."
    python fix_backend_import.py
    
    # Instalar dependencias de Python si es necesario
    echo "📦 Verificando dependencias de Python..."
    pip install fastapi uvicorn sqlalchemy asyncpg alembic python-jose passlib python-multipart python-dotenv redis celery
    
    # Iniciar backend en background
    echo "🚀 Iniciando backend..."
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    
    # Esperar un poco para que inicie
    sleep 10
    
    if pgrep -f "uvicorn" > /dev/null; then
        echo "✅ Backend iniciado exitosamente"
    else
        echo "❌ Error iniciando backend. Revisa backend.log"
        echo "📋 Últimas líneas del log:"
        tail -n 20 backend.log
        echo ""
        echo "🔧 Intentando iniciar manualmente para ver errores..."
        timeout 10 python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 || true
        exit 1
    fi
else
    echo "✅ Backend ya está corriendo"
fi

# 5. Verificar conectividad del backend
echo "🌐 Verificando conectividad del backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend responde correctamente"
else
    echo "❌ Backend no responde. Verificando logs..."
    tail -n 10 /opt/jasmin-sms-dashboard/backend.log
fi

# 6. Actualizar configuración de nginx con la ruta correcta
echo "📝 Actualizando configuración de nginx..."
cat > /tmp/nginx_fixed.conf << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name 190.105.244.174;

    root /opt/jasmin-sms-dashboard/frontend/build;
    index index.html;

    # Logs específicos
    access_log /var/log/nginx/jasmin-sms-dashboard.access.log;
    error_log /var/log/nginx/jasmin-sms-dashboard.error.log;

    # Configuración para SPA (Single Page Application)
    location / {
        try_files $uri $uri/ /index.html;
        
        # Headers para evitar cache en desarrollo
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # Archivos estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1d;
        add_header Cache-Control "public";
        try_files $uri =404;
    }

    # API proxy al backend FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check directo
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Documentación API
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo cp /tmp/nginx_fixed.conf /etc/nginx/sites-available/jasmin-sms-dashboard
echo "✅ Configuración actualizada"

# 7. Recargar nginx
echo "🔄 Recargando nginx..."
sudo systemctl reload nginx
echo "✅ Nginx recargado"

# 8. Verificar estado final
echo ""
echo "🎯 VERIFICACIÓN FINAL"
echo "===================="

echo "📊 Estado de servicios:"
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Activo"
else
    echo "❌ Nginx: Inactivo"
fi

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Backend: Corriendo"
else
    echo "❌ Backend: No corriendo"
fi

echo ""
echo "🌐 URLs para probar:"
echo "   Frontend: http://190.105.244.174/"
echo "   Login: http://190.105.244.174/login"
echo "   Health: http://190.105.244.174/health"
echo "   API Docs: http://190.105.244.174/docs"

echo ""
echo "🔑 Credenciales:"
echo "   admin@jasmin.com / admin123"

echo ""
echo "📋 Si persisten problemas, revisa los logs:"
echo "   sudo tail -f /var/log/nginx/jasmin-sms-dashboard.error.log"
echo "   tail -f /opt/jasmin-sms-dashboard/backend.log"

echo ""
echo "✅ Diagnóstico completado!"