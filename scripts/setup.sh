#!/bin/bash
echo "🛠️  Setup Environment for Food Delivery System"
echo "=============================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip are available"

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir logs
    echo "✅ Created logs directory"
fi

# Setup API Gateway
echo "🚀 Setting up API Gateway..."
cd microservices/api-gateway
pip install -r requirements.txt
cd ../..

# Setup User Service
echo "👤 Setting up User Service (Arthur - Port 5001)..."
cd microservices/user-service
pip install -r requirements.txt
cd ../..

# Setup Restaurant Service
echo "🍽️  Setting up Restaurant Service (Rizki - Port 5002)..."
cd microservices/restaurant-service
pip install -r requirements.txt
cd ../..

# Setup Order Service
echo "📦 Setting up Order Service (Nadia - Port 5003)..."
cd microservices/order-service
pip install -r requirements.txt
cd ../..

# Setup Delivery Service
echo "🚚 Setting up Delivery Service (Aydin - Port 5004)..."
cd microservices/delivery-service
pip install -r requirements.txt
cd ../..

# Setup Payment Service
echo "💳 Setting up Payment Service (Reza - Port 5005)..."
cd microservices/payment-service
pip install -r requirements.txt
cd ../..

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Available services:"
echo "   - API Gateway    : http://localhost:5000"
echo "   - User Service   : http://localhost:5001 (Arthur)"
echo "   - Restaurant     : http://localhost:5002 (Rizki)"
echo "   - Order Service  : http://localhost:5003 (Nadia)"
echo "   - Delivery       : http://localhost:5004 (Aydin)"
echo "   - Payment        : http://localhost:5005 (Reza)"
echo "   - Frontend       : http://localhost:8080"
echo ""
echo "🚀 To start all services, run:"
echo "   bash scripts/run-all.sh"
echo ""
echo "📚 For more information, see README.md"