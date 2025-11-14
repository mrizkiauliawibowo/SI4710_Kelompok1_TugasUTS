from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========== RESTAURANT MODEL ==========
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'rating': self.rating,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

# ========== MENU ITEM MODEL (FULL CRUD) ==========
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # appetizer, main, dessert, drink
    image_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True)
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_spicy = db.Column(db.Boolean, default=False)
    preparation_time = db.Column(db.Integer)  # minutes
    calories = db.Column(db.Integer)
    allergens = db.Column(db.Text)  # JSON string of allergens
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationship
    restaurant = db.relationship('Restaurant', backref=db.backref('menu_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'is_vegetarian': self.is_vegetarian,
            'is_spicy': self.is_spicy,
            'preparation_time': self.preparation_time,
            'calories': self.calories,
            'allergens': self.get_allergens_list(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }
    
    def get_allergens_list(self):
        """Convert allergens string to list"""
        if self.allergens:
            try:
                return eval(self.allergens) if isinstance(self.allergens, str) else self.allergens
            except:
                return []
        return []
    
    def set_allergens_list(self, allergens_list):
        """Convert allergens list to string"""
        if allergens_list:
            self.allergens = str(allergens_list)
        else:
            self.allergens = None

def create_tables():
    with app.app_context():
        db.create_all()
        print(" Database tables created")

# ========== HEALTH CHECK ==========
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "restaurant-service",
        "timestamp": datetime.utcnow().isoformat()
    })

# ========== RESTAURANT ENDPOINTS ==========
@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """READ ALL - Get all restaurants"""
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

        if include_deleted:
            restaurants = Restaurant.query.all()
        else:
            restaurants = Restaurant.query.filter_by(deleted_at=None).all()

        # Return dict directly - Flask will auto-convert to JSON
        return {
            "success": True,
            "data": [r.to_dict() for r in restaurants],
            "count": len(restaurants)
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    """READ BY ID - Get single restaurant"""
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant or (restaurant.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true'):
            return jsonify({"success": False, "error": "Restaurant not found"}), 404
            
        return jsonify({
            "success": True,
            "data": restaurant.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/restaurants', methods=['POST'])
def create_restaurant():
    """CREATE - Create new restaurant"""
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"success": False, "error": "Name is required"}), 400
        
        new_restaurant = Restaurant(
            name=data.get('name'),
            description=data.get('description', ''),
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            rating=data.get('rating', 0.0),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_restaurant)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": new_restaurant.to_dict(),
            "message": "Restaurant created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== MENU ITEM ENDPOINTS (FULL CRUD) ==========

# ===== READ OPERATIONS =====
@app.route('/api/menu-items', methods=['GET'])
def get_menu_items():
    """READ ALL - Get all menu items with filtering"""
    try:
        restaurant_id = request.args.get('restaurant_id', type=int)
        category = request.args.get('category')
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        query = MenuItem.query
        
        # Filter by restaurant
        if restaurant_id:
            query = query.filter_by(restaurant_id=restaurant_id)
            
        # Filter by category
        if category:
            query = query.filter_by(category=category)
            
        # Filter soft deleted
        if not include_deleted:
            query = query.filter_by(deleted_at=None)
            
        menu_items = query.all()
        
        return jsonify({
            "success": True,
            "data": [item.to_dict() for item in menu_items],
            "count": len(menu_items),
            "filters": {
                "restaurant_id": restaurant_id,
                "category": category,
                "include_deleted": include_deleted
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-items/<int:id>', methods=['GET'])
def get_menu_item(id):
    """READ BY ID - Get single menu item"""
    try:
        menu_item = MenuItem.query.get(id)
        if not menu_item or (menu_item.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true'):
            return jsonify({"success": False, "error": "Menu item not found"}), 404
            
        return jsonify({
            "success": True,
            "data": menu_item.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-items/restaurant/<int:restaurant_id>', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    """READ BY RESTAURANT - Get menu for specific restaurant"""
    try:
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant or (restaurant.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true'):
            return jsonify({"success": False, "error": "Restaurant not found"}), 404
            
        category = request.args.get('category')
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        query = MenuItem.query.filter_by(restaurant_id=restaurant_id)
        
        if category:
            query = query.filter_by(category=category)
        if not include_deleted:
            query = query.filter_by(deleted_at=None)
            
        menu_items = query.all()
        
        # Group by category
        menu_by_category = {}
        for item in menu_items:
            cat = item.category or 'uncategorized'
            if cat not in menu_by_category:
                menu_by_category[cat] = []
            menu_by_category[cat].append(item.to_dict())
        
        return jsonify({
            "success": True,
            "restaurant": restaurant.to_dict(),
            "menu": menu_by_category,
            "total_items": len(menu_items)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ===== CREATE OPERATIONS =====
@app.route('/api/menu-items', methods=['POST'])
def create_menu_item():
    """CREATE - Create new menu item"""
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('price') or not data.get('restaurant_id'):
            return jsonify({"success": False, "error": "Name, price, and restaurant_id are required"}), 400
        
        # Check if restaurant exists
        restaurant = Restaurant.query.get(data.get('restaurant_id'))
        if not restaurant:
            return jsonify({"success": False, "error": "Restaurant not found"}), 404
        
        menu_item = MenuItem(
            restaurant_id=data.get('restaurant_id'),
            name=data.get('name'),
            description=data.get('description', ''),
            price=float(data.get('price')),
            category=data.get('category'),
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True),
            is_vegetarian=data.get('is_vegetarian', False),
            is_spicy=data.get('is_spicy', False),
            preparation_time=data.get('preparation_time'),
            calories=data.get('calories'),
            allergens=data.get('allergens', []),
            is_active=data.get('is_active', True)
        )
        
        # Set allergens
        if data.get('allergens'):
            menu_item.set_allergens_list(data.get('allergens'))
        
        db.session.add(menu_item)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": menu_item.to_dict(),
            "message": "Menu item created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ===== UPDATE OPERATIONS =====
@app.route('/api/menu-items/<int:id>', methods=['PUT'])
def update_menu_item(id):
    """UPDATE - Full update of menu item"""
    try:
        menu_item = MenuItem.query.get(id)
        if not menu_item or menu_item.deleted_at:
            return jsonify({"success": False, "error": "Menu item not found"}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Update fields
        if 'name' in data:
            menu_item.name = data['name']
        if 'description' in data:
            menu_item.description = data['description']
        if 'price' in data:
            menu_item.price = float(data['price'])
        if 'category' in data:
            menu_item.category = data['category']
        if 'image_url' in data:
            menu_item.image_url = data['image_url']
        if 'is_available' in data:
            menu_item.is_available = data['is_available']
        if 'is_vegetarian' in data:
            menu_item.is_vegetarian = data['is_vegetarian']
        if 'is_spicy' in data:
            menu_item.is_spicy = data['is_spicy']
        if 'preparation_time' in data:
            menu_item.preparation_time = data['preparation_time']
        if 'calories' in data:
            menu_item.calories = data['calories']
        if 'allergens' in data:
            menu_item.set_allergens_list(data['allergens'])
        if 'is_active' in data:
            menu_item.is_active = data['is_active']
        if 'restaurant_id' in data:
            # Check if new restaurant exists
            new_restaurant = Restaurant.query.get(data['restaurant_id'])
            if not new_restaurant:
                return jsonify({"success": False, "error": "New restaurant not found"}), 400
            menu_item.restaurant_id = data['restaurant_id']
            
        menu_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": menu_item.to_dict(),
            "message": "Menu item updated successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-items/<int:id>', methods=['PATCH'])
def partial_update_menu_item(id):
    """PARTIAL UPDATE - Update specific fields"""
    try:
        menu_item = MenuItem.query.get(id)
        if not menu_item or menu_item.deleted_at:
            return jsonify({"success": False, "error": "Menu item not found"}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Update only provided fields
        for field, value in data.items():
            if hasattr(menu_item, field) and field not in ['id', 'created_at', 'updated_at']:
                if field == 'allergens':
                    menu_item.set_allergens_list(value)
                else:
                    setattr(menu_item, field, value)
                    
        menu_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": menu_item.to_dict(),
            "message": "Menu item updated successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ===== DELETE OPERATIONS =====
@app.route('/api/menu-items/<int:id>/soft-delete', methods=['DELETE'])
def soft_delete_menu_item(id):
    """SOFT DELETE - Mark as deleted without removing from database"""
    try:
        menu_item = MenuItem.query.get(id)
        if not menu_item:
            return jsonify({"success": False, "error": "Menu item not found"}), 404
            
        if menu_item.deleted_at:
            return jsonify({"success": False, "error": "Menu item already deleted"}), 400
            
        menu_item.deleted_at = datetime.utcnow()
        menu_item.is_active = False
        menu_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": menu_item.to_dict(),
            "message": "Menu item soft deleted successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-items/<int:id>', methods=['DELETE'])
def hard_delete_menu_item(id):
    """HARD DELETE - Permanently remove from database"""
    try:
        menu_item = MenuItem.query.get(id)
        if not menu_item:
            return jsonify({"success": False, "error": "Menu item not found"}), 404
            
        db.session.delete(menu_item)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Menu item permanently deleted"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-items/<int:id>/restore', methods=['POST'])
def restore_menu_item(id):
    """RESTORE - Restore soft deleted menu item"""
    try:
        menu_item = MenuItem.query.get(id)
        if not menu_item:
            return jsonify({"success": False, "error": "Menu item not found"}), 404
            
        if not menu_item.deleted_at:
            return jsonify({"success": False, "error": "Menu item is not deleted"}), 400
            
        menu_item.deleted_at = None
        menu_item.is_active = True
        menu_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": menu_item.to_dict(),
            "message": "Menu item restored successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ===== BULK OPERATIONS =====
@app.route('/api/menu-items/bulk-delete', methods=['DELETE'])
def bulk_soft_delete_menu_items():
    """BULK SOFT DELETE - Delete multiple menu items"""
    try:
        data = request.get_json()
        if not data or not data.get('ids'):
            return jsonify({"success": False, "error": "IDs array is required"}), 400
            
        ids = data['ids']
        menu_items = MenuItem.query.filter(MenuItem.id.in_(ids)).all()
        
        deleted_count = 0
        for item in menu_items:
            if not item.deleted_at:
                item.deleted_at = datetime.utcnow()
                item.is_active = False
                item.updated_at = datetime.utcnow()
                deleted_count += 1
                
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{deleted_count} menu items soft deleted successfully",
            "deleted_count": deleted_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu-items/bulk-restore', methods=['POST'])
def bulk_restore_menu_items():
    """BULK RESTORE - Restore multiple soft deleted menu items"""
    try:
        data = request.get_json()
        if not data or not data.get('ids'):
            return jsonify({"success": False, "error": "IDs array is required"}), 400
            
        ids = data['ids']
        menu_items = MenuItem.query.filter(MenuItem.id.in_(ids)).all()
        
        restored_count = 0
        for item in menu_items:
            if item.deleted_at:
                item.deleted_at = None
                item.is_active = True
                item.updated_at = datetime.utcnow()
                restored_count += 1
                
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{restored_count} menu items restored successfully",
            "restored_count": restored_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ===== ADVANCED QUERIES =====
@app.route('/api/menu-items/filter', methods=['POST'])
def filter_menu_items():
    """ADVANCED FILTER - Filter menu items by multiple criteria"""
    try:
        data = request.get_json() or {}
        
        query = MenuItem.query
        
        # Apply filters
        if data.get('restaurant_ids'):
            query = query.filter(MenuItem.restaurant_id.in_(data['restaurant_ids']))
        if data.get('categories'):
            query = query.filter(MenuItem.category.in_(data['categories']))
        if data.get('price_min') is not None:
            query = query.filter(MenuItem.price >= data['price_min'])
        if data.get('price_max') is not None:
            query = query.filter(MenuItem.price <= data['price_max'])
        if data.get('is_vegetarian') is not None:
            query = query.filter(MenuItem.is_vegetarian == data['is_vegetarian'])
        if data.get('is_spicy') is not None:
            query = query.filter(MenuItem.is_spicy == data['is_spicy'])
        if data.get('include_deleted') is False:
            query = query.filter(MenuItem.deleted_at == None)
            
        # Pagination
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        menu_items = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            "success": True,
            "data": [item.to_dict() for item in menu_items.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": menu_items.total,
                "pages": menu_items.pages,
                "has_next": menu_items.has_next,
                "has_prev": menu_items.has_prev
            },
            "filters": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    create_tables()
    PORT = 5002  # Restaurant Service
    print(f" Restaurant Service starting on port {PORT}")
    print(f" Available endpoints:")
    print(f"   Restaurants:")
    print(f"     GET  /api/restaurants              - Read all restaurants")
    print(f"     GET  /api/restaurants/<id>         - Read restaurant by ID")
    print(f"     POST /api/restaurants              - Create restaurant")
    print(f"   Menu Items (Full CRUD):")
    print(f"     GET  /api/menu-items               - Read all menu items")
    print(f"     GET  /api/menu-items/<id>          - Read menu item by ID")
    print(f"     GET  /api/menu-items/restaurant/<id> - Get restaurant menu")
    print(f"     POST /api/menu-items               - Create menu item")
    print(f"     PUT  /api/menu-items/<id>          - Full update menu item")
    print(f"     PATCH/api/menu-items/<id>          - Partial update menu item")
    print(f"     DELETE /api/menu-items/<id>/soft-delete - Soft delete")
    print(f"     DELETE /api/menu-items/<id>        - Hard delete")
    print(f"     POST /api/menu-items/<id>/restore  - Restore")
    print(f"     DELETE /api/menu-items/bulk-delete - Bulk soft delete")
    print(f"     POST /api/menu-items/bulk-restore  - Bulk restore")
    print(f"     POST /api/menu-items/filter        - Advanced filtering")
    app.run(host='127.0.0.1', port=PORT, debug=True)