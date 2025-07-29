#!/bin/bash

# 🚀 Script de Inicio Rápido - Jasmin SMS Dashboard Backend
# Versión: 2.0.0
# Descripción: Inicia el backend FastAPI con todas las dependencias

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🚀 JASMIN SMS DASHBOARD BACKEND STARTER            ║"
echo "║                     Enterprise Edition v2.0.0               ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    print_error "No se encontró main.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

print_status "Iniciando Jasmin SMS Dashboard Backend..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado. Por favor instala Python 3.11 o superior."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python version: $PYTHON_VERSION"

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    print_warning "Entorno virtual no encontrado. Creando..."
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate

# Verificar e instalar dependencias
if [ ! -f "venv/pyvenv.cfg" ] || [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    print_status "Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencias instaladas"
else
    print_status "Dependencias ya instaladas"
fi

# Verificar PostgreSQL
print_status "Verificando PostgreSQL..."
if ! systemctl is-active --quiet postgresql; then
    print_warning "PostgreSQL no está corriendo. Intentando iniciar..."
    sudo systemctl start postgresql
    if systemctl is-active --quiet postgresql; then
        print_success "PostgreSQL iniciado"
    else
        print_error "No se pudo iniciar PostgreSQL. Verifica la instalación."
        exit 1
    fi
else
    print_success "PostgreSQL está corriendo"
fi

# Verificar Redis
print_status "Verificando Redis..."
if ! systemctl is-active --quiet redis-server; then
    print_warning "Redis no está corriendo. Intentando iniciar..."
    sudo systemctl start redis-server
    if systemctl is-active --quiet redis-server; then
        print_success "Redis iniciado"
    else
        print_error "No se pudo iniciar Redis. Verifica la instalación."
        exit 1
    fi
else
    print_success "Redis está corriendo"
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado. Creando desde .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones antes de continuar"
        print_warning "   Especialmente la configuración de base de datos y claves secretas"
        echo ""
        read -p "¿Quieres editar el archivo .env ahora? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano .env
        fi
    else
        print_error "No se encontró .env.example. Crea manualmente el archivo .env"
        exit 1
    fi
fi

# Verificar conexión a base de datos
print_status "Verificando conexión a base de datos..."
if python3 -c "
import asyncio
from app.core.database import engine
from sqlalchemy import text

async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        print('✅ Conexión a base de datos exitosa')
        return True
    except Exception as e:
        print(f'❌ Error de conexión: {e}')
        return False

result = asyncio.run(test_connection())
exit(0 if result else 1)
" 2>/dev/null; then
    print_success "Conexión a base de datos exitosa"
else
    print_error "No se pudo conectar a la base de datos"
    print_warning "Verifica la configuración DATABASE_URL en el archivo .env"
    print_warning "Ejemplo: postgresql://jasmin_user:password@localhost/jasmin_sms_dashboard"
    exit 1
fi

# Ejecutar migraciones
print_status "Ejecutando migraciones de base de datos..."
if alembic upgrade head; then
    print_success "Migraciones ejecutadas correctamente"
else
    print_warning "Error en migraciones o ya están actualizadas"
fi

# Crear usuario administrador si no existe
print_status "Verificando usuario administrador..."
python3 -c "
import asyncio
from app.models.user import User, UserRole
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin_if_not_exists():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).where(User.email == 'admin@jasmin.com'))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print('✅ Usuario administrador ya existe')
                return
                
            admin = User(
                email='admin@jasmin.com',
                username='admin',
                full_name='Administrador del Sistema',
                hashed_password=get_password_hash('admin123'),
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            db.add(admin)
            await db.commit()
            print('✅ Usuario administrador creado: admin@jasmin.com / admin123')
        except Exception as e:
            print(f'❌ Error creando usuario administrador: {e}')

asyncio.run(create_admin_if_not_exists())
"

# Mostrar información de inicio
echo ""
print_success "🎉 ¡Todo listo para iniciar el backend!"
echo ""
print_status "Configuración:"
echo "  • Backend API: http://localhost:8000"
echo "  • Documentación API: http://localhost:8000/docs"
echo "  • Documentación Redoc: http://localhost:8000/redoc"
echo "  • WebSocket: ws://localhost:8000/ws"
echo ""
print_status "Credenciales de administrador:"
echo "  • Email: admin@jasmin.com"
echo "  • Password: admin123"
echo ""

# Preguntar modo de inicio
echo "Selecciona el modo de inicio:"
echo "1) Desarrollo (con recarga automática)"
echo "2) Producción (optimizado)"
echo "3) Solo verificar configuración (no iniciar)"
echo ""
read -p "Opción (1-3): " -n 1 -r
echo ""

case $REPLY in
    1)
        print_status "Iniciando en modo desarrollo..."
        echo ""
        print_warning "Presiona Ctrl+C para detener el servidor"
        echo ""
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    2)
        print_status "Iniciando en modo producción..."
        echo ""
        print_warning "Presiona Ctrl+C para detener el servidor"
        echo ""
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
        ;;
    3)
        print_success "Configuración verificada correctamente"
        print_status "Para iniciar manualmente:"
        echo "  • Desarrollo: uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
        echo "  • Producción: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"
        ;;
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

print_success "Script completado"