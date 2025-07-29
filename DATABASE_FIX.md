# 🔧 Corrección Rápida de Base de Datos

## ❌ Problema Detectado

Error en la relación SQLAlchemy entre `SMPPConnector` y `Route`:
```
Could not determine join condition between parent/child tables on relationship SMPPConnector.routes - there are multiple foreign key paths linking the tables.
```

## ✅ Solución Implementada

He corregido el problema en el modelo de datos y creado un script de corrección automática.

---

## 🚀 Corrección Inmediata (Opción 1 - Recomendada)

### **Ejecutar Script de Corrección:**
```bash
cd /opt/jasmin-sms-dashboard
source venv/bin/activate

# Ejecutar corrección automática
python fix_database.py
```

**Este script:**
- ✅ Corrige las relaciones SQLAlchemy
- ✅ Crea todas las tablas necesarias
- ✅ Crea el usuario administrador
- ✅ Crea usuarios de demostración

---

## 🔧 Corrección Manual (Opción 2)

### **1. Activar Entorno Virtual:**
```bash
cd /opt/jasmin-sms-dashboard
source venv/bin/activate
```

### **2. Ejecutar Migraciones:**
```bash
# Crear migración para la corrección
alembic revision --autogenerate -m "fix_connector_routes_relationship"

# Aplicar migración
alembic upgrade head
```

### **3. Crear Usuario Administrador Manualmente:**
```bash
python -c "
import asyncio
from app.core.database import get_async_session
from app.core.security import get_password_hash
from app.models.user import User, UserRole
import uuid

async def create_admin():
    async with get_async_session() as session:
        admin = User(
            id=uuid.uuid4(),
            email='admin@jasmin.com',
            username='admin',
            full_name='Administrator',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True
        )
        session.add(admin)
        await session.commit()
        print('✅ Usuario administrador creado')

asyncio.run(create_admin())
"
```

---

## 🎯 Verificación Post-Corrección

### **1. Verificar Tablas:**
```bash
# Conectar a PostgreSQL
psql -h localhost -U jasmin_user -d jasmin_sms

# Listar tablas
\dt

# Verificar usuarios
SELECT email, role, is_active FROM users;

# Salir
\q
```

### **2. Probar Conexión:**
```bash
python -c "
import asyncio
from app.core.database import get_async_session
from sqlalchemy import text

async def test_db():
    async with get_async_session() as session:
        result = await session.execute(text('SELECT COUNT(*) FROM users'))
        count = result.scalar()
        print(f'✅ Usuarios en base de datos: {count}')

asyncio.run(test_db())
"
```

---

## 🚀 Reiniciar Backend

Una vez corregida la base de datos:

```bash
# Iniciar backend
./start_backend.sh
# Seleccionar opción 2 (Producción)
```

---

## 📋 Credenciales Post-Corrección

### **Usuarios Creados:**
- **👑 Super Admin**: admin@jasmin.com / admin123
- **👔 Manager**: manager@jasmin.com / manager123
- **🔧 Operator**: operator@jasmin.com / operator123
- **👤 User**: user@jasmin.com / user123

---

## 🔍 Detalles Técnicos del Problema

### **Problema Original:**
```python
# En SMPPConnector
routes: Mapped[List["Route"]] = relationship(
    "Route",
    back_populates="connector",
    cascade="all, delete-orphan"
)
```

### **Solución Aplicada:**
```python
# En SMPPConnector (corregido)
routes: Mapped[List["Route"]] = relationship(
    "Route",
    back_populates="connector",
    foreign_keys="Route.connector_id",  # ← Especifica cuál FK usar
    cascade="all, delete-orphan"
)
```

**Explicación:** El modelo `Route` tiene dos foreign keys hacia `SMPPConnector`:
- `connector_id` (conector principal)
- `failover_connector_id` (conector de respaldo)

SQLAlchemy no sabía cuál usar para la relación `routes`, por lo que especificamos explícitamente `Route.connector_id`.

---

## ⚡ Comando de Corrección Rápida

```bash
cd /opt/jasmin-sms-dashboard && source venv/bin/activate && python fix_database.py && ./start_backend.sh
```

**¡En 2 minutos tendrás todo funcionando!** 🚀

---

## 🆘 Si Persisten Problemas

### **Resetear Base de Datos Completamente:**
```bash
# Conectar a PostgreSQL como superusuario
sudo -u postgres psql

# Recrear base de datos
DROP DATABASE IF EXISTS jasmin_sms;
CREATE DATABASE jasmin_sms OWNER jasmin_user;
\q

# Ejecutar corrección
cd /opt/jasmin-sms-dashboard
source venv/bin/activate
python fix_database.py
```

### **Verificar Servicios:**
```bash
# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis

# Jasmin
sudo systemctl status jasmin
```

---

## 🎉 Resultado Esperado

Después de la corrección:

```
🚀 Jasmin SMS Dashboard - Corrección de Base de Datos
============================================================
🔧 Iniciando corrección de base de datos...
📋 Creando tablas...
✅ Tablas creadas correctamente
👤 Verificando usuario administrador...
✅ Usuario administrador creado exitosamente
   📧 Email: admin@jasmin.com
   🔑 Password: admin123
   👑 Role: UserRole.SUPER_ADMIN
👥 Creando usuarios de demostración...
   ✅ Usuario manager@jasmin.com creado
   ✅ Usuario operator@jasmin.com creado
   ✅ Usuario user@jasmin.com creado
✅ Usuarios de demostración creados exitosamente
============================================================
🎉 ¡Corrección completada exitosamente!
```

**¡Tu plataforma SMS estará lista para usar!** 📱✨