from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========================
#  GANTI MODEL INI SESUAI SERVICE ANDA
# ========================
class ExampleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)  # For soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

def create_tables():
    with app.app_context():
        db.create_all()
        print(" Database tables created")

# ========================
# ENHANCED CRUD OPERATIONS
# ========================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Example Service Template",
        "version": "1.0.0",
        "description": "Microservice template untuk Food Delivery System",
        "endpoints": {
            "health": "/health",
            "api": "/api/examples",
            "create": "POST /api/examples",
            "read_all": "GET /api/examples",
            "read_one": "GET /api/examples/<id>",
            "update": "PUT /api/examples/<id>",
            "patch": "PATCH /api/examples/<id>",
            "soft_delete": "DELETE /api/examples/<id>/soft-delete",
            "hard_delete": "DELETE /api/examples/<id>",
            "restore": "POST /api/examples/<id>/restore",
            "bulk_delete": "DELETE /api/examples/bulk-delete",
            "bulk_restore": "POST /api/examples/bulk-restore"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "example-service",
        "timestamp": datetime.utcnow().isoformat()
    })

# ========== READ OPERATIONS ==========
@app.route('/api/examples', methods=['GET'])
def get_all():
    """READ ALL - Get all resources (including soft deleted if include_deleted=true)"""
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        if include_deleted:
            # Include soft deleted records
            resources = ExampleModel.query.all()
        else:
            # Only active records
            resources = ExampleModel.query.filter_by(deleted_at=None).all()
            
        return jsonify({
            "success": True,
            "data": [r.to_dict() for r in resources],
            "count": len(resources),
            "include_deleted": include_deleted
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/examples/<int:id>', methods=['GET'])
def get_one(id):
    """READ BY ID - Get single resource"""
    try:
        resource = ExampleModel.query.get(id)
        if not resource:
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        # Check if soft deleted
        if resource.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true':
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        return jsonify({
            "success": True,
            "data": resource.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ========== CREATE OPERATIONS ==========
@app.route('/api/examples', methods=['POST'])
def create():
    """CREATE - Create new resource"""
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"success": False, "error": "Name is required"}), 400
        
        new_resource = ExampleModel(
            name=data.get('name'),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_resource)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": new_resource.to_dict(),
            "message": "Resource created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== UPDATE OPERATIONS ==========
@app.route('/api/examples/<int:id>', methods=['PUT'])
def update(id):
    """UPDATE - Full update of resource"""
    try:
        resource = ExampleModel.query.get(id)
        if not resource:
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        if resource.deleted_at:
            return jsonify({"success": False, "error": "Cannot update deleted resource"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Update fields
        if 'name' in data:
            resource.name = data['name']
        if 'description' in data:
            resource.description = data['description']
        if 'is_active' in data:
            resource.is_active = data['is_active']
            
        resource.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": resource.to_dict(),
            "message": "Resource updated successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/examples/<int:id>', methods=['PATCH'])
def partial_update(id):
    """PARTIAL UPDATE - Update specific fields"""
    try:
        resource = ExampleModel.query.get(id)
        if not resource:
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        if resource.deleted_at:
            return jsonify({"success": False, "error": "Cannot update deleted resource"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Update only provided fields
        for field, value in data.items():
            if hasattr(resource, field) and field != 'id':
                setattr(resource, field, value)
                
        resource.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "data": resource.to_dict(),
            "message": "Resource updated successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== DELETE OPERATIONS ==========
@app.route('/api/examples/<int:id>/soft-delete', methods=['DELETE'])
def soft_delete(id):
    """SOFT DELETE - Mark as deleted without removing from database"""
    try:
        resource = ExampleModel.query.get(id)
        if not resource:
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        if resource.deleted_at:
            return jsonify({"success": False, "error": "Resource already deleted"}), 400
            
        resource.deleted_at = datetime.utcnow()
        resource.is_active = False
        resource.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": resource.to_dict(),
            "message": "Resource soft deleted successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/examples/<int:id>', methods=['DELETE'])
def hard_delete(id):
    """HARD DELETE - Permanently remove from database"""
    try:
        resource = ExampleModel.query.get(id)
        if not resource:
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        db.session.delete(resource)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Resource permanently deleted"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/examples/<int:id>/restore', methods=['POST'])
def restore(id):
    """RESTORE - Restore soft deleted resource"""
    try:
        resource = ExampleModel.query.get(id)
        if not resource:
            return jsonify({"success": False, "error": "Resource not found"}), 404
            
        if not resource.deleted_at:
            return jsonify({"success": False, "error": "Resource is not deleted"}), 400
            
        resource.deleted_at = None
        resource.is_active = True
        resource.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": resource.to_dict(),
            "message": "Resource restored successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== BULK OPERATIONS ==========
@app.route('/api/examples/bulk-delete', methods=['DELETE'])
def bulk_soft_delete():
    """BULK SOFT DELETE - Delete multiple resources"""
    try:
        data = request.get_json()
        if not data or not data.get('ids'):
            return jsonify({"success": False, "error": "IDs array is required"}), 400
            
        ids = data['ids']
        resources = ExampleModel.query.filter(ExampleModel.id.in_(ids)).all()
        
        deleted_count = 0
        for resource in resources:
            if not resource.deleted_at:
                resource.deleted_at = datetime.utcnow()
                resource.is_active = False
                resource.updated_at = datetime.utcnow()
                deleted_count += 1
                
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{deleted_count} resources soft deleted successfully",
            "deleted_count": deleted_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/examples/bulk-restore', methods=['POST'])
def bulk_restore():
    """BULK RESTORE - Restore multiple soft deleted resources"""
    try:
        data = request.get_json()
        if not data or not data.get('ids'):
            return jsonify({"success": False, "error": "IDs array is required"}), 400
            
        ids = data['ids']
        resources = ExampleModel.query.filter(ExampleModel.id.in_(ids)).all()
        
        restored_count = 0
        for resource in resources:
            if resource.deleted_at:
                resource.deleted_at = None
                resource.is_active = True
                resource.updated_at = datetime.utcnow()
                restored_count += 1
                
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{restored_count} resources restored successfully",
            "restored_count": restored_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    create_tables()
    #  UBAH PORT INI SESUAI SERVICE ANDA:
    PORT = 5001  # ARTHUR:5001, rizki:5002, Nadia:5003, aydin:5004, reza:5005
    print(f" Service starting on port {PORT}")
    print(f" Available endpoints:")
    print(f"   GET    /api/examples              - Read all")
    print(f"   GET    /api/examples/<id>         - Read by ID")
    print(f"   POST   /api/examples              - Create")
    print(f"   PUT    /api/examples/<id>         - Full update")
    print(f"   PATCH  /api/examples/<id>         - Partial update")
    print(f"   DELETE /api/examples/<id>/soft-delete - Soft delete")
    print(f"   DELETE /api/examples/<id>         - Hard delete")
    print(f"   POST   /api/examples/<id>/restore - Restore")
    print(f"   DELETE /api/examples/bulk-delete  - Bulk soft delete")
    print(f"   POST   /api/examples/bulk-restore - Bulk restore")
    app.run(host='0.0.0.0', port=PORT, debug=True)