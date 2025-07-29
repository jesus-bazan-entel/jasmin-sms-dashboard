#!/usr/bin/env python3
"""
Script de corrección rápida para la base de datos
Corrige el problema de foreign keys y crea el usuario administrador
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.core.database import get_db, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid

async def fix_database():
    """Corregir la base de datos y crear usuario administrador"""
    
    print("🔧 Iniciando corrección de base de datos...")
    
    try:
        # Crear todas las tablas
        from app.models import user, connector, campaign, contact, billing, message
        from app.core.database import Base
        
        async with engine.begin() as conn:
            print("📋 Creando tablas...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas correctamente")
        
        # Crear usuario administrador
        async with SessionLocal() as session:
            print("👤 Verificando usuario administrador...")
            
            # Verificar si ya existe
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": "admin@jasmin.com"}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print("✅ Usuario administrador ya existe")
                return True
            
            # Crear nuevo usuario administrador
            admin_user = User(
                id=uuid.uuid4(),
                email="admin@jasmin.com",
                username="admin",
                full_name="Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                is_verified=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            print("✅ Usuario administrador creado exitosamente")
            print(f"   📧 Email: admin@jasmin.com")
            print(f"   🔑 Password: admin123")
            print(f"   👑 Role: {UserRole.SUPER_ADMIN}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error en corrección de base de datos: {e}")
        return False

async def create_demo_users():
    """Crear usuarios de demostración"""
    
    demo_users = [
        {
            "email": "admin@jasmin.com",
            "username": "admin2",
            "full_name": "Admin User",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "email": "manager@jasmin.com",
            "username": "manager",
            "full_name": "Campaign Manager",
            "password": "manager123",
            "role": UserRole.CAMPAIGN_MANAGER
        },
        {
            "email": "analyst@jasmin.com",
            "username": "analyst",
            "full_name": "Analyst User",
            "password": "analyst123",
            "role": UserRole.ANALYST
        },
        {
            "email": "client@jasmin.com",
            "username": "client",
            "full_name": "Client User",
            "password": "client123",
            "role": UserRole.CLIENT
        }
    ]
    
    try:
        async with SessionLocal() as session:
            print("👥 Creando usuarios de demostración...")
            
            for user_data in demo_users:
                # Verificar si ya existe
                result = await session.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": user_data["email"]}
                )
                existing_user = result.fetchone()
                
                if existing_user:
                    print(f"   ⏭️  Usuario {user_data['email']} ya existe")
                    continue
                
                # Crear usuario
                user = User(
                    id=uuid.uuid4(),
                    email=user_data["email"],
                    username=user_data["username"],
                    full_name=user_data["full_name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                    is_verified=True
                )
                
                session.add(user)
                print(f"   ✅ Usuario {user_data['email']} creado")
            
            await session.commit()
            print("✅ Usuarios de demostración creados exitosamente")
            
    except Exception as e:
        print(f"❌ Error creando usuarios de demostración: {e}")

async def main():
    """Función principal"""
    print("🚀 Jasmin SMS Dashboard - Corrección de Base de Datos")
    print("=" * 60)
    
    # Corregir base de datos
    success = await fix_database()
    if not success:
        print("❌ Falló la corrección de base de datos")
        return False
    
    # Crear usuarios de demostración
    await create_demo_users()
    
    print("=" * 60)
    print("🎉 ¡Corrección completada exitosamente!")
    print("")
    print("📋 Credenciales disponibles:")
    print("   👑 Admin: admin@jasmin.com / admin123")
    print("   👔 Manager: manager@jasmin.com / manager123") 
    print("   🔧 Operator: operator@jasmin.com / operator123")
    print("   👤 User: user@jasmin.com / user123")
    print("")
    print("🚀 Ahora puedes iniciar el backend con: ./start_backend.sh")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())