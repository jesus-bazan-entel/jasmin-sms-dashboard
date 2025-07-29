# 🎯 SOLUCIÓN INMEDIATA - Error 500

## ✅ Diagnóstico Completado

El problema está identificado:
- ❌ Frontend no compilado (directorio build no existe)
- ❌ Backend no corriendo (puerto 8000 cerrado)
- ✅ Nginx funcionando correctamente

## 🚀 Solución en 3 Pasos

### **PASO 1: Ejecutar Corrección Automática**
```bash
cd /opt/jasmin-sms-dashboard
chmod +x fix_500_error.sh
sudo ./fix_500_error.sh
```

### **PASO 2: Verificar Resultado**
```bash
./quick_check.sh
```

### **PASO 3: Probar URLs**
- http://190.105.244.174/
- http://190.105.244.174/login
- http://190.105.244.174/health

## 🔧 Si Prefieres Pasos Manuales

### **1. Compilar Frontend:**
```bash
cd frontend
npm run build
```

### **2. Iniciar Backend:**
```bash
cd /opt/jasmin-sms-dashboard
source venv/bin/activate
python fix_database_simple.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### **3. Verificar:**
```bash
curl http://localhost:8000/health
```

## 📋 Credenciales

- **Email**: admin@jasmin.com
- **Password**: admin123

## ⚡ Comando de Una Línea

```bash
cd /opt/jasmin-sms-dashboard && chmod +x fix_500_error.sh && sudo ./fix_500_error.sh
```

¡El sistema estará funcionando en menos de 5 minutos! 🚀