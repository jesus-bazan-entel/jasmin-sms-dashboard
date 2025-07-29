@echo off
REM Script para limpiar cache y compilar el frontend en Windows

echo 🧹 Limpiando cache de React...
if exist node_modules\.cache rmdir /s /q node_modules\.cache
if exist build rmdir /s /q build

echo 📦 Instalando dependencias...
npm install

echo 🔨 Compilando frontend...
npm run build

echo ✅ Compilación completada!
pause