from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

# Konfigurasi services
SERVICES = {
    'users': 'http://localhost:5001',
    'restaurants': 'http://localhost:5002',
    'orders': 'http://localhost:5003',
    'deliveries': 'http://localhost:5004',
    'payments': 'http://localhost:5005'
}

@app.route('/<service_name>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway_proxy(service_name, path):
    """Route request ke service yang sesuai"""
    if service_name not in SERVICES:
        return jsonify({"success": False, "error": "Service tidak ditemukan"}), 404

    service_url = SERVICES[service_name]
    full_url = f"{service_url}/{path}"

    try:
        # Forward request ke service target
        response = requests.request(
            method=request.method,
            url=full_url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            json=request.json if request.is_json else None,
            timeout=30
        )
        
        return Response(response.content, status=response.status_code)
    
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "error": f"Service {service_name} tidak available"}), 503
    except Exception as e:
        logging.error(f"Gateway error: {str(e)}")
        return jsonify({"success": False, "error": "Gateway error"}), 500

@app.route('/health', methods=['GET'])
def gateway_health():
    """Health check untuk semua services"""
    services_status = {}
    
    for service_name, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            services_status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy'
            }
        except Exception as e:
            services_status[service_name] = {'status': 'unavailable'}
    
    return jsonify({
        'gateway': 'healthy', 
        'services': services_status
    })

@app.route('/')
def home():
    """Home page redirect ke frontend"""
    return """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=/index.html">
        </head>
        <body>
            <p>Redirecting to <a href="/index.html">Frontend</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Starting API Gateway on port 5000")
    print("📡 Available services:")
    for service, url in SERVICES.items():
        print(f"   {service}: {url}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)