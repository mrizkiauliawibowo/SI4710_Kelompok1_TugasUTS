#!/bin/bash
echo " Starting API Gateway..."
cd microservices/api-gateway
pip install -r requirements.txt
python app.py