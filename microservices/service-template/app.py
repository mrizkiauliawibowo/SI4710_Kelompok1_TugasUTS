from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# ❗ GANTI MODEL INI SESUAI SERVICE ANDA
class ExampleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Tambahkan field sesuai kebutuhan service Anda

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"success": True, "status": "healthy"})

@app.route('/examples', methods=['GET'])
def get_all():
    # Implementasi GET all
    return jsonify({"success": True, "data": []})

@app.route('/examples', methods=['POST'])
def create():
    # Implementasi CREATE
    return jsonify({"success": True, "data": {}}), 201

if __name__ == '__main__':
    # ❗ UBAH PORT SESUAI ASSIGNMENT
    PORT = 5000  # ARTHUR:5001, rizki:5002, Nadia:5003, aydin:5004, reza:5005
    app.run(host='0.0.0.0', port=PORT, debug=True)