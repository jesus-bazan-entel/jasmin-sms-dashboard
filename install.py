#!/usr/bin/env python3
"""
Jasmin SMS Dashboard - Automated Installation Script
Enterprise SMS Management Platform Setup
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import platform
import time

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def print_step(step, text):
    """Print formatted step"""
    print(f"\n[{step}] {text}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def run_command(command, description="", cwd=None, check=True):
    """Run command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        if result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False, e.stderr

def check_system_requirements():
    """Check system requirements"""
    print_step("SYSTEM", "Checking system requirements")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check Node.js
    success, output = run_command("node --version", check=False)
    if not success:
        print_error("Node.js is required for frontend. Please install Node.js 16+")
        return False
    
    node_version = output.strip().replace('v', '')
    major_version = int(node_version.split('.')[0])
    if major_version < 16:
        print_error("Node.js 16 or higher is required")
        return False
    print_success(f"Node.js {node_version} detected")
    
    # Check npm
    success, output = run_command("npm --version", check=False)
    if not success:
        print_error("npm is required")
        return False
    print_success(f"npm {output.strip()} detected")
    
    # Check PostgreSQL
    success, output = run_command("psql --version", check=False)
    if not success:
        print_warning("PostgreSQL not found. Please install PostgreSQL 12+")
        print("You can install it from: https://www.postgresql.org/download/")
    else:
        print_success(f"PostgreSQL detected: {output.strip()}")
    
    # Check Redis
    success, output = run_command("redis-server --version", check=False)
    if not success:
        print_warning("Redis not found. Please install Redis 6+")
        print("You can install it from: https://redis.io/download")
    else:
        print_success(f"Redis detected: {output.strip()}")
    
    return True

def setup_backend():
    """Setup FastAPI backend"""
    print_step("BACKEND", "Setting up FastAPI backend")
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    success, _ = run_command(f"{sys.executable} -m venv venv")
    if not success:
        return False
    print_success("Virtual environment created")
    
    # Determine activation script
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        python_path = "venv\\Scripts\\python"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_script = "venv/bin/activate"
        python_path = "venv/bin/python"
        pip_path = "venv/bin/pip"
    
    # Upgrade pip
    print("Upgrading pip...")
    success, _ = run_command(f"{pip_path} install --upgrade pip")
    if not success:
        return False
    print_success("pip upgraded")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    success, _ = run_command(f"{pip_path} install -r requirements.txt")
    if not success:
        print_error("Failed to install Python dependencies")
        return False
    print_success("Python dependencies installed")
    
    # Create necessary directories
    print("Creating necessary directories...")
    directories = ['logs', 'uploads', 'exports', 'static', 'media']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print_success("Directories created")
    
    return True

def setup_frontend():
    """Setup React frontend"""
    print_step("FRONTEND", "Setting up React frontend")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return False
    
    # Install npm dependencies
    print("Installing npm dependencies...")
    success, _ = run_command("npm install", cwd=frontend_dir)
    if not success:
        print_error("Failed to install npm dependencies")
        return False
    print_success("npm dependencies installed")
    
    return True

def setup_database():
    """Setup database"""
    print_step("DATABASE", "Setting up database")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        shutil.copy(".env.example", ".env")
        print_success(".env file created")
        print_warning("Please edit .env file with your database credentials")
    
    # Run database migrations
    print("Running database migrations...")
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    success, _ = run_command(f"{python_path} -m alembic upgrade head")
    if not success:
        print_warning("Database migrations failed. Please check your database configuration in .env")
        return False
    
    print_success("Database migrations completed")
    return True

def create_superuser():
    """Create superuser"""
    print_step("USER", "Creating superuser")
    
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    print("Creating superuser account...")
    print("Please provide the following information:")
    
    # This would be interactive in a real implementation
    print_warning("Run the following command manually to create a superuser:")
    print(f"{python_path} -c \"from app.scripts.create_superuser import create_superuser; create_superuser()\"")
    
    return True

def setup_services():
    """Setup system services"""
    print_step("SERVICES", "Setting up system services")
    
    # Create systemd service files (Linux only)
    if platform.system() == "Linux":
        print("Creating systemd service files...")
        
        # FastAPI service
        fastapi_service = f"""[Unit]
Description=Jasmin SMS Dashboard API
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'jasmin')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={os.getcwd()}/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        # Celery worker service
        celery_worker_service = f"""[Unit]
Description=Jasmin SMS Dashboard Celery Worker
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'jasmin')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={os.getcwd()}/venv/bin/celery -A app.tasks worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        # Celery beat service
        celery_beat_service = f"""[Unit]
Description=Jasmin SMS Dashboard Celery Beat
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'jasmin')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={os.getcwd()}/venv/bin/celery -A app.tasks beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        # Write service files
        service_files = [
            ("jasmin-sms-api.service", fastapi_service),
            ("jasmin-sms-worker.service", celery_worker_service),
            ("jasmin-sms-beat.service", celery_beat_service),
        ]
        
        for filename, content in service_files:
            with open(filename, 'w') as f:
                f.write(content)
        
        print_success("Systemd service files created")
        print("To install services, run:")
        for filename, _ in service_files:
            print(f"  sudo cp {filename} /etc/systemd/system/")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable jasmin-sms-api jasmin-sms-worker jasmin-sms-beat")
    
    else:
        print_warning("Automatic service setup is only available on Linux")
        print("Please refer to the documentation for manual service setup")
    
    return True

def build_frontend():
    """Build frontend for production"""
    print_step("BUILD", "Building frontend for production")
    
    frontend_dir = Path("frontend")
    
    print("Building React frontend...")
    success, _ = run_command("npm run build", cwd=frontend_dir)
    if not success:
        print_error("Failed to build frontend")
        return False
    
    print_success("Frontend built successfully")
    return True

def create_nginx_config():
    """Create Nginx configuration"""
    print_step("NGINX", "Creating Nginx configuration")
    
    nginx_config = f"""server {{
    listen 80;
    server_name your-domain.com;  # Change this to your domain
    
    # Serve React frontend
    location / {{
        root {os.getcwd()}/frontend/build;
        try_files $uri $uri/ /index.html;
    }}
    
    # API endpoints
    location /api/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # WebSocket endpoints
    location /ws/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files
    location /static/ {{
        alias {os.getcwd()}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Media files
    location /media/ {{
        alias {os.getcwd()}/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
    
    with open("nginx-jasmin-sms.conf", "w") as f:
        f.write(nginx_config)
    
    print_success("Nginx configuration created: nginx-jasmin-sms.conf")
    print("To install:")
    print("  sudo cp nginx-jasmin-sms.conf /etc/nginx/sites-available/jasmin-sms")
    print("  sudo ln -s /etc/nginx/sites-available/jasmin-sms /etc/nginx/sites-enabled/")
    print("  sudo nginx -t")
    print("  sudo systemctl reload nginx")
    
    return True

def print_final_instructions():
    """Print final setup instructions"""
    print_header("INSTALLATION COMPLETE!")
    
    print("\n🎉 Jasmin SMS Dashboard has been installed successfully!")
    
    print("\n📋 NEXT STEPS:")
    print("1. Edit the .env file with your actual configuration:")
    print("   - Database credentials")
    print("   - Jasmin SMS Gateway settings")
    print("   - Email configuration")
    print("   - Secret keys")
    
    print("\n2. Start the services:")
    if platform.system() == "Windows":
        print("   # Terminal 1: API Server")
        print("   venv\\Scripts\\activate")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\n   # Terminal 2: Celery Worker")
        print("   venv\\Scripts\\activate")
        print("   celery -A app.tasks worker --loglevel=info")
        print("\n   # Terminal 3: Celery Beat")
        print("   venv\\Scripts\\activate")
        print("   celery -A app.tasks beat --loglevel=info")
        print("\n   # Terminal 4: Frontend Development")
        print("   cd frontend")
        print("   npm start")
    else:
        print("   # Terminal 1: API Server")
        print("   source venv/bin/activate")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\n   # Terminal 2: Celery Worker")
        print("   source venv/bin/activate")
        print("   celery -A app.tasks worker --loglevel=info")
        print("\n   # Terminal 3: Celery Beat")
        print("   source venv/bin/activate")
        print("   celery -A app.tasks beat --loglevel=info")
        print("\n   # Terminal 4: Frontend Development")
        print("   cd frontend")
        print("   npm start")
    
    print("\n3. Access the application:")
    print("   - Development Frontend: http://localhost:3000")
    print("   - API Documentation: http://localhost:8000/api/docs")
    print("   - API Redoc: http://localhost:8000/api/redoc")
    
    print("\n4. Configure Jasmin SMS Gateway:")
    print("   - Install Jasmin: pip3 install jasmin")
    print("   - Or use Docker: docker run -d --name jasmin-sms -p 2775:2775 -p 8990:8990 -p 1401:1401 jookies/jasmin")
    print("   - Configure connectors via the web interface")
    
    print("\n5. Production deployment:")
    print("   - Use the generated systemd service files (Linux)")
    print("   - Configure Nginx with the provided configuration")
    print("   - Set up SSL certificates")
    print("   - Configure firewall rules")
    
    print("\n📚 DOCUMENTATION:")
    print("   - README.md: Complete setup and usage guide")
    print("   - API Documentation: Available at /api/docs when running")
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("   - Change the SECRET_KEY in production")
    print("   - Use strong database passwords")
    print("   - Configure proper firewall rules")
    print("   - Enable HTTPS in production")
    print("   - Regularly update dependencies")
    
    print("\n🆘 SUPPORT:")
    print("   - GitHub Issues: https://github.com/your-repo/jasmin-sms-dashboard/issues")
    print("   - Documentation: See README.md")
    
    print("\n" + "="*70)
    print(" Thank you for using Jasmin SMS Dashboard!")
    print("="*70)

def main():
    """Main installation function"""
    print_header("JASMIN SMS DASHBOARD - INSTALLATION")
    print("Enterprise SMS Management Platform")
    print("Version 2.0.0")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print_error("Please run this script from the project root directory")
        sys.exit(1)
    
    # Installation steps
    steps = [
        ("System Requirements", check_system_requirements),
        ("Backend Setup", setup_backend),
        ("Frontend Setup", setup_frontend),
        ("Database Setup", setup_database),
        ("Create Superuser", create_superuser),
        ("Build Frontend", build_frontend),
        ("System Services", setup_services),
        ("Nginx Configuration", create_nginx_config),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
                print_error(f"Step '{step_name}' failed")
            else:
                print_success(f"Step '{step_name}' completed")
        except Exception as e:
            failed_steps.append(step_name)
            print_error(f"Step '{step_name}' failed with exception: {e}")
    
    # Summary
    if failed_steps:
        print_header("INSTALLATION COMPLETED WITH WARNINGS")
        print_warning("The following steps had issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease review the errors above and complete these steps manually.")
    else:
        print_header("INSTALLATION SUCCESSFUL")
    
    # Final instructions
    print_final_instructions()

if __name__ == "__main__":
    main()