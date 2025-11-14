from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime

def setup_swagger(app):
    """Setup Swagger documentation untuk API Gateway"""
    
    api = Api(
        app, 
        version='1.0',
        title='Food Delivery System API Gateway',
        description='API Gateway untuk Food Delivery System Microservices',
        doc='/api-docs/',
        contact={
            "name": "Kelompok 01",
            "email": "food.delivery@example.com"
        }
    )
    
    # Authentication Model
    auth_model = api.model('Auth', {
        'username': fields.String(required=True, description='Username'),
        'password': fields.String(required=True, description='Password'),
        'role': fields.String(description='User role (admin, user)')
    })
    
    # Health Check Model
    health_model = api.model('Health', {
        'status': fields.String(description='Service status'),
        'timestamp': fields.String(description='Current timestamp'),
        'services': fields.List(fields.String, description='Available services')
    })
    
    # Error Model
    error_model = api.model('Error', {
        'success': fields.Boolean(description='Success status'),
        'error': fields.String(description='Error message'),
        'code': fields.Integer(description='HTTP status code')
    })
    
    # User Service Namespace
    users_ns = Namespace('users', description='User Management Operations')
    api.add_namespace(users_ns, path='/api/user-service')
    
    # Restaurant Service Namespace
    restaurants_ns = Namespace('restaurants', description='Restaurant Management Operations')
    api.add_namespace(restaurants_ns, path='/api/restaurant-service')
    
    # Order Service Namespace
    orders_ns = Namespace('orders', description='Order Management Operations')
    api.add_namespace(orders_ns, path='/api/order-service')
    
    # Delivery Service Namespace
    deliveries_ns = Namespace('deliveries', description='Delivery Management Operations')
    api.add_namespace(deliveries_ns, path='/api/delivery-service')
    
    # Payment Service Namespace
    payments_ns = Namespace('payments', description='Payment Management Operations')
    api.add_namespace(payments_ns, path='/api/payment-service')
    
    return api

# Swagger components untuk User Service
user_model = {
    'id': fields.Integer(required=True, description='User ID'),
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email'),
    'phone': fields.String(description='User phone'),
    'address': fields.String(description='User address'),
    'is_active': fields.Boolean(description='User active status'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
}

user_input_model = {
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(description='User password'),
    'phone': fields.String(description='User phone'),
    'address': fields.String(description='User address')
}

# Swagger components untuk Restaurant Service
restaurant_model = {
    'id': fields.Integer(required=True, description='Restaurant ID'),
    'name': fields.String(required=True, description='Restaurant name'),
    'description': fields.String(description='Restaurant description'),
    'address': fields.String(description='Restaurant address'),
    'phone': fields.String(description='Restaurant phone'),
    'email': fields.String(description='Restaurant email'),
    'rating': fields.Float(description='Restaurant rating'),
    'is_active': fields.Boolean(description='Restaurant active status'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
}

menu_item_model = {
    'id': fields.Integer(required=True, description='Menu item ID'),
    'restaurant_id': fields.Integer(required=True, description='Restaurant ID'),
    'name': fields.String(required=True, description='Menu item name'),
    'description': fields.String(description='Menu item description'),
    'price': fields.Float(required=True, description='Menu item price'),
    'category': fields.String(description='Menu category'),
    'image_url': fields.String(description='Menu item image'),
    'is_available': fields.Boolean(description='Item availability'),
    'is_vegetarian': fields.Boolean(description='Vegetarian option'),
    'is_spicy': fields.Boolean(description='Spicy option'),
    'preparation_time': fields.Integer(description='Preparation time in minutes'),
    'calories': fields.Integer(description='Calories'),
    'allergens': fields.List(fields.String, description='Allergens list'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
}

# Swagger components untuk Order Service
order_model = {
    'id': fields.Integer(required=True, description='Order ID'),
    'user_id': fields.Integer(required=True, description='User ID'),
    'restaurant_id': fields.Integer(required=True, description='Restaurant ID'),
    'total_amount': fields.Float(required=True, description='Total amount'),
    'status': fields.String(description='Order status'),
    'delivery_address': fields.String(description='Delivery address'),
    'special_instructions': fields.String(description='Special instructions'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
}

order_item_model = {
    'menu_item_id': fields.Integer(required=True, description='Menu item ID'),
    'menu_item_name': fields.String(required=True, description='Menu item name'),
    'quantity': fields.Integer(required=True, description='Quantity ordered'),
    'price': fields.Float(required=True, description='Price per item'),
    'subtotal': fields.Float(required=True, description='Subtotal for this item')
}

# Swagger components untuk Delivery Service
delivery_model = {
    'id': fields.Integer(required=True, description='Delivery ID'),
    'order_id': fields.Integer(required=True, description='Order ID'),
    'delivery_address': fields.String(required=True, description='Delivery address'),
    'delivery_person_name': fields.String(description='Delivery person name'),
    'delivery_person_phone': fields.String(description='Delivery person phone'),
    'status': fields.String(description='Delivery status'),
    'estimated_delivery_time': fields.String(description='Estimated delivery time'),
    'actual_delivery_time': fields.String(description='Actual delivery time'),
    'delivery_fee': fields.Float(description='Delivery fee'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
}

# Swagger components untuk Payment Service
payment_model = {
    'id': fields.Integer(required=True, description='Payment ID'),
    'order_id': fields.Integer(required=True, description='Order ID'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'payment_method': fields.String(description='Payment method'),
    'status': fields.String(description='Payment status'),
    'transaction_id': fields.String(description='Transaction ID'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
}

# Common response models
success_response = {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Success message'),
    'timestamp': fields.String(description='Response timestamp')
}

list_response = {
    'success': fields.Boolean(description='Operation success status'),
    'data': fields.List(fields.Raw, description='Data list'),
    'count': fields.Integer(description='Total count'),
    'message': fields.String(description='Response message')
}