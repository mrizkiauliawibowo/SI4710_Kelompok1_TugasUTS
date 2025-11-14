#!/usr/bin/env python3
"""
Food Delivery System - All Services Startup Script
Jalankan semua services (API Gateway + 5 microservices) secara otomatis
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def run_command(command, cwd=None, shell=False):
    """Jalankan command di subprocess"""
    try:
        if isinstance(command, str):
            command = [sys.executable, command]
        print(f"🚀 Running: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell,
            stdout=None,
            stderr=None
        )
        return process
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return None

def start_api_gateway():
    """Start API Gateway di port 5000"""
    print("🔐 Starting API Gateway...")
    api_gateway_path = Path("microservices/api-gateway")
    
    # Install dependencies jika belum
    print("📦 Installing API Gateway dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                   cwd=api_gateway_path)
    
    # Start API Gateway
    print("🌐 Starting API Gateway on port 5000...")
    process = run_command(f"{sys.executable} app.py", cwd=api_gateway_path)

    if process:
        print("✅ API Gateway started successfully!")
        time.sleep(3)  # Wait for startup
        return process
    return None

def start_frontend_server():
    """Start frontend HTTP server"""
    print("🖥️ Starting Frontend Server...")
    frontend_path = Path("frontend")

    # Start HTTP server di port 3000
    print("🌐 Serving frontend on port 3000...")
    process = run_command(f"{sys.executable} -m http.server 3000", cwd=frontend_path)

    if process:
        print("✅ Frontend server started successfully!")
        time.sleep(3)  # Wait for startup
        return process
    return None

def start_microservices():
    """Start semua microservices"""
    services = {
        "User Service": {
            "path": "microservices/user-service",
            "port": 5001,
            "description": "👤 User Management (ARTHUR)"
        },
        "Restaurant Service": {
            "path": "microservices/restaurant-service", 
            "port": 5002,
            "description": "🍽️ Restaurant Management (rizki)"
        },
        "Order Service": {
            "path": "microservices/order-service",
            "port": 5003,
            "description": "📦 Order Management (Nadia)"
        },
        "Delivery Service": {
            "path": "microservices/delivery-service",
            "port": 5004,
            "description": "🚚 Delivery Management (aydin)"
        },
        "Payment Service": {
            "path": "microservices/payment-service",
            "port": 5005,
            "description": "💳 Payment Management (reza)"
        }
    }
    
    processes = {}
    
    for service_name, config in services.items():
        print(f"🚀 Starting {config['description']}...")
        service_path = Path(config["path"])
        
        # Install dependencies
        print(f"📦 Installing dependencies for {service_name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                       cwd=service_path)
        
        # Start service
        print(f"🌐 Starting {service_name} on port {config['port']}...")
        process = run_command(f"{sys.executable} app.py", cwd=service_path)

        if process:
            print(f"✅ {service_name} started successfully!")
            time.sleep(3)  # Wait for startup
            processes[service_name] = process
        else:
            print(f"❌ Failed to start {service_name}")
    
    return processes

def check_services():
    """Check status semua services"""
    import requests
    
    services = {
        "API Gateway": "http://localhost:5000/health",
        "User Service": "http://localhost:5001/health", 
        "Restaurant Service": "http://localhost:5002/health",
        "Order Service": "http://localhost:5003/health",
        "Delivery Service": "http://localhost:5004/health",
        "Payment Service": "http://localhost:5005/health"
    }
    
    print("\n🔍 Checking services status...")
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                print(f"✅ {service_name}: {status}")
            else:
                print(f"⚠️ {service_name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"❌ {service_name}: Connection failed")

def open_browser():
    """Open browser otomatis"""
    print("🌐 Opening browser...")
    time.sleep(3)  # Wait untuk server ready
    webbrowser.open("http://localhost:3000/")

def main():
    """Main function"""
    print("🍕 FOOD DELIVERY SYSTEM - AUTOMATED STARTUP")
    print("=" * 50)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("⚠️ Warning: .env file not found!")
        print("Creating default .env file...")
        
        env_content = """
# Food Delivery System Environment
JWT_SECRET_KEY=food-delivery-jwt-secret-key-for-uts-iae-2024
SECRET_KEY=gateway-secret-key-for-food-delivery-system
API_GATEWAY_PORT=5000

# Service URLs
USER_SERVICE_URL=http://localhost:5001
RESTAURANT_SERVICE_URL=http://localhost:5002
ORDER_SERVICE_URL=http://localhost:5003
DELIVERY_SERVICE_URL=http://localhost:5004
PAYMENT_SERVICE_URL=http://localhost:5005

# Demo Users
DEMO_ADMIN_USERNAME=admin
DEMO_ADMIN_PASSWORD=admin123
DEMO_USER_USERNAME=user
DEMO_USER_PASSWORD=user123
"""
        
        with open(".env", "w") as f:
            f.write(env_content.strip())
        print("✅ .env file created!")
    
    print("\n🎯 Starting all services...")
    
    # Start services
    api_gateway_process = start_api_gateway()
    frontend_process = start_frontend_server()
    microservices_processes = start_microservices()
    
    # Wait a moment
    time.sleep(5)
    
    # Check services
    check_services()
    
    # Open browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("\n" + "=" * 50)
    print("🎉 Food Delivery System is running!")
    print("\n📋 Access Points:")
    print("   🌐 Frontend:      http://localhost:3000/")
    print("   📚 API Docs:      http://localhost:5000/api-docs/")
    print("   🔧 Health Check:  http://localhost:5000/health")
    print("\n🔐 Demo Credentials:")
    print("   Admin: username=admin, password=admin123")
    print("   User:  username=user, password=user123")
    print("\n⏹️ Press Ctrl+C to stop all services")
    print("=" * 50)
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        
        # Kill all processes
        if api_gateway_process:
            api_gateway_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        for name, process in microservices_processes.items():
            print(f"Stopping {name}...")
            process.terminate()
        
        print("✅ All services stopped!")

if __name__ == "__main__":
    main()