#!/bin/bash

echo "🌐 Starting API Gateway..."
echo "========================="

# Check dependencies
pip install -r requirements.txt > /dev/null 2>&1

echo "✅ API Gateway starting on port 5000"
echo "📡 Services configuration:"
echo "   - Users: http://localhost:5001"
echo "   - Restaurants: http://localhost:5002"
echo "   - Orders: http://localhost:5003" 
echo "   - Deliveries: http://localhost:5004"
echo "   - Payments: http://localhost:5005"

python app.py