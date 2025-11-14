from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import random
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========================
#  PAYMENT SERVICE MODELS
# ========================
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # credit_card, debit_card, e_wallet, bank_transfer
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='IDR')
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed, cancelled, refunded
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)  # For card payments
    gateway_response = db.Column(db.Text, nullable=True)  # JSON string for payment gateway response
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # For soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'transaction_id': self.transaction_id,
            'payment_method': self.payment_method,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'gateway_response': self.gateway_response,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    card_number_hash = db.Column(db.String(128), nullable=True)  # Hashed card number for security
    card_holder_name = db.Column(db.String(100), nullable=True)
    expiry_month = db.Column(db.Integer, nullable=True)
    expiry_year = db.Column(db.Integer, nullable=True)
    cvv_hash = db.Column(db.String(128), nullable=True)  # Hashed CVV
    provider = db.Column(db.String(50), nullable=True)  # visa, mastercard, bca, mandiri, etc.
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'card_number_masked': self._mask_card_number(),
            'card_holder_name': self.card_holder_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
            'provider': self.provider,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_deleted': self.deleted_at is not None
        }
    
    def _mask_card_number(self):
        """Return masked card number for security"""
        if not self.card_number_hash:
            return None
        # In real implementation, store and retrieve masked version
        return "****-****-****-****"

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # created, updated, completed, failed, refunded
    status_before = db.Column(db.String(20), nullable=True)
    status_after = db.Column(db.String(20), nullable=False)
    amount_before = db.Column(db.Float, nullable=True)
    amount_after = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    gateway_data = db.Column(db.Text, nullable=True)  # JSON string
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'action': self.action,
            'status_before': self.status_before,
            'status_after': self.status_after,
            'amount_before': self.amount_before,
            'amount_after': self.amount_after,
            'notes': self.notes,
            'gateway_data': self.gateway_data,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }

class Refund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    processed_date = db.Column(db.DateTime, nullable=True)
    refund_transaction_id = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'refund_amount': self.refund_amount,
            'reason': self.reason,
            'status': self.status,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None,
            'refund_transaction_id': self.refund_transaction_id,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def create_tables():
    with app.app_context():
        db.create_all()
        print("✅ Payment Service tables created")

def generate_transaction_id():
    """Generate unique transaction ID"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_part = str(random.randint(100000, 999999))
    return f"TXN{timestamp}{random_part}"

def hash_sensitive_data(data):
    """Simple hashing for sensitive data - in production use proper encryption"""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()

def simulate_payment_gateway(amount, method, card_number=None):
    """Simulate payment gateway response"""
    # Simulate processing time
    import time
    time.sleep(1)
    
    # Simulate success/failure based on amount and method
    if amount <= 0:
        return {
            "status": "failed",
            "error": "Invalid amount",
            "gateway_transaction_id": None
        }
    
    if method in ["credit_card", "debit_card"] and not card_number:
        return {
            "status": "failed",
            "error": "Card number required",
            "gateway_transaction_id": None
        }
    
    # 90% success rate for demo
    if random.random() < 0.9:
        return {
            "status": "completed",
            "gateway_transaction_id": f"GW{uuid.uuid4().hex[:16].upper()}",
            "approval_code": f"APP{random.randint(100000, 999999)}",
            "response_code": "00"
        }
    else:
        return {
            "status": "failed",
            "error": "Payment declined by bank",
            "gateway_transaction_id": None
        }

# ========================
# ENHANCED CRUD OPERATIONS
# ========================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Payment Service",
        "version": "1.0.0",
        "description": "Microservice untuk Manajemen Payment dan Transaksi",
        "endpoints": {
            "health": "/health",
            "api": "/api/payments",
            "methods": "/api/payment-methods",
            "history": "/api/payment-history",
            "refunds": "/api/refunds",
            "create": "POST /api/payments",
            "read_all": "GET /api/payments",
            "read_one": "GET /api/payments/<id>",
            "process": "POST /api/payments/<id>/process",
            "refund": "POST /api/payments/<id>/refund",
            "soft_delete": "DELETE /api/payments/<id>/soft-delete",
            "hard_delete": "DELETE /api/payments/<id>",
            "restore": "POST /api/payments/<id>/restore",
            "bulk_delete": "DELETE /api/payments/bulk-delete",
            "bulk_restore": "POST /api/payments/bulk-restore"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "payment-service",
        "timestamp": datetime.utcnow().isoformat()
    })

# ========== PAYMENT ENDPOINTS ==========
@app.route('/api/payments', methods=['GET'])
def get_all_payments():
    """READ ALL - Get all payments"""
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        status_filter = request.args.get('status')
        user_filter = request.args.get('user_id')
        order_filter = request.args.get('order_id')

        query = Payment.query
        if not include_deleted:
            query = query.filter_by(deleted_at=None)
        if status_filter:
            query = query.filter_by(status=status_filter)
        if user_filter:
            query = query.filter_by(user_id=user_filter)
        if order_filter:
            query = query.filter_by(order_id=order_filter)

        payments = query.order_by(Payment.created_at.desc()).all()

        return {
            "success": True,
            "data": [p.to_dict() for p in payments],
            "count": len(payments),
            "filters": {
                "include_deleted": include_deleted,
                "status": status_filter,
                "user_id": user_filter,
                "order_id": order_filter
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/payments/<int:id>', methods=['GET'])
def get_payment(id):
    """READ BY ID - Get single payment"""
    try:
        payment = Payment.query.get(id)
        if not payment:
            return {"success": False, "error": "Payment not found"}, 404

        if payment.deleted_at and not request.args.get('include_deleted', 'false').lower() == 'true':
            return {"success": False, "error": "Payment not found"}, 404

        # Get payment history
        history = PaymentHistory.query.filter_by(payment_id=id).order_by(PaymentHistory.created_at.desc()).all()

        return {
            "success": True,
            "data": {
                "payment": payment.to_dict(),
                "history": [h.to_dict() for h in history]
            }
        }, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/api/payments', methods=['POST'])
def create_payment():
    """CREATE - Create new payment"""
    try:
        data = request.get_json()
        
        required_fields = ['order_id', 'user_id', 'amount', 'payment_method']
        for field in required_fields:
            if not data or not data.get(field):
                return {"success": False, "error": f"{field} is required"}, 400

        order_id = data.get('order_id')
        user_id = data.get('user_id')
        amount = data.get('amount')
        payment_method = data.get('payment_method')

        # Check if payment already exists for this order
        existing_payment = Payment.query.filter_by(order_id=order_id, status='completed').first()
        if existing_payment:
            return {"success": False, "error": "Payment already completed for this order"}, 400

        # Generate transaction ID
        transaction_id = generate_transaction_id()

        # Create payment record
        new_payment = Payment(
            order_id=order_id,
            user_id=user_id,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            currency=data.get('currency', 'IDR'),
            status='pending',
            notes=data.get('notes', '')
        )

        # Set expiry date for card payments
        if payment_method in ['credit_card', 'debit_card'] and data.get('expiry_date'):
            new_payment.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))

        db.session.add(new_payment)
        db.session.flush()  # Get payment ID

        # Create history entry
        history_entry = PaymentHistory(
            payment_id=new_payment.id,
            action='created',
            status_before=None,
            status_after='pending',
            amount_before=None,
            amount_after=amount,
            notes=f'Payment created for order {order_id}',
            created_by=user_id
        )
        db.session.add(history_entry)

        db.session.commit()

        return {
            "success": True,
            "data": new_payment.to_dict(),
            "message": "Payment created successfully"
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/payments/<int:id>/process', methods=['POST'])
def process_payment(id):
    """PROCESS - Process payment through gateway"""
    try:
        payment = Payment.query.get(id)
        if not payment:
            return jsonify({"success": False, "error": "Payment not found"}), 404
            
        if payment.deleted_at:
            return jsonify({"success": False, "error": "Cannot process deleted payment"}), 400
            
        if payment.status not in ['pending', 'failed']:
            return jsonify({"success": False, "error": f"Cannot process payment with status: {payment.status}"}), 400
        
        data = request.get_json() or {}
        card_number = data.get('card_number')

        # Store previous status and amount
        old_status = payment.status
        old_amount = payment.amount

        # Simulate payment gateway processing
        gateway_response = simulate_payment_gateway(
            payment.amount,
            payment.payment_method,
            card_number
        )

        payment.gateway_response = str(gateway_response)

        if gateway_response["status"] == "completed":
            payment.status = "completed"
            payment.payment_date = datetime.utcnow()
        else:
            payment.status = "failed"

        payment.updated_at = datetime.utcnow()

        # Create history entry
        history_entry = PaymentHistory(
            payment_id=payment.id,
            action='processed',
            status_before=old_status,
            status_after=payment.status,
            amount_before=old_amount,
            amount_after=payment.amount,
            notes=gateway_response.get("error", "Payment processed"),
            gateway_data=str(gateway_response),
            created_by=payment.user_id
        )
        db.session.add(history_entry)

        db.session.commit()

        return {
            "success": True,
            "data": payment.to_dict(),
            "gateway_response": gateway_response,
            "message": f"Payment {gateway_response['status']}"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/payments/<int:id>/refund', methods=['POST'])
def create_refund(id):
    """CREATE REFUND - Create refund for payment"""
    try:
        payment = Payment.query.get(id)
        if not payment:
            return jsonify({"success": False, "error": "Payment not found"}), 404
            
        if payment.status != 'completed':
            return jsonify({"success": False, "error": "Only completed payments can be refunded"}), 400
        
        data = request.get_json()
        if not data or not data.get('refund_amount') or not data.get('reason'):
            return {"success": False, "error": "refund_amount and reason are required"}, 400

        refund_amount = data.get('refund_amount')
        reason = data.get('reason')

        if refund_amount > payment.amount:
            return {"success": False, "error": "Refund amount cannot exceed payment amount"}, 400

        # Create refund record
        refund = Refund(
            payment_id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            refund_amount=refund_amount,
            reason=reason,
            notes=data.get('notes', '')
        )

        # Simulate refund processing
        import time
        time.sleep(0.5)

        if random.random() < 0.95:  # 95% success rate for refunds
            refund.status = 'completed'
            refund.processed_date = datetime.utcnow()
            refund.refund_transaction_id = f"RFD{uuid.uuid4().hex[:16].upper()}"

            # Update payment status if fully refunded
            if refund_amount >= payment.amount:
                payment.status = 'refunded'
        else:
            refund.status = 'failed'

        db.session.add(refund)

        # Create payment history
        history_entry = PaymentHistory(
            payment_id=payment.id,
            action='refunded',
            status_before=payment.status,
            status_after=payment.status,
            amount_before=payment.amount,
            amount_after=payment.amount - refund_amount,
            notes=f'Refund of {refund_amount} created: {reason}',
            created_by=payment.user_id
        )
        db.session.add(history_entry)

        db.session.commit()

        return {
            "success": True,
            "data": {
                "payment": payment.to_dict(),
                "refund": refund.to_dict()
            },
            "message": f"Refund {refund.status}"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

# ========== PAYMENT METHOD ENDPOINTS ==========
@app.route('/api/payment-methods', methods=['GET'])
def get_payment_methods():
    """READ ALL - Get all payment methods for user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "user_id parameter is required"}), 400
        
        methods = PaymentMethod.query.filter_by(user_id=user_id, deleted_at=None).all()
        
        return jsonify({
            "success": True,
            "data": [m.to_dict() for m in methods],
            "count": len(methods)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/payment-methods', methods=['POST'])
def create_payment_method():
    """CREATE - Create new payment method"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'name']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        user_id = data.get('user_id')
        
        # If this is set as default, unset other defaults
        if data.get('is_default', False):
            PaymentMethod.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        
        new_method = PaymentMethod(
            user_id=user_id,
            name=data.get('name'),
            card_holder_name=data.get('card_holder_name'),
            expiry_month=data.get('expiry_month'),
            expiry_year=data.get('expiry_year'),
            provider=data.get('provider'),
            is_default=data.get('is_default', False)
        )
        
        # Hash sensitive data
        if data.get('card_number'):
            new_method.card_number_hash = hash_sensitive_data(data['card_number'])
        if data.get('cvv'):
            new_method.cvv_hash = hash_sensitive_data(data['cvv'])
        
        db.session.add(new_method)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": new_method.to_dict(),
            "message": "Payment method created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ========== DELETE OPERATIONS ==========
@app.route('/api/payments/<int:id>/soft-delete', methods=['DELETE'])
def soft_delete_payment(id):
    """SOFT DELETE - Mark payment as deleted"""
    try:
        payment = Payment.query.get(id)
        if not payment:
            return {"success": False, "error": "Payment not found"}, 404

        if payment.deleted_at:
            return {"success": False, "error": "Payment already deleted"}, 400

        payment.deleted_at = datetime.utcnow()
        payment.is_active = False
        payment.updated_at = datetime.utcnow()

        # Create history entry
        history_entry = PaymentHistory(
            payment_id=payment.id,
            action='deleted',
            status_before=payment.status,
            status_after=payment.status,
            amount_before=payment.amount,
            amount_after=payment.amount,
            notes='Payment soft deleted',
            created_by=payment.user_id
        )
        db.session.add(history_entry)

        db.session.commit()

        return {
            "success": True,
            "data": payment.to_dict(),
            "message": "Payment soft deleted successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

@app.route('/api/payments/<int:id>/restore', methods=['POST'])
def restore_payment(id):
    """RESTORE - Restore soft deleted payment"""
    try:
        payment = Payment.query.get(id)
        if not payment:
            return {"success": False, "error": "Payment not found"}, 404

        if not payment.deleted_at:
            return {"success": False, "error": "Payment is not deleted"}, 400

        payment.deleted_at = None
        payment.is_active = True
        payment.updated_at = datetime.utcnow()

        # Create history entry
        history_entry = PaymentHistory(
            payment_id=payment.id,
            action='restored',
            status_before=payment.status,
            status_after=payment.status,
            amount_before=payment.amount,
            amount_after=payment.amount,
            notes='Payment restored',
            created_by=payment.user_id
        )
        db.session.add(history_entry)

        db.session.commit()

        return {
            "success": True,
            "data": payment.to_dict(),
            "message": "Payment restored successfully"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}, 500

if __name__ == '__main__':
    create_tables()
    PORT = 5005  # Reza's Payment Service
    print(f"💳 Payment Service starting on port {PORT}")
    print(f"📋 Available endpoints:")
    print(f"   POST   /api/payments               - Create new payment")
    print(f"   GET    /api/payments               - Read all payments")
    print(f"   GET    /api/payments/<id>          - Read by ID with history")
    print(f"   POST   /api/payments/<id>/process  - Process payment")
    print(f"   POST   /api/payments/<id>/refund   - Create refund")
    print(f"   GET    /api/payment-methods        - Read user payment methods")
    print(f"   POST   /api/payment-methods        - Create payment method")
    print(f"   DELETE /api/payments/<id>/soft-delete - Soft delete")
    print(f"   POST   /api/payments/<id>/restore  - Restore")
    print(f"   GET    /api/refunds                - Read all refunds")
    app.run(host='127.0.0.1', port=PORT, debug=True)