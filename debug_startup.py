#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas de startup
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

async def test_database_connection():
    """Probar conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        from app.core.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Probar conexión básica
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Conexión a PostgreSQL exitosa")
            
        # Probar sesión
        async with SessionLocal() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✅ Sesión de base de datos exitosa - {count} usuarios encontrados")
            
        return True
        
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
        traceback.print_exc()
        return False

async def test_models_import():
    """Probar importación de modelos"""
    print("🔍 Probando importación de modelos...")
    
    try:
        from app.models import user, connector, campaign, contact, billing, message
        print("✅ Modelos importados correctamente")
        
        # Probar clases específicas
        from app.models.user import User, UserRole
        from app.models.connector import SMPPConnector
        print("✅ Clases de modelos accesibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        traceback.print_exc()
        return False

async def test_app_startup():
    """Probar startup de la aplicación"""
    print("🔍 Probando startup de la aplicación...")
    
    try:
        from app.main import app
        print("✅ Aplicación FastAPI importada")
        
        # Probar eventos de startup
        from app.core.database import init_db
        await init_db()
        print("✅ Inicialización de base de datos exitosa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en startup de aplicación: {e}")
        traceback.print_exc()
        return False

async def test_services():
    """Probar servicios"""
    print("🔍 Probando servicios...")
    
    try:
        from app.services.metrics import MetricsService
        metrics = MetricsService()
        print("✅ MetricsService inicializado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en servicios: {e}")
        traceback.print_exc()
        return False

async def test_config():
    """Probar configuración"""
    print("🔍 Probando configuración...")
    
    try:
        from app.core.config import settings
        print(f"✅ Configuración cargada")
        print(f"   📊 DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        print(f"   🔑 SECRET_KEY: {'*' * 20}")
        print(f"   🌐 CORS_ORIGINS: {settings.CORS_ORIGINS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        traceback.print_exc()
        return False

async def main():
    """Función principal de diagnóstico"""
    print("🚀 Jasmin SMS Dashboard - Diagnóstico de Startup")
    print("=" * 60)
    
    tests = [
        ("Configuración", test_config),
        ("Modelos", test_models_import),
        ("Base de Datos", test_database_connection),
        ("Servicios", test_services),
        ("Aplicación", test_app_startup),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando prueba: {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ¡Todos los tests pasaron! El backend debería funcionar.")
        print("\n🚀 Intenta iniciar el backend con:")
        print("   ./start_backend.sh")
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores arriba.")
        print("\n🔧 Posibles soluciones:")
        print("   1. Ejecutar: python fix_database_simple.py")
        print("   2. Verificar variables de entorno")
        print("   3. Revisar logs de PostgreSQL")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())