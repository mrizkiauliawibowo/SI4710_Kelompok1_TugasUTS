from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import random
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///delivery_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========================
#  DELIVERY SERVICE MODELS
# ========================
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False, unique=True)
    courier_id = db.Column(db.Integer, nullable=True)
    courier_name = db.Column(db.String(100), nullable=True)
    courier_phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, assigned, picked_up, in_transit, delivered, failed
    pickup_address = db.Column(db.Text, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    estimated_pickup_time = db.Column(db.DateTime, nullable=True)
    actual_pickup_time = db.Column(db.DateTime, nullable=True)
    estimated_delivery_time = db.Column(db.DateTime, nullable=True)
    actual_delivery_time = db.Column(db.DateTime, nullable=True)
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    delivery_fee = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # For soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'courier_id': self.courier_id,
            'courier_name': self.courier_name,
            'courier_phone': self.courier_phone,
            'status': self.status,
            'pickup_address': self.pickup_address,
            'delivery_address': self.delivery_address,
            'estimated_pickup_time': self.estimated_pickup_time.isoformat() if self.estimated_pickup_time else None,
            'actual_pickup_time': self.actual_pickup_time.isoformat() if self.actual_pickup_time else None,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None,
            'current_location': {
                'latitude': self.current_latitude,
                'longitude': self.current_longitude
            } if self.current_latitude and self.current_longitude else None,
            'delivery_fee': self.delivery_fee,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

class Courier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=False)  # motorcycle, bicycle, car, walking
    vehicle_number = db.Column(db.String(20), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='available')  # available, busy, offline
    rating = db.Column(db.Float, default=5.0)
    total_deliveries = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'vehicle_type': self.vehicle_type,
            'vehicle_number': self.vehicle_number,
            'license_number': self.license_number,
            'current_location': {
                'latitude': self.current_latitude,
                'longitude': self.current_longitude
            } if self.current_latitude and self.current_longitude else None,
            'status': self.status,
            'rating': self.rating,
            'total_deliveries': self.total_deliveries,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

class DeliveryLocationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    courier_id = db.Column(db.Integer, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'delivery_id': self.delivery_id,
            'courier_id': self.courier_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat()
        }

def create_tables():
    with app.app_context():
        db.create_all()
        print("✅ Delivery Service tables created")
        
        # Create sample couriers if none exist
        if Courier.query.count() == 0:
            sample_couriers = [
                Courier(name="Ahmad Rizki", phone="081234567890", email="ahmad@example.com", vehicle_type="motorcycle", vehicle_number="B 1234 ABC"),
                Courier(name="Budi Santoso", phone="081234567891", email="budi@example.com", vehicle_type="motorcycle", vehicle_number="B 5678 DEF"),
                Courier(name="Siti Nurhaliza", phone="081234567892", email="siti@example.com", vehicle_type="bicycle", vehicle_number=""),
                Courier(name="Andi Wijaya", phone="081234567893", email="andi@example.com", vehicle_type="motorcycle", vehicle_number="B 9012 GHI"),
                Courier(name="Rina Marlina", phone="081234567894", email="rina@example.com", vehicle_type="motorcycle", vehicle_number="B 3456 JKL")
            ]
            db.session.add_all(sample_couriers)
            db.session.commit()
            print("✅ Sample couriers created")

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return distance

def generate_random_coordinates(center_lat=-6.2088, center_lng=106.8456, radius_km=10):
    """Generate random coordinates within a radius (Jakarta area)"""
    lat = center_lat
    lng = center_lng
    
    # Generate random location within radius
    bearing = random.uniform(0, 360)
    distance = random.uniform(0, radius_km)
    
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)
    
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance / R) +
        math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing)
    )
    
    new_lng_rad = lng_rad + math.atan2(
        math.sin(bearing) * math.sin(distance / R) * math.cos(lat_rad),
        math.cos(distance / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    
    new_lat = math.degrees(new_lat_rad)
    new_lng = math.degrees(new_lng_rad)
    
    return new_lat, new_lng

# ========================
# ENHANCED CRUD OPERATIONS
# ========================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Delivery Service",
        "version": "1.0.0",
        "description": "Microservice untuk Manajemen Delivery dan Tracking",
        "endpoints": {
            "health": "/health",
            "api": "/api/deliveries",
            "couriers": "/api/couriers",
            "tracking": "/api/tracking",
            "locations": "/api/location-history",
            "create": "POST /api/deliveries",
            "read_all": "GET /api/deliveries",
            "read_one": "GET /api/deliveries/<id>",
            "update": "PUT /api/deliveries/<id>",
            "patch": "PATCH /api/deliveries/<id>",
            "assign_courier": "POST /api/deliveries/<id>/assign-courier",
            "update_location": "POST /api/deliveries/<id>/location",
            "track": "GET /api/tracking/<order_id>",
            "soft_delete": "DELETE /api/deliveries/<id>/soft-delete",
            "hard_delete": "DELETE /api/deliveries/<id>",
            "restore": "POST /api/deliveries/<id>/restore",
            "bulk_delete": "DELETE /api/deliveries/bulk-delete",
            "bulk_restore": "POST /api/deliveries/bulk-restore"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "delivery-service",
        "timestamp": datetime.utcnow().isoformat()
    })

# ========== COURIER ENDPOINTS ==========
@app.route('/api/couriers', methods=['GET'])
def get_all_couriers():
    """READ ALL - Get all couriers"""
    try:
        status_filter = request.args.get('status')
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        query = Courier.query
        if not include_deleted:
            query = query.filter_by(deleted_at=None)
        if status_filter:
            query = query.filter_by(status=status_filter)
            
        couriers = query.order_by(Courier.name).all()
        
        return jsonify({
            "success": True,
            "data": [c.to_dict() for c in couriers],
            "count": len(couriers)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/couriers/<int:id>', methods=['GET'])
def get_courier(id):
    """READ BY ID - Get single courier"""
    try:
        courier = Courier.query.get(id)
        if not courier or courier.deleted_at:
            return jsonify({"success": False, "error": "Courier not found"}), 404
            
        return jsonify({
            "success": True,
            "data": courier.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/couriers', methods=['POST'])
def create_courier():
    """CREATE - Create new courier"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'phone', 'vehicle_type']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        new_courier = Courier(
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            vehicle_type=data.get('vehicle_type'),
            vehicle_number=data.get('vehicle_number'),
            license_number=data.get('license_number'),
            status=data.get('status', 'available')
        )
        
        db.session.add(new_courier)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": new_courier.to_dict(),
            "message": "Courier created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== DELIVERY ENDPOINTS ==========
@app.route('/api/deliveries', methods=['GET'])
def get_all_deliveries():
    """READ ALL - Get all deliveries"""
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        status_filter = request.args.get('status')
        courier_filter = request.args.get('courier_id')

        query = Delivery.query
        if not include_deleted:
            query = query.filter_by(deleted_at=None)
        if status_filter:
            query = query.filter_by(status=status_filter)
        if courier_filter:
            query = query.filter_by(courier_id=courier_filter)

        deliveries = query.order_by(Delivery.created_at.desc()).all()

        return {
            "success": True,
            "data": [d.to_dict() for d in deliveries],
            "count": len(deliveries),
            "filters": {
                "include_deleted": include_deleted,
                "status": status_filter,
                "courier_id": courier_filter
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/deliveries/<int:id>', methods=['GET'])
def get_delivery(id):
    """READ BY ID - Get single delivery"""
    try:
        delivery = Delivery.query.get(id)
        if not delivery:
            return {"success": False, "error": "Delivery not found"}, 404

        if delivery.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true':
            return {"success": False, "error": "Delivery not found"}, 404

        # Get location history
        location_history = DeliveryLocationHistory.query.filter_by(delivery_id=id).order_by(DeliveryLocationHistory.timestamp.desc()).all()

        return {
            "success": True,
            "data": {
                "delivery": delivery.to_dict(),
                "location_history": [loc.to_dict() for loc in location_history]
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/deliveries', methods=['POST'])
def create_delivery():
    """CREATE - Create new delivery"""
    try:
        data = request.get_json()
        
        required_fields = ['order_id', 'pickup_address', 'delivery_address']
        for field in required_fields:
            if not data or not data.get(field):
                return {"success": False, "error": f"{field} is required"}, 400

        order_id = data.get('order_id')

        # Check if delivery already exists for this order
        existing_delivery = Delivery.query.filter_by(order_id=order_id).first()
        if existing_delivery:
            return {"success": False, "error": "Delivery already exists for this order"}, 400

        new_delivery = Delivery(
            order_id=order_id,
            status='pending',
            pickup_address=data.get('pickup_address'),
            delivery_address=data.get('delivery_address'),
            estimated_pickup_time=data.get('estimated_pickup_time'),
            estimated_delivery_time=data.get('estimated_delivery_time'),
            delivery_fee=data.get('delivery_fee', 0.0),
            notes=data.get('notes', '')
        )

        db.session.add(new_delivery)
        db.session.commit()

        return {
            "success": True,
            "data": new_delivery.to_dict(),
            "message": "Delivery created successfully"
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/deliveries/<int:id>/assign-courier', methods=['POST'])
def assign_courier(id):
    """ASSIGN COURIER - Assign courier to delivery"""
    try:
        delivery = Delivery.query.get(id)
        if not delivery:
            return jsonify({"success": False, "error": "Delivery not found"}), 404
            
        if delivery.deleted_at:
            return jsonify({"success": False, "error": "Cannot assign courier to deleted delivery"}), 400
            
        data = request.get_json()
        if not data or not data.get('courier_id'):
            return {"success": False, "error": "courier_id is required"}, 400

        courier_id = data.get('courier_id')
        courier = Courier.query.get(courier_id)

        if not courier or courier.deleted_at:
            return {"success": False, "error": "Courier not found"}, 404

        if courier.status == 'busy':
            return {"success": False, "error": "Courier is currently busy"}, 400

        # Update delivery
        delivery.courier_id = courier_id
        delivery.courier_name = courier.name
        delivery.courier_phone = courier.phone
        delivery.status = 'assigned'
        delivery.estimated_pickup_time = datetime.utcnow() + timedelta(minutes=15)
        delivery.updated_at = datetime.utcnow()

        # Update courier status
        courier.status = 'busy'

        # Create location history entry
        location_entry = DeliveryLocationHistory(
            delivery_id=delivery.id,
            courier_id=courier_id,
            latitude=courier.current_latitude or -6.2088,
            longitude=courier.current_longitude or 106.8456,
            status='assigned',
            notes=f'Courier {courier.name} assigned to delivery'
        )

        db.session.add(location_entry)
        db.session.commit()

        return {
            "success": True,
            "data": delivery.to_dict(),
            "message": f"Courier {courier.name} assigned successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/deliveries/<int:id>/location', methods=['POST'])
def update_delivery_location(id):
    """UPDATE LOCATION - Update courier location"""
    try:
        delivery = Delivery.query.get(id)
        if not delivery:
            return jsonify({"success": False, "error": "Delivery not found"}), 404
            
        if delivery.deleted_at:
            return jsonify({"success": False, "error": "Cannot update location of deleted delivery"}), 400
            
        data = request.get_json()
        if not data or not data.get('latitude') or not data.get('longitude'):
            return {"success": False, "error": "latitude and longitude are required"}, 400

        latitude = data.get('latitude')
        longitude = data.get('longitude')
        status = data.get('status')
        notes = data.get('notes', '')

        # Update delivery location
        delivery.current_latitude = latitude
        delivery.current_longitude = longitude
        if status:
            delivery.status = status
        delivery.updated_at = datetime.utcnow()

        # Update courier location if courier is assigned
        if delivery.courier_id:
            courier = Courier.query.get(delivery.courier_id)
            if courier:
                courier.current_latitude = latitude
                courier.current_longitude = longitude

        # Create location history entry
        location_entry = DeliveryLocationHistory(
            delivery_id=delivery.id,
            courier_id=delivery.courier_id,
            latitude=latitude,
            longitude=longitude,
            status=status,
            notes=notes
        )

        db.session.add(location_entry)
        db.session.commit()

        return {
            "success": True,
            "data": delivery.to_dict(),
            "message": "Location updated successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/tracking/<int:order_id>', methods=['GET'])
def track_delivery(order_id):
    """TRACK - Get delivery tracking information"""
    try:
        delivery = Delivery.query.filter_by(order_id=order_id).first()
        if not delivery:
            return {"success": False, "error": "Delivery not found for this order"}, 404

        # Get location history
        location_history = DeliveryLocationHistory.query.filter_by(delivery_id=delivery.id).order_by(DeliveryLocationHistory.timestamp.asc()).all()

        # Get courier info
        courier_info = None
        if delivery.courier_id:
            courier = Courier.query.get(delivery.courier_id)
            if courier:
                courier_info = courier.to_dict()

        return {
            "success": True,
            "data": {
                "delivery": delivery.to_dict(),
                "courier": courier_info,
                "tracking_history": [loc.to_dict() for loc in location_history],
                "estimated_delivery_time": delivery.estimated_delivery_time.isoformat() if delivery.estimated_delivery_time else None
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# ========== DELETE OPERATIONS ==========
@app.route('/api/deliveries/<int:id>/soft-delete', methods=['DELETE'])
def soft_delete_delivery(id):
    """SOFT DELETE - Mark delivery as deleted"""
    try:
        delivery = Delivery.query.get(id)
        if not delivery:
            return {"success": False, "error": "Delivery not found"}, 404

        if delivery.deleted_at:
            return {"success": False, "error": "Delivery already deleted"}, 400

        delivery.deleted_at = datetime.utcnow()
        delivery.is_active = False
        delivery.updated_at = datetime.utcnow()

        # Free up courier if assigned
        if delivery.courier_id:
            courier = Courier.query.get(delivery.courier_id)
            if courier and courier.status == 'busy':
                courier.status = 'available'

        db.session.commit()

        return {
            "success": True,
            "data": delivery.to_dict(),
            "message": "Delivery soft deleted successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/deliveries/<int:id>/restore', methods=['POST'])
def restore_delivery(id):
    """RESTORE - Restore soft deleted delivery"""
    try:
        delivery = Delivery.query.get(id)
        if not delivery:
            return {"success": False, "error": "Delivery not found"}, 404

        if not delivery.deleted_at:
            return {"success": False, "error": "Delivery is not deleted"}, 400

        delivery.deleted_at = None
        delivery.is_active = True
        delivery.updated_at = datetime.utcnow()

        db.session.commit()

        return {
            "success": True,
            "data": delivery.to_dict(),
            "message": "Delivery restored successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

if __name__ == '__main__':
    create_tables()
    PORT = 5004  # aydin's Delivery Service
    print(f"🚚 Delivery Service starting on port {PORT}")
    print(f"📋 Available endpoints:")
    print(f"   POST   /api/deliveries               - Create new delivery")
    print(f"   GET    /api/deliveries               - Read all deliveries")
    print(f"   GET    /api/deliveries/<id>          - Read by ID with tracking")
    print(f"   POST   /api/deliveries/<id>/assign-courier - Assign courier")
    print(f"   POST   /api/deliveries/<id>/location - Update location")
    print(f"   GET    /api/tracking/<order_id>      - Track delivery by order")
    print(f"   GET    /api/couriers                 - Read all couriers")
    print(f"   POST   /api/couriers                 - Create courier")
    print(f"   DELETE /api/deliveries/<id>/soft-delete - Soft delete")
    print(f"   POST   /api/deliveries/<id>/restore  - Restore")
    app.run(host='127.0.0.1', port=PORT, debug=True)