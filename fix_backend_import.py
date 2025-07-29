#!/usr/bin/env python3
"""
Script para corregir problemas de importación del backend
"""

import os
import sys
from pathlib import Path

def create_missing_files():
    """Crear archivos faltantes para que el backend funcione"""
    
    print("🔧 Corrigiendo problemas de importación del backend...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app"):
        print("❌ No se encuentra el directorio 'app'. Asegúrate de estar en /opt/jasmin-sms-dashboard")
        return False
    
    # Crear archivo de configuración básico si no existe
    config_file = Path("app/core/config.py")
    if not config_file.exists():
        print("📝 Creando archivo de configuración...")
        config_content = '''"""
Configuration settings for Jasmin SMS Dashboard
"""

import os
from typing import List

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://jasmin_user:jasmin_password@localhost:5432/jasmin_sms"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://190.105.244.174",
        "http://190.105.244.174:3000"
    ]
    
    # Allowed hosts
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Jasmin
    JASMIN_HOST: str = os.getenv("JASMIN_HOST", "localhost")
    JASMIN_PORT: int = int(os.getenv("JASMIN_PORT", "8990"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
'''
        config_file.write_text(config_content)
        print("✅ Archivo de configuración creado")
    
    # Crear archivo de seguridad básico si no existe
    security_file = Path("app/core/security.py")
    if not security_file.exists():
        print("📝 Creando archivo de seguridad...")
        security_content = '''"""
Security utilities for authentication and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
'''
        security_file.write_text(security_content)
        print("✅ Archivo de seguridad creado")
    
    # Verificar que el archivo main.py existe y es correcto
    main_file = Path("app/main.py")
    if main_file.exists():
        print("✅ Archivo main.py existe")
    else:
        print("❌ Archivo main.py no existe")
        return False
    
    # Crear requirements.txt si no existe
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("📝 Creando requirements.txt...")
        requirements_content = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
redis==5.0.1
celery==5.3.4
'''
        requirements_file.write_text(requirements_content)
        print("✅ Requirements.txt creado")
    
    print("✅ Corrección de importaciones completada")
    return True

def test_import():
    """Probar si el módulo se puede importar"""
    print("🧪 Probando importación del módulo...")
    
    try:
        # Agregar el directorio actual al path
        sys.path.insert(0, os.getcwd())
        
        # Intentar importar
        from app.main import app
        print("✅ Módulo app.main importado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando módulo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Jasmin SMS Dashboard - Corrección de Backend")
    print("=" * 50)
    
    # Crear archivos faltantes
    if not create_missing_files():
        print("❌ Error creando archivos")
        return False
    
    # Probar importación
    if test_import():
        print("\n🎉 ¡Backend corregido exitosamente!")
        print("\n🚀 Ahora puedes iniciar el backend con:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return True
    else:
        print("\n❌ Aún hay problemas con el backend")
        print("Revisa los logs para más detalles")
        return False

if __name__ == "__main__":
    main()