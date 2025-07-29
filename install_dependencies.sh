#!/bin/bash
# Script para instalar todas las dependencias del frontend

echo "📦 Instalando dependencias del frontend..."
cd frontend

echo "🧹 Limpiando instalación anterior..."
rm -rf node_modules
rm -f package-lock.json

echo "📋 Instalando dependencias base..."
npm install

echo "🔧 Instalando dependencias específicas faltantes..."
npm install @reduxjs/toolkit react-redux

echo "🎨 Instalando dependencias de UI..."
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install @mui/lab

echo "🌐 Instalando dependencias de routing y HTTP..."
npm install react-router-dom axios

echo "📊 Instalando dependencias de gráficos..."
npm install recharts

echo "🔌 Instalando dependencias de WebSocket..."
npm install socket.io-client

echo "🛠️ Instalando dependencias de desarrollo..."
npm install --save-dev @types/react @types/react-dom

echo "✅ Todas las dependencias instaladas!"

echo "🔨 Intentando compilar..."
npm run build

if [ $? -eq 0 ]; then
    echo "🎉 ¡Frontend compilado exitosamente!"
    echo "📁 Archivos generados en: $(pwd)/build"
    ls -la build/
else
    echo "❌ Error en compilación. Revisando package.json..."
    echo "📋 Dependencias actuales:"
    npm list --depth=0
fi