#!/bin/bash
echo "🚀 Starting all services..."
cd microservices/user-service && python app.py &
cd microservices/restaurant-service && python app.py &
cd microservices/order-service && python app.py &
cd microservices/delivery-service && python app.py &
cd microservices/payment-service && python app.py &
cd microservices/api-gateway && python app.py &
echo "✅ All services started! Access: http://localhost:5000"