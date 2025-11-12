from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

def create_tables():
    with app.app_context():
        db.create_all()
        print(" Database tables created")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "example-service",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/examples', methods=['GET'])
def get_all():
    resources = ExampleModel.query.all()
    return jsonify({
        "success": True,
        "data": [r.to_dict() for r in resources],
        "count": len(resources)
    })

@app.route('/api/examples', methods=['POST'])
def create():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"success": False, "error": "Name is required"}), 400
    
    new_resource = ExampleModel(
        name=data.get('name'),
        description=data.get('description', '')
    )
    db.session.add(new_resource)
    db.session.commit()
    return jsonify({"success": True, "data": new_resource.to_dict()}), 201

@app.route('/api/examples/<int:id>', methods=['GET'])
def get_one(id):
    resource = ExampleModel.query.get(id)
    if not resource:
        return jsonify({"success": False, "error": "Not found"}), 404
    return jsonify({"success": True, "data": resource.to_dict()})

if __name__ == '__main__':
    create_tables()
    #  UBAH PORT INI SESUAI SERVICE ANDA:
    PORT = 5000  # ARTHUR:5001, rizki:5002, Nadia:5003, aydin:5004, reza:5005
    print(f" Service starting on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)