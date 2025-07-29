#!/usr/bin/env python3
"""
Script de corrección simple para la base de datos
Corrige el problema de foreign keys y crea el usuario administrador
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

async def fix_database():
    """Corregir la base de datos y crear usuario administrador"""
    
    print("🔧 Iniciando corrección simple de base de datos...")
    
    try:
        # Importar después de agregar al path
        from app.core.database import engine, SessionLocal, Base
        from app.core.security import get_password_hash
        from app.models.user import User, UserRole
        from sqlalchemy import text
        import uuid
        
        # Crear todas las tablas
        print("📋 Creando tablas...")
        async with engine.begin() as conn:
            # Importar todos los modelos para registrarlos
            try:
                from app.models import user, connector, campaign, contact, billing, message, template
                print("✅ Modelos importados correctamente")
            except Exception as e:
                print(f"⚠️  Advertencia importando modelos: {e}")
                # Continuar de todas formas
            
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas correctamente")
        
        # Crear usuario administrador
        print("👤 Creando usuario administrador...")
        async with SessionLocal() as session:
            try:
                # Verificar si ya existe
                result = await session.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": "admin@jasmin.com"}
                )
                existing_user = result.fetchone()
                
                if existing_user:
                    print("✅ Usuario administrador ya existe")
                else:
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
                
                # Crear usuarios adicionales
                demo_users = [
                    ("manager@jasmin.com", "manager", "Manager User", "manager123", UserRole.MANAGER),
                    ("operator@jasmin.com", "operator", "Operator User", "operator123", UserRole.OPERATOR),
                    ("user@jasmin.com", "user", "Regular User", "user123", UserRole.USER)
                ]
                
                print("👥 Creando usuarios de demostración...")
                for email, username, full_name, password, role in demo_users:
                    # Verificar si ya existe
                    result = await session.execute(
                        text("SELECT id FROM users WHERE email = :email"),
                        {"email": email}
                    )
                    existing = result.fetchone()
                    
                    if existing:
                        print(f"   ⏭️  Usuario {email} ya existe")
                        continue
                    
                    # Crear usuario
                    user = User(
                        id=uuid.uuid4(),
                        email=email,
                        username=username,
                        full_name=full_name,
                        hashed_password=get_password_hash(password),
                        role=role,
                        is_active=True,
                        is_verified=True
                    )
                    
                    session.add(user)
                    print(f"   ✅ Usuario {email} creado")
                
                await session.commit()
                print("✅ Usuarios de demostración creados exitosamente")
                
            except Exception as e:
                await session.rollback()
                print(f"❌ Error creando usuarios: {e}")
                return False
            
        return True
            
    except Exception as e:
        print(f"❌ Error en corrección de base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal"""
    print("🚀 Jasmin SMS Dashboard - Corrección Simple de Base de Datos")
    print("=" * 65)
    
    # Corregir base de datos
    success = await fix_database()
    if not success:
        print("❌ Falló la corrección de base de datos")
        return False
    
    print("=" * 65)
    print("🎉 ¡Corrección completada exitosamente!")
    print("")
    print("📋 Credenciales disponibles:")
    print("   👑 Admin: admin@jasmin.com / admin123")
    print("   👔 Manager: manager@jasmin.com / manager123") 
    print("   🔧 Operator: operator@jasmin.com / operator123")
    print("   👤 User: user@jasmin.com / user123")
    print("")
    print("🚀 Ahora puedes iniciar el backend con:")
    print("   ./start_backend.sh")
    print("   (Seleccionar opción 2 para producción)")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())