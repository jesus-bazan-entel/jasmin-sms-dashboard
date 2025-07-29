#!/bin/bash
# Script para configurar Nginx para React SPA

echo "🔧 Configurando Nginx para Jasmin SMS Dashboard..."

# Verificar si nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx no está instalado. Instalando..."
    sudo apt update
    sudo apt install -y nginx
fi

# Crear directorio de configuración si no existe
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# Copiar configuración
echo "📋 Copiando configuración de Nginx..."
sudo cp nginx_spa.conf /etc/nginx/sites-available/jasmin-sms-dashboard

# Crear enlace simbólico
echo "🔗 Habilitando sitio..."
sudo ln -sf /etc/nginx/sites-available/jasmin-sms-dashboard /etc/nginx/sites-enabled/

# Deshabilitar sitio por defecto si existe
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "🚫 Deshabilitando sitio por defecto..."
    sudo rm /etc/nginx/sites-enabled/default
fi

# Verificar configuración
echo "✅ Verificando configuración de Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuración válida. Reiniciando Nginx..."
    sudo systemctl reload nginx
    sudo systemctl enable nginx
    
    echo "🎉 ¡Nginx configurado exitosamente!"
    echo ""
    echo "📋 URLs disponibles:"
    echo "   🌐 Frontend: http://190.105.244.174/"
    echo "   🔐 Login: http://190.105.244.174/login"
    echo "   📊 Dashboard: http://190.105.244.174/dashboard"
    echo "   🔧 API Docs: http://190.105.244.174/docs"
    echo "   ❤️  Health: http://190.105.244.174/health"
    echo ""
    echo "🔑 Credenciales:"
    echo "   👑 Admin: admin@jasmin.com / admin123"
    echo ""
    echo "⚠️  Asegúrate de que el backend esté corriendo en el puerto 8000"
    echo "   cd /opt/jasmin-sms-dashboard"
    echo "   source venv/bin/activate"
    echo "   ./start_backend.sh"
    
else
    echo "❌ Error en la configuración de Nginx. Revisa los logs:"
    echo "   sudo nginx -t"
    echo "   sudo tail -f /var/log/nginx/error.log"
fi