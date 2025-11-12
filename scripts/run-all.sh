#!/bin/bash
echo " Starting Food Delivery System..."
echo "===================================="

# Kill existing services
echo "Stopping existing services..."
pkill -f "python app.py" 2>/dev/null || true
sleep 2

# Start API Gateway
echo "Starting API Gateway (5000)..."
cd microservices/api-gateway
python app.py > ../../logs/gateway.log 2>&1 &
GATEWAY_PID=$!
echo $GATEWAY_PID > ../../logs/gateway.pid

# Wait for gateway to start
sleep 3

echo ""
echo " API Gateway started on http://localhost:5000"
echo ""
echo " Manual service startup required:"
echo "   Each team member should run their service:"
echo ""
echo "   ARTHUR (5001):   cd microservices/user-service && python app.py"
echo "   rizki (5002):    cd microservices/restaurant-service && python app.py"
echo "   Nadia (5003):    cd microservices/order-service && python app.py"
echo "   aydin (5004):    cd microservices/delivery-service && python app.py"
echo "   reza (5005):     cd microservices/payment-service && python app.py"
echo ""
echo " Frontend: http://localhost:5000"
echo " API Gateway: http://localhost:5000/health"