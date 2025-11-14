#!/bin/bash

# ========================================
# Food Delivery System - Run All Services
# ========================================
# Usage: bash run-all.sh
# This script starts all 5 microservices + API Gateway

echo ""
echo "=========================================="
echo "🚀 Starting Food Delivery System..."
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Trap Ctrl+C to stop all background processes
trap 'killall' INT

killall() {
    echo ""
    echo -e "${YELLOW}⏹️  Stopping all services...${NC}"
    pkill -f "python.*app.py" 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local developer=$3
    
    echo -e "${BLUE}▶ Starting $service_name on port $port ($developer)...${NC}"
    cd "microservices/$service_name"
    nohup python app.py > "../../logs/$service_name.log" 2>&1 &
    cd ../..
    sleep 2
}

# Create logs directory
mkdir -p logs

# Kill existing services first
echo -e "${YELLOW}⏹️  Stopping existing services...${NC}"
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

echo ""
echo -e "${GREEN}✅ Ready to start services${NC}"
echo ""

# Start API Gateway
echo -e "${BLUE}▶ Starting API Gateway on port 5000...${NC}"
cd "microservices/api-gateway"
nohup python app.py > "../../logs/api-gateway.log" 2>&1 &
cd ../..
sleep 3

# Start all services
start_service "user-service" "5001" "ARTHUR"
start_service "restaurant-service" "5002" "Rizki"
start_service "order-service" "5003" "Nadia"
start_service "delivery-service" "5004" "Aydin"
start_service "payment-service" "5005" "Reza"

echo ""
echo -e "${GREEN}=========================================="
echo "✅ All services started successfully!"
echo "==========================================${NC}"
echo ""
echo "📋 Services Running:"
echo "   🔗 API Gateway:         http://localhost:5000"
echo "   👤 User Service:        http://localhost:5001 (ARTHUR)"
echo "   🍽️  Restaurant Service:  http://localhost:5002 (Rizki)"
echo "   📦 Order Service:       http://localhost:5003 (Nadia)"
echo "   🚚 Delivery Service:    http://localhost:5004 (Aydin)"
echo "   💳 Payment Service:     http://localhost:5005 (Reza)"
echo ""
echo "📚 Documentation:"
echo "   • Swagger API:  http://localhost:5000/"
echo "   • Health:       http://localhost:5000/health"
echo ""
echo "🧪 Testing:"
echo "   • Postman Collection: Import 'POSTMAN_COLLECTION_LENGKAP.json'"
echo "   • Testing Guide: Read 'POSTMAN_TUTORIAL_LENGKAP.md'"
echo ""
echo "📊 Logs:"
echo "   • Gateway Log:   logs/api-gateway.log"
echo "   • User Log:      logs/user-service.log"
echo "   • Restaurant Log: logs/restaurant-service.log"
echo "   • Order Log:     logs/order-service.log"
echo "   • Delivery Log:  logs/delivery-service.log"
echo "   • Payment Log:   logs/payment-service.log"
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
while true; do
    sleep 1
    # Check if services are still running
    if ! pgrep -f "python.*api-gateway/app.py" > /dev/null; then
        echo -e "${RED}❌ API Gateway crashed!${NC}"
    fi
done