from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import hashlib
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'food-delivery-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
db = SQLAlchemy(app)

# Initialize JWT Manager
jwt = JWTManager(app)

# Setup Flask-RESTX
api = Api(app, version='1.0', title='User Service API',
          description='Microservice untuk Manajemen User dan Authentication')

# Namespace untuk user operations
ns = api.namespace('api/users', description='User operations')

# Swagger models
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email'),
    'full_name': fields.String(description='Full name'),
    'phone': fields.String(description='Phone'),
    'address': fields.String(description='Address'),
    'user_type': fields.String(description='User type'),
    'is_active': fields.Boolean(description='Active status'),
    'created_at': fields.String(description='Created timestamp'),
    'updated_at': fields.String(description='Updated timestamp'),
    'is_deleted': fields.Boolean(description='Deleted status')
})

user_input_model = api.model('UserInput', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
    'full_name': fields.String(required=True, description='Full name'),
    'phone': fields.String(description='Phone'),
    'address': fields.String(description='Address'),
    'user_type': fields.String(description='User type')
})

# ========================
#  USER SERVICE MODELS
# ========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    user_type = db.Column(db.String(20), default='customer')  # customer, restaurant_owner, admin
    is_active = db.Column(db.Boolean, default=True)  # For soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    preferences = db.Column(db.Text, nullable=True)  # JSON string for preferences
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bio': self.bio,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'preferences': self.preferences,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

def create_tables():
    with app.app_context():
        db.create_all()
        print("✅ User Service tables created")

def hash_password(password):
    """Simple password hashing - in production use proper hashing like bcrypt"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========================
# ENHANCED CRUD OPERATIONS
# ========================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "User Service",
        "version": "1.0.0",
        "description": "Microservice untuk Manajemen User dan Authentication",
        "endpoints": {
            "health": "/health",
            "api": "/api/users",
            "auth": "/api/auth",
            "profiles": "/api/profiles",
            "create": "POST /api/users",
            "read_all": "GET /api/users",
            "read_one": "GET /api/users/<id>",
            "update": "PUT /api/users/<id>",
            "patch": "PATCH /api/users/<id>",
            "soft_delete": "DELETE /api/users/<id>/soft-delete",
            "hard_delete": "DELETE /api/users/<id>",
            "restore": "POST /api/users/<id>/restore",
            "bulk_delete": "DELETE /api/users/bulk-delete",
            "bulk_restore": "POST /api/users/bulk-restore",
            "login": "POST /api/auth/login",
            "register": "POST /api/auth/register"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "user-service",
        "timestamp": datetime.utcnow().isoformat()
    })

# ========== AUTHENTICATION ENDPOINTS ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    """REGISTER - User registration"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        # Check if email is valid
        if not validate_email(email):
            return jsonify({"success": False, "error": "Invalid email format"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({"success": False, "error": "Username or email already exists"}), 400
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            phone=data.get('phone'),
            address=data.get('address'),
            user_type=data.get('user_type', 'customer')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": new_user.to_dict(),
            "message": "User registered successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """LOGIN - User authentication"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"success": False, "error": "Username and password are required"}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or user.password_hash != hash_password(password):
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
        
        if user.deleted_at:
            return jsonify({"success": False, "error": "Account is deleted"}), 400

        if not user.is_active:
            return jsonify({"success": False, "error": "Account is inactive"}), 400

        # Create JWT access token
        access_token = create_access_token(
            identity={
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.user_type
            }
        )

        return jsonify({
            "success": True,
            "data": {
                "user": user.to_dict(),
                "token": access_token
            },
            "message": "Login successful"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ========== USER PROFILE ENDPOINTS ==========
@app.route('/api/profiles', methods=['GET'])
def get_all_profiles():
    """READ ALL - Get all user profiles"""
    try:
        profiles = UserProfile.query.filter_by(deleted_at=None).all()
        return jsonify({
            "success": True,
            "data": [p.to_dict() for p in profiles],
            "count": len(profiles)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/profiles/<int:id>', methods=['GET'])
def get_profile(id):
    """READ PROFILE - Get single user profile"""
    try:
        profile = UserProfile.query.get(id)
        if not profile or profile.deleted_at:
            return jsonify({"success": False, "error": "Profile not found"}), 404
            
        return jsonify({
            "success": True,
            "data": profile.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """CREATE PROFILE - Create user profile"""
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id'):
            return jsonify({"success": False, "error": "user_id is required"}), 400
        
        # Check if user exists
        user = User.query.get(data.get('user_id'))
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        new_profile = UserProfile(
            user_id=data.get('user_id'),
            bio=data.get('bio'),
            date_of_birth=data.get('date_of_birth'),
            preferences=data.get('preferences'),
            avatar_url=data.get('avatar_url')
        )
        
        db.session.add(new_profile)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": new_profile.to_dict(),
            "message": "Profile created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== USER CRUD OPERATIONS ==========

@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users')
    def get(self):
        """READ ALL - Get all users"""
        try:
            include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

            if include_deleted:
                users = User.query.all()
            else:
                users = User.query.filter_by(deleted_at=None).all()

            # Return proper JSON response with serialized data
            return jsonify({
                "success": True,
                "data": [u.to_dict() for u in users],
                "count": len(users)
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @ns.doc('create_user')
    @ns.expect(user_input_model)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """CREATE - Create new user"""
        try:
            data = request.get_json()
            if not data:
                api.abort(400, "Request body is required")

            missing_fields = []
            if not data.get('username'):
                missing_fields.append('username')
            if not data.get('email'):
                missing_fields.append('email')
            if not data.get('password'):
                missing_fields.append('password')
            if not data.get('full_name'):
                missing_fields.append('full_name')

            if missing_fields:
                api.abort(400, f"Missing required fields: {', '.join(missing_fields)}")

            new_user = User(
                username=data.get('username'),
                email=data.get('email'),
                password_hash=hash_password(data.get('password', '')),
                full_name=data.get('full_name', ''),
                phone=data.get('phone'),
                address=data.get('address'),
                user_type=data.get('user_type', 'customer')
            )

            db.session.add(new_user)
            db.session.commit()

            return new_user.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error creating user: {str(e)}")

@ns.route('/<int:id>')
class UserDetail(Resource):
    @ns.doc('get_user')
    def get(self, id):
        """READ BY ID - Get single user"""
        try:
            user = User.query.get(id)
            if not user:
                return jsonify({"success": False, "error": f"User {id} not found"}), 404

            if user.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true':
                return jsonify({"success": False, "error": f"User {id} not found"}), 404

            return jsonify({
                "success": True,
                "data": user.to_dict()
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @ns.doc('update_user')
    @ns.expect(user_input_model)
    @ns.marshal_with(user_model)
    def put(self, id):
        """UPDATE - Full update of user"""
        try:
            user = User.query.get(id)
            if not user:
                api.abort(404, f"User {id} not found")

            if user.deleted_at:
                api.abort(400, "Cannot update deleted user")

            data = request.get_json()
            if not data:
                api.abort(400, "No data provided")

            # Update fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'address' in data:
                user.address = data['address']
            if 'user_type' in data:
                user.user_type = data['user_type']
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'password' in data:
                user.password_hash = hash_password(data['password'])

            user.updated_at = datetime.utcnow()
            db.session.commit()

            return user.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error updating user: {str(e)}")

    @ns.doc('delete_user')
    def delete(self, id):
        """DELETE - Hard delete user"""
        try:
            user = User.query.get(id)
            if not user:
                api.abort(404, f"User {id} not found")

            # Delete associated profiles first
            UserProfile.query.filter_by(user_id=id).delete()

            db.session.delete(user)
            db.session.commit()

            return {'message': 'User permanently deleted'}, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error deleting user: {str(e)}")

@ns.route('/<int:id>/soft-delete')
class UserSoftDelete(Resource):
    @ns.doc('soft_delete_user')
    def delete(self, id):
        """SOFT DELETE - Mark user as deleted"""
        try:
            user = User.query.get(id)
            if not user:
                api.abort(404, f"User {id} not found")

            if user.deleted_at:
                api.abort(400, "User already deleted")

            user.deleted_at = datetime.utcnow()
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.session.commit()

            return {'message': 'User soft deleted successfully', 'user': user.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error soft deleting user: {str(e)}")

@ns.route('/<int:id>/restore')
class UserRestore(Resource):
    @ns.doc('restore_user')
    @ns.marshal_with(user_model)
    def post(self, id):
        """RESTORE - Restore soft deleted user"""
        try:
            user = User.query.get(id)
            if not user:
                api.abort(404, f"User {id} not found")

            if not user.deleted_at:
                api.abort(400, "User is not deleted")

            user.deleted_at = None
            user.is_active = True
            user.updated_at = datetime.utcnow()
            db.session.commit()

            return user.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error restoring user: {str(e)}")

@ns.route('/bulk-delete')
class UserBulkDelete(Resource):
    @ns.doc('bulk_soft_delete_users')
    def delete(self):
        """BULK SOFT DELETE - Delete multiple users"""
        try:
            data = request.get_json()
            if not data or not data.get('ids'):
                api.abort(400, "IDs array is required")

            ids = data['ids']
            users = User.query.filter(User.id.in_(ids)).all()

            deleted_count = 0
            for user in users:
                if not user.deleted_at:
                    user.deleted_at = datetime.utcnow()
                    user.is_active = False
                    user.updated_at = datetime.utcnow()
                    deleted_count += 1

            db.session.commit()

            return {
                'message': f"{deleted_count} users soft deleted successfully",
                'deleted_count': deleted_count
            }, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error bulk deleting users: {str(e)}")

@ns.route('/bulk-restore')
class UserBulkRestore(Resource):
    @ns.doc('bulk_restore_users')
    def post(self):
        """BULK RESTORE - Restore multiple users"""
        try:
            data = request.get_json()
            if not data or not data.get('ids'):
                api.abort(400, "IDs array is required")

            ids = data['ids']
            users = User.query.filter(User.id.in_(ids)).all()

            restored_count = 0
            for user in users:
                if user.deleted_at:
                    user.deleted_at = None
                    user.is_active = True
                    user.updated_at = datetime.utcnow()
                    restored_count += 1

            db.session.commit()

            return {
                'message': f"{restored_count} users restored successfully",
                'restored_count': restored_count
            }, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Error bulk restoring users: {str(e)}")

if __name__ == '__main__':
    create_tables()
    PORT = 5001  # Arthur's User Service
    print(f"👤 User Service starting on port {PORT}")
    print(f"📚 Swagger Documentation: http://localhost:{PORT}/")
    print(f"🩺 Health Check: http://localhost:{PORT}/health")
    print(f"📋 Available endpoints:")
    print(f"   POST   /api/auth/register       - Register new user")
    print(f"   POST   /api/auth/login          - User login")
    print(f"   GET    /api/users               - Read all users")
    print(f"   GET    /api/users/<id>          - Read by ID")
    print(f"   POST   /api/users               - Create")
    print(f"   PUT    /api/users/<id>          - Full update")
    print(f"   DELETE /api/users/<id>/soft-delete - Soft delete")
    print(f"   DELETE /api/users/<id>          - Hard delete")
    print(f"   POST   /api/users/<id>/restore  - Restore")
    print(f"   DELETE /api/users/bulk-delete   - Bulk soft delete")
    print(f"   POST   /api/users/bulk-restore  - Bulk restore")
    print(f"   GET    /api/profiles            - Read all profiles")
    print(f"   POST   /api/profiles            - Create profile")
    app.run(host='127.0.0.1', port=PORT, debug=True)