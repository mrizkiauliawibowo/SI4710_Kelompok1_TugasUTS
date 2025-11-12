from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

SERVICES = {
    'users': 'http://localhost:5001',
    'restaurants': 'http://localhost:5002', 
    'orders': 'http://localhost:5003',
    'deliveries': 'http://localhost:5004',
    'payments': 'http://localhost:5005'
}

@app.route('/<service_name>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway_proxy(service_name, path):
    """Route requests to appropriate microservice"""
    if service_name not in SERVICES:
        return jsonify({"error": "Service not found"}), 404
    
    service_url = SERVICES[service_name]
    full_url = f"{service_url}/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=full_url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            json=request.json if request.is_json else None,
            timeout=30
        )
        return Response(response.content, status=response.status_code, content_type=response.headers.get('content-type'))
    except requests.exceptions.ConnectionError:
        logger.error(f"Service {service_name} unavailable")
        return jsonify({"error": f"Service {service_name} unavailable"}), 503
    except Exception as e:
        logger.error(f"Gateway error: {str(e)}")
        return jsonify({"error": "Gateway error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "api-gateway",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Food Delivery System</title>
            <meta http-equiv="refresh" content="0; url=/index.html">
        </head>
        <body>
            <p>Redirecting to <a href="/index.html">Frontend</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print(" API Gateway starting on port 5000")
    print(" Available services:")
    for service, url in SERVICES.items():
        print(f"   - {service}: {url}")
    app.run(host='0.0.0.0', port=5000, debug=True)