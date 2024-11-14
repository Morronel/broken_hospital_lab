from flask import Blueprint, render_template, request, jsonify, session
from database.db import create_user, get_user_by_email, init_db
from utils.email_service import EmailService
from werkzeug.security import generate_password_hash
import uuid

signup_bp = Blueprint('signup', __name__)
email_service = EmailService()

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Create user data dictionary
        new_user = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'name': name,
            'role': 'patient'
        }
        
        if not create_user(new_user):
            return jsonify({
                "error": "Failed to create user"
            }), 500
            
        return jsonify({
            "message": "Registration successful!",
            "email_sent": False
        }), 201
        
    except Exception as e:
        print(f"Unexpected error during registration: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred during registration"
        }), 500

# Separate route for email confirmation
@signup_bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        user = db.get_user_by_confirmation_token(token)
        if not user:
            return render_template('error.html', 
                message="Invalid or expired confirmation link"), 400
        
        db.confirm_user_email(user.id)
        return render_template('confirmation_success.html')
    except Exception as e:
        print(f"Error during email confirmation: {str(e)}")
        return render_template('error.html', 
            message="An error occurred during confirmation"), 500