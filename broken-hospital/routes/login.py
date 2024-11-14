from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db import get_user_by_email, get_db
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')

        error = None
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            
            if request.is_json:
                response = {'success': True}
                if user['role'] == 'admin':
                    response['redirect'] = url_for('admin.dashboard')
                elif user['role'] == 'doctor':
                    response['redirect'] = url_for('cabinet.doctor_dashboard')
                else:
                    response['redirect'] = url_for('cabinet.patient_dashboard')
                return jsonify(response)
            else:
                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user['role'] == 'doctor':
                    return redirect(url_for('cabinet.doctor_dashboard'))
                else:
                    return redirect(url_for('cabinet.patient_dashboard'))

        if request.is_json:
            return jsonify({'error': error}), 401
        flash(error)

    return render_template('login/login.html')