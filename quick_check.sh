#!/bin/bash
# Script de verificación rápida

echo "🔍 DIAGNÓSTICO RÁPIDO - Error 500"
echo "================================="

# Verificar directorio build
echo "1. 📦 Frontend build:"
if [ -d "/opt/jasmin-sms-dashboard/frontend/build" ]; then
    echo "   ✅ Directorio build existe"
    echo "   📁 Archivos: $(ls -la /opt/jasmin-sms-dashboard/frontend/build | wc -l) elementos"
    if [ -f "/opt/jasmin-sms-dashboard/frontend/build/index.html" ]; then
        echo "   ✅ index.html existe"
    else
        echo "   ❌ index.html NO existe"
    fi
else
    echo "   ❌ Directorio build NO existe"
fi

# Verificar nginx
echo ""
echo "2. 🌐 Nginx:"
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx activo"
else
    echo "   ❌ Nginx inactivo"
fi

echo "   📋 Configuración:"
if [ -f "/etc/nginx/sites-enabled/jasmin-sms-dashboard" ]; then
    echo "   ✅ Configuración habilitada"
else
    echo "   ❌ Configuración NO habilitada"
fi

# Verificar backend
echo ""
echo "3. 🔧 Backend:"
if pgrep -f "uvicorn" > /dev/null; then
    echo "   ✅ Backend corriendo (PID: $(pgrep -f uvicorn))"
else
    echo "   ❌ Backend NO corriendo"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend responde en puerto 8000"
else
    echo "   ❌ Backend NO responde en puerto 8000"
fi

# Verificar puertos
echo ""
echo "4. 🔌 Puertos:"
if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "   ✅ Puerto 80 (nginx) abierto"
else
    echo "   ❌ Puerto 80 NO abierto"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo "   ✅ Puerto 8000 (backend) abierto"
else
    echo "   ❌ Puerto 8000 NO abierto"
fi

# Verificar logs recientes
echo ""
echo "5. 📋 Logs recientes:"
echo "   Nginx error (últimas 3 líneas):"
if [ -f "/var/log/nginx/error.log" ]; then
    sudo tail -n 3 /var/log/nginx/error.log | sed 's/^/      /'
else
    echo "      No hay logs de nginx"
fi

echo ""
echo "   Backend (últimas 3 líneas):"
if [ -f "/opt/jasmin-sms-dashboard/backend.log" ]; then
    tail -n 3 /opt/jasmin-sms-dashboard/backend.log | sed 's/^/      /'
else
    echo "      No hay logs de backend"
fi

echo ""
echo "🎯 RECOMENDACIONES:"
echo "=================="

if [ ! -d "/opt/jasmin-sms-dashboard/frontend/build" ]; then
    echo "❗ Compilar frontend: cd frontend && npm run build"
fi

if ! pgrep -f "uvicorn" > /dev/null; then
    echo "❗ Iniciar backend: cd /opt/jasmin-sms-dashboard && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
fi

if ! systemctl is-active --quiet nginx; then
    echo "❗ Iniciar nginx: sudo systemctl start nginx"
fi

echo ""
echo "🚀 Para corrección automática ejecuta:"
echo "   chmod +x fix_500_error.sh"
echo "   sudo ./fix_500_error.sh"