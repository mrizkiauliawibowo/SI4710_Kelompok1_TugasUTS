from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory, send_file
from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import requests
import logging
import os
import datetime
from functools import wraps

from swagger_config import setup_swagger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'food-delivery-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=24)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gateway-secret-key')

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
api = setup_swagger(app)

# Service URLs
SERVICES = {
    'user-service': 'http://localhost:5001',
    'restaurant-service': 'http://localhost:5002', 
    'order-service': 'http://localhost:5003',
    'delivery-service': 'http://localhost:5004',
    'payment-service': 'http://localhost:5005'
}

# Demo user database (in production, use real database)
USERS = [
    {
        "id": 1,
        "username": "admin",
        "password": "admin123",
        "email": "admin@fooddelivery.com",
        "role": "admin"
    },
    {
        "id": 2,
        "username": "user",
        "password": "user123", 
        "email": "user@fooddelivery.com",
        "role": "user"
    }
]

# ========== AUTHENTICATION ENDPOINTS ==========

@api.route('/auth/login')
class Login(Resource):
    @api.doc('login')
    @api.expect(api.model('Login', {
        'username': fields.String(required=True, description='Username or Email'),
        'password': fields.String(required=True, description='Password')
    }))
    @api.marshal_with(api.model('LoginResponse', {
        'success': fields.Boolean(description='Login success status'),
        'access_token': fields.String(description='JWT access token'),
        'user': fields.Nested(api.model('User', {
            'id': fields.Integer(description='User ID'),
            'username': fields.String(description='Username'),
            'email': fields.String(description='Email'),
            'role': fields.String(description='User role')
        })),
        'message': fields.String(description='Response message')
    }))
    def post(self):
        """Login user dan mendapatkan JWT token"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return {
                'success': False,
                'message': 'Username/email and password are required'
            }, 400

        # Find user by username or email
        user = next((u for u in USERS if u['username'] == data['username'] or u['email'] == data['username']), None)
        
        if not user or user['password'] != data['password']:
            return {
                'success': False,
                'message': 'Invalid credentials'
            }, 401
        
        # Create access token
        access_token = create_access_token(
            identity={
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        )
        
        return {
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            },
            'message': 'Login successful'
        }, 200

@api.route('/auth/register')
class Register(Resource):
    @api.doc('register')
    @api.expect(api.model('Register', {
        'username': fields.String(required=True, description='Username'),
        'password': fields.String(required=True, description='Password'),
        'email': fields.String(required=True, description='Email')
    }))
    @api.marshal_with(api.model('RegisterResponse', {
        'success': fields.Boolean(description='Registration success status'),
        'message': fields.String(description='Response message')
    }))
    def post(self):
        """Register user baru"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return {
                'success': False,
                'message': 'Username, password, and email are required'
            }, 400
        
        # Check if username already exists
        if next((u for u in USERS if u['username'] == data['username']), None):
            return {
                'success': False,
                'message': 'Username already exists'
            }, 400
        
        # In production, hash password and save to database
        new_user = {
            'id': len(USERS) + 1,
            'username': data['username'],
            'password': data['password'],  # Hash in production
            'email': data['email'],
            'role': 'user'
        }
        
        return {
            'success': True,
            'message': 'User registered successfully'
        }, 201

@api.route('/auth/verify')
class VerifyToken(Resource):
    @api.doc('verify_token')
    @api.marshal_with(api.model('VerifyResponse', {
        'success': fields.Boolean(description='Token verification status'),
        'user': fields.Nested(api.model('User', {
            'id': fields.Integer(description='User ID'),
            'username': fields.String(description='Username'),
            'email': fields.String(description='Email'),
            'role': fields.String(description='User role')
        }))
    }))
    @jwt_required()
    def get(self):
        """Verify JWT token"""
        current_user = get_jwt_identity()
        return {
            'success': True,
            'user': current_user
        }, 200

# ========== HELPER FUNCTIONS ==========

def auth_required(f):
    """Decorator untuk required authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator untuk admin-only access"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if current_user.get('role') != 'admin':
            return {
                'success': False,
                'message': 'Admin access required'
            }, 403
        return f(*args, **kwargs)
    return decorated_function

def forward_request(service_name, path):
    """Forward request to appropriate microservice"""
    if service_name not in SERVICES:
        return jsonify({
            "success": False,
            "error": "Service not found",
            "message": f"Service '{service_name}' is not available"
        }), 404

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

        # Return response as text/json string to avoid bytes serialization issue
        # This prevents Flask-RESTX from trying to serialize bytes to JSON
        if response.headers.get('content-type', '').startswith('application/json'):
            # Return as JSON response object
            return response.json(), response.status_code
        else:
            # Return as text for non-JSON content
            return response.text, response.status_code, {'Content-Type': response.headers.get('content-type', 'text/plain')}
    except requests.exceptions.ConnectionError:
        logger.error(f"Service {service_name} unavailable")
        return jsonify({
            "success": False,
            "error": f"Service '{service_name}' is currently unavailable",
            "message": "Please try again later"
        }), 503
    except requests.exceptions.Timeout:
        logger.error(f"Service {service_name} timeout")
        return jsonify({
            "success": False,
            "error": f"Service '{service_name}' request timeout",
            "message": "Request took too long to complete"
        }), 504
    except Exception as e:
        logger.error(f"Gateway error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal gateway error",
            "message": "An unexpected error occurred"
        }), 500

# ========== AUTHENTICATED PROXY ROUTES ==========

@api.route('/api/user-service/<path:path>')
@api.doc('user-service-proxy')
class UserServiceProxy(Resource):
    def get(self, path):
        """Proxy GET requests to User Service"""
        return forward_request('user-service', path)
    
    def post(self, path):
        """Proxy POST requests to User Service"""
        return forward_request('user-service', path)
    
    def put(self, path):
        """Proxy PUT requests to User Service"""
        return forward_request('user-service', path)
    
    def patch(self, path):
        """Proxy PATCH requests to User Service"""
        return forward_request('user-service', path)
    
    def delete(self, path):
        """Proxy DELETE requests to User Service"""
        return forward_request('user-service', path)

@api.route('/api/restaurant-service/<path:path>')
@api.doc('restaurant-service-proxy')
class RestaurantServiceProxy(Resource):
    def get(self, path):
        """Proxy GET requests to Restaurant Service"""
        return forward_request('restaurant-service', path)
    
    def post(self, path):
        """Proxy POST requests to Restaurant Service"""
        return forward_request('restaurant-service', path)
    
    def put(self, path):
        """Proxy PUT requests to Restaurant Service"""
        return forward_request('restaurant-service', path)
    
    def patch(self, path):
        """Proxy PATCH requests to Restaurant Service"""
        return forward_request('restaurant-service', path)
    
    def delete(self, path):
        """Proxy DELETE requests to Restaurant Service"""
        return forward_request('restaurant-service', path)

@api.route('/api/order-service/<path:path>')
@api.doc('order-service-proxy')
class OrderServiceProxy(Resource):
    def get(self, path):
        """Proxy GET requests to Order Service"""
        return forward_request('order-service', path)
    
    def post(self, path):
        """Proxy POST requests to Order Service"""
        return forward_request('order-service', path)
    
    def put(self, path):
        """Proxy PUT requests to Order Service"""
        return forward_request('order-service', path)
    
    def patch(self, path):
        """Proxy PATCH requests to Order Service"""
        return forward_request('order-service', path)
    
    def delete(self, path):
        """Proxy DELETE requests to Order Service"""
        return forward_request('order-service', path)

@api.route('/api/delivery-service/<path:path>')
@api.doc('delivery-service-proxy')
class DeliveryServiceProxy(Resource):
    def get(self, path):
        """Proxy GET requests to Delivery Service"""
        return forward_request('delivery-service', path)
    
    def post(self, path):
        """Proxy POST requests to Delivery Service"""
        return forward_request('delivery-service', path)
    
    def put(self, path):
        """Proxy PUT requests to Delivery Service"""
        return forward_request('delivery-service', path)
    
    def patch(self, path):
        """Proxy PATCH requests to Delivery Service"""
        return forward_request('delivery-service', path)
    
    def delete(self, path):
        """Proxy DELETE requests to Delivery Service"""
        return forward_request('delivery-service', path)

@api.route('/api/payment-service/<path:path>')
@api.doc('payment-service-proxy')
class PaymentServiceProxy(Resource):
    def get(self, path):
        """Proxy GET requests to Payment Service"""
        return forward_request('payment-service', path)
    
    def post(self, path):
        """Proxy POST requests to Payment Service"""
        return forward_request('payment-service', path)
    
    def put(self, path):
        """Proxy PUT requests to Payment Service"""
        return forward_request('payment-service', path)
    
    def patch(self, path):
        """Proxy PATCH requests to Payment Service"""
        return forward_request('payment-service', path)
    
    def delete(self, path):
        """Proxy DELETE requests to Payment Service"""
        return forward_request('payment-service', path)

# ========== SYSTEM ENDPOINTS ==========

@api.route('/health')
@api.doc('health-check')
class HealthCheck(Resource):
    @api.marshal_with(api.model('Health', {
        'status': fields.String(description='Service status'),
        'timestamp': fields.String(description='Current timestamp'),
        'services': fields.List(fields.String, description='Available services'),
        'version': fields.String(description='API Gateway version')
    }))
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'api-gateway',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'services': list(SERVICES.keys()),
            'version': '1.0.0'
        }

@api.route('/')
@api.doc('home')
class Home(Resource):
    def get(self):
        """API Gateway information"""
        return {
            'service': 'Food Delivery System API Gateway',
            'version': '1.0.0',
            'description': 'API Gateway untuk Food Delivery System Microservices',
            'endpoints': {
                'health': '/health',
                'documentation': '/api-docs/',
                'auth': {
                    'login': '/auth/login',
                    'register': '/auth/register', 
                    'verify': '/auth/verify'
                },
                'services': {
                    'user-service': '/api/user-service/',
                    'restaurant-service': '/api/restaurant-service/',
                    'order-service': '/api/order-service/',
                    'delivery-service': '/api/delivery-service/',
                    'payment-service': '/api/payment-service/'
                }
            },
            'authentication': 'JWT Bearer Token required for service endpoints'
        }

@api.route('/services')
@api.doc('services-list')
class ListServices(Resource):
    @api.marshal_with(api.model('Services', {
        'services': fields.List(fields.Nested(api.model('Service', {
            'name': fields.String(description='Service name'),
            'url': fields.String(description='Service URL'),
            'status': fields.String(description='Service status')
        })))
    }))
    def get(self):
        """List all available services"""
        services_status = []
        for name, url in SERVICES.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                status = 'healthy' if response.status_code == 200 else 'unhealthy'
            except:
                status = 'unknown'
            
            services_status.append({
                'name': name,
                'url': url,
                'status': status
            })
        
        return {
            'services': services_status
        }

# ========== ERROR HANDLERS ==========

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token has expired',
        'message': 'Please login again'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Invalid token',
        'message': 'Please provide a valid token'
    }), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        'success': False,
        'error': 'Authorization required',
        'message': 'Please provide a valid JWT token'
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    print(" 🔐 API Gateway starting on port 5000")
    print(" 📚 Swagger Documentation: http://localhost:5000/api-docs/")
    print(" 🔑 Authentication: JWT Bearer Token")
    print(" 🏥 Health Check: http://localhost:5000/health")
    print(" 📋 Available services:")
    for service, url in SERVICES.items():
        print(f"   - {service}: {url}")
    print("\n 📝 Demo Credentials:")
    print("   Admin: username='admin', password='admin123'")
    print("   User:  username='user', password='user123'")

    app.debug = False
    app.run(host='127.0.0.1', port=5000, debug=False)