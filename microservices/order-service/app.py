from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========================
#  ORDER SERVICE MODELS
# ========================
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, preparing, ready, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0)
    special_instructions = db.Column(db.Text, nullable=True)
    estimated_delivery_time = db.Column(db.DateTime, nullable=True)
    actual_delivery_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # For soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'order_number': self.order_number,
            'status': self.status,
            'total_amount': self.total_amount,
            'delivery_address': self.delivery_address,
            'delivery_fee': self.delivery_fee,
            'special_instructions': self.special_instructions,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, nullable=False)
    menu_item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    special_requests = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'special_requests': self.special_requests,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

class OrderStatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)  # User ID who made the change
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'notes': self.notes,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat()
        }

def create_tables():
    with app.app_context():
        db.create_all()
        print("✅ Order Service tables created")

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    import random
    random_suffix = random.randint(100, 999)
    return f"ORD-{timestamp}-{random_suffix}"

# ========================
# ENHANCED CRUD OPERATIONS
# ========================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Order Service",
        "version": "1.0.0",
        "description": "Microservice untuk Manajemen Order dan Pemesanan",
        "endpoints": {
            "health": "/health",
            "api": "/api/orders",
            "items": "/api/order-items",
            "status": "/api/status-history",
            "create": "POST /api/orders",
            "read_all": "GET /api/orders",
            "read_one": "GET /api/orders/<id>",
            "update": "PUT /api/orders/<id>",
            "patch": "PATCH /api/orders/<id>",
            "status_update": "PATCH /api/orders/<id>/status",
            "soft_delete": "DELETE /api/orders/<id>/soft-delete",
            "hard_delete": "DELETE /api/orders/<id>",
            "restore": "POST /api/orders/<id>/restore",
            "bulk_delete": "DELETE /api/orders/bulk-delete",
            "bulk_restore": "POST /api/orders/bulk-restore"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "order-service",
        "timestamp": datetime.utcnow().isoformat()
    })

# ========== ORDER ENDPOINTS ==========
@app.route('/api/orders', methods=['GET'])
def get_all_orders():
    """READ ALL - Get all orders"""
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        status_filter = request.args.get('status')
        user_filter = request.args.get('user_id')
        restaurant_filter = request.args.get('restaurant_id')

        query = Order.query
        if not include_deleted:
            query = query.filter_by(deleted_at=None)

        if status_filter:
            query = query.filter_by(status=status_filter)
        if user_filter:
            query = query.filter_by(user_id=user_filter)
        if restaurant_filter:
            query = query.filter_by(restaurant_id=restaurant_filter)

        orders = query.order_by(Order.created_at.desc()).all()

        return {
            "success": True,
            "data": [o.to_dict() for o in orders],
            "count": len(orders),
            "filters": {
                "include_deleted": include_deleted,
                "status": status_filter,
                "user_id": user_filter,
                "restaurant_id": restaurant_filter
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders/<int:id>', methods=['GET'])
def get_order(id):
    """READ BY ID - Get single order"""
    try:
        order = Order.query.get(id)
        if not order:
            return {"success": False, "error": "Order not found"}, 404

        if order.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true':
            return {"success": False, "error": "Order not found"}, 404

        # Get order items
        order_items = OrderItem.query.filter_by(order_id=id, deleted_at=None).all()

        # Get status history
        status_history = OrderStatusHistory.query.filter_by(order_id=id).order_by(OrderStatusHistory.created_at.desc()).all()

        return {
            "success": True,
            "data": {
                "order": order.to_dict(),
                "items": [item.to_dict() for item in order_items],
                "status_history": [history.to_dict() for history in status_history]
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """CREATE - Create new order"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['user_id', 'restaurant_id', 'items', 'delivery_address']
        for field in required_fields:
            if not data or not data.get(field):
                return {"success": False, "error": f"{field} is required"}, 400

        user_id = data.get('user_id')
        restaurant_id = data.get('restaurant_id')
        items = data.get('items', [])
        delivery_address = data.get('delivery_address')
        special_instructions = data.get('special_instructions', '')

        if not items:
            return {"success": False, "error": "At least one item is required"}, 400

        # Calculate total amount
        total_amount = 0
        for item in items:
            if not item.get('menu_item_id') or not item.get('quantity') or not item.get('unit_price'):
                return {"success": False, "error": "Each item requires menu_item_id, quantity, and unit_price"}, 400
            total_amount += item.get('quantity') * item.get('unit_price')

        # Calculate delivery fee (simple logic: free delivery for orders > 50000)
        delivery_fee = 0.0 if total_amount > 50000 else 5000.0

        # Generate order number
        order_number = generate_order_number()

        # Create order
        new_order = Order(
            user_id=user_id,
            restaurant_id=restaurant_id,
            order_number=order_number,
            status='pending',
            total_amount=total_amount + delivery_fee,
            delivery_address=delivery_address,
            delivery_fee=delivery_fee,
            special_instructions=special_instructions,
            estimated_delivery_time=datetime.utcnow() + timedelta(minutes=30)
        )

        db.session.add(new_order)
        db.session.flush()  # Get the order ID

        # Create order items
        for item in items:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item.get('menu_item_id'),
                menu_item_name=item.get('menu_item_name', 'Unknown Item'),
                quantity=item.get('quantity'),
                unit_price=item.get('unit_price'),
                total_price=item.get('quantity') * item.get('unit_price'),
                special_requests=item.get('special_requests', '')
            )
            db.session.add(order_item)

        # Create status history
        status_history = OrderStatusHistory(
            order_id=new_order.id,
            old_status=None,
            new_status='pending',
            notes='Order created',
            updated_by=user_id
        )
        db.session.add(status_history)

        db.session.commit()

        return {
            "success": True,
            "data": new_order.to_dict(),
            "message": "Order created successfully"
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders/<int:id>', methods=['PATCH'])
def update_order_status(id):
    """UPDATE STATUS - Update order status"""
    try:
        order = Order.query.get(id)
        if not order:
            return {"success": False, "error": "Order not found"}, 404

        if order.deleted_at:
            return {"success": False, "error": "Cannot update deleted order"}, 400

        data = request.get_json()
        if not data or not data.get('status'):
            return {"success": False, "error": "Status is required"}, 400

        new_status = data.get('status')
        notes = data.get('notes', '')
        updated_by = data.get('updated_by')

        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}, 400

        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()

        # Set actual delivery time when status becomes 'delivered'
        if new_status == 'delivered':
            order.actual_delivery_time = datetime.utcnow()

        # Create status history
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
            updated_by=updated_by
        )
        db.session.add(status_history)

        db.session.commit()

        return {
            "success": True,
            "data": order.to_dict(),
            "message": f"Order status updated from '{old_status}' to '{new_status}'"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

# ========== DELETE OPERATIONS ==========
@app.route('/api/orders/<int:id>/soft-delete', methods=['DELETE'])
def soft_delete_order(id):
    """SOFT DELETE - Mark order as deleted"""
    try:
        order = Order.query.get(id)
        if not order:
            return {"success": False, "error": "Order not found"}, 404

        if order.deleted_at:
            return {"success": False, "error": "Order already deleted"}, 400

        order.deleted_at = datetime.utcnow()
        order.is_active = False
        order.updated_at = datetime.utcnow()

        # Soft delete all order items
        order_items = OrderItem.query.filter_by(order_id=id).all()
        for item in order_items:
            item.deleted_at = datetime.utcnow()

        db.session.commit()

        return {
            "success": True,
            "data": order.to_dict(),
            "message": "Order soft deleted successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders/<int:id>', methods=['DELETE'])
def hard_delete_order(id):
    """HARD DELETE - Permanently delete order"""
    try:
        order = Order.query.get(id)
        if not order:
            return {"success": False, "error": "Order not found"}, 404

        # Delete associated items and status history
        OrderItem.query.filter_by(order_id=id).delete()
        OrderStatusHistory.query.filter_by(order_id=id).delete()

        db.session.delete(order)
        db.session.commit()

        return {
            "success": True,
            "message": "Order permanently deleted"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders/<int:id>/restore', methods=['POST'])
def restore_order(id):
    """RESTORE - Restore soft deleted order"""
    try:
        order = Order.query.get(id)
        if not order:
            return {"success": False, "error": "Order not found"}, 404

        if not order.deleted_at:
            return {"success": False, "error": "Order is not deleted"}, 400

        order.deleted_at = None
        order.is_active = True
        order.updated_at = datetime.utcnow()

        # Restore all order items
        order_items = OrderItem.query.filter_by(order_id=id).all()
        for item in order_items:
            item.deleted_at = None

        db.session.commit()

        return {
            "success": True,
            "data": order.to_dict(),
            "message": "Order restored successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders/bulk-delete', methods=['DELETE'])
def bulk_soft_delete_orders():
    """BULK SOFT DELETE - Delete multiple orders"""
    try:
        data = request.get_json()
        if not data or not data.get('ids'):
            return {"success": False, "error": "IDs array is required"}, 400

        ids = data['ids']
        orders = Order.query.filter(Order.id.in_(ids)).all()

        deleted_count = 0
        for order in orders:
            if not order.deleted_at:
                order.deleted_at = datetime.utcnow()
                order.is_active = False
                order.updated_at = datetime.utcnow()

                # Soft delete order items
                order_items = OrderItem.query.filter_by(order_id=order.id).all()
                for item in order_items:
                    item.deleted_at = datetime.utcnow()

                deleted_count += 1

        db.session.commit()

        return {
            "success": True,
            "message": f"{deleted_count} orders soft deleted successfully",
            "deleted_count": deleted_count
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/orders/bulk-restore', methods=['POST'])
def bulk_restore_orders():
    """BULK RESTORE - Restore multiple orders"""
    try:
        data = request.get_json()
        if not data or not data.get('ids'):
            return {"success": False, "error": "IDs array is required"}, 400

        ids = data['ids']
        orders = Order.query.filter(Order.id.in_(ids)).all()

        restored_count = 0
        for order in orders:
            if order.deleted_at:
                order.deleted_at = None
                order.is_active = True
                order.updated_at = datetime.utcnow()

                # Restore order items
                order_items = OrderItem.query.filter_by(order_id=order.id).all()
                for item in order_items:
                    item.deleted_at = None

                restored_count += 1

        db.session.commit()

        return {
            "success": True,
            "message": f"{restored_count} orders restored successfully",
            "restored_count": restored_count
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

if __name__ == '__main__':
    create_tables()
    PORT = 5003  # Nadia's Order Service
    print(f"📦 Order Service starting on port {PORT}")
    print(f"📋 Available endpoints:")
    print(f"   POST   /api/orders               - Create new order")
    print(f"   GET    /api/orders               - Read all orders")
    print(f"   GET    /api/orders/<id>          - Read by ID with items & history")
    print(f"   PATCH  /api/orders/<id>/status   - Update order status")
    print(f"   DELETE /api/orders/<id>/soft-delete - Soft delete")
    print(f"   DELETE /api/orders/<id>          - Hard delete")
    print(f"   POST   /api/orders/<id>/restore  - Restore")
    print(f"   DELETE /api/orders/bulk-delete   - Bulk soft delete")
    print(f"   POST   /api/orders/bulk-restore  - Bulk restore")
    print(f"   GET    /api/order-items          - Read all order items")
    print(f"   GET    /api/status-history       - Read status history")
    app.run(host='127.0.0.1', port=PORT, debug=True)