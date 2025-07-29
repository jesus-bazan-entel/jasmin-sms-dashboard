#!/bin/bash
# Script para limpiar cache y compilar el frontend

echo "🧹 Limpiando cache de React..."
rm -rf node_modules/.cache
rm -rf build

echo "📦 Instalando dependencias..."
npm install

echo "🔨 Compilando frontend..."
npm run build

echo "✅ Compilación completada!"