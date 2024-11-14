from flask import Blueprint, jsonify
from database.db import Database

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
db = Database()

@admin_bp.route('/', methods=['GET'])
def admin_home():
    return "Admin panel home"  # For testing

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    users = db.get_all_users()
    return jsonify([{
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.name
    } for user in users])

@admin_bp.route('/medical_records', methods=['GET'])
def get_all_records():
    # Intentionally vulnerable - no authentication check
    users = db.get_all_users()
    all_records = []
    for user in users:
        if user.role == 'patient':
            records = db.get_patient_records(user.id)
            all_records.extend(records)
    
    return jsonify([{
        "id": record.id,
        "patient_id": record.patient_id,
        "type": record.record_type,
        "details": record.details,
        "created_at": record.created_at.isoformat()
    } for record in all_records]) 