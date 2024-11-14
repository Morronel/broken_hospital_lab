from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from routes.auth import login_required
from database.db import get_db, get_user_by_id, get_user_by_email
from datetime import datetime
from werkzeug.security import generate_password_hash

cabinet_bp = Blueprint('cabinet', __name__, url_prefix='/cabinet')

@cabinet_bp.route('/cabinet')
@login_required
def cabinet():
    user = get_user_by_id(session['user_id'])
    
    # Redirect to appropriate dashboard based on role
    if user['role'] == 'patient':
        return redirect(url_for('cabinet.patient_dashboard'))
    elif user['role'] == 'doctor':
        return redirect(url_for('cabinet.doctor_dashboard'))
    else:
        return redirect(url_for('admin.dashboard'))

@cabinet_bp.route('/patient-dashboard')
@login_required
def patient_dashboard():
    user = get_user_by_id(session['user_id'])
    if user['role'] != 'patient':
        return redirect(url_for('cabinet.cabinet'))
    
    db = get_db()
    appointments = db.execute('''
        SELECT a.*, d.specialization, u.name as doctor_name
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.user_id = ?
        ORDER BY a.date DESC, a.time DESC
        LIMIT 5
    ''', (user['id'],)).fetchall()
    
    return render_template('cabinet/patient_dashboard.html', user=user, appointments=appointments)

@cabinet_bp.route('/doctor-dashboard')
@login_required
def doctor_dashboard():
    user = get_user_by_id(session['user_id'])
    if user['role'] != 'doctor':
        return redirect(url_for('cabinet.cabinet'))
    
    db = get_db()
    doctor = db.execute('SELECT * FROM doctors WHERE user_id = ?', (user['id'],)).fetchone()
    appointments = db.execute('''
        SELECT a.*, u.name as patient_name, u.birth_date, u.sex 
        FROM appointments a 
        JOIN users u ON a.user_id = u.id 
        WHERE a.doctor_id = ? AND a.status = 'scheduled'
        ORDER BY date ASC, time ASC
    ''', (doctor['id'],)).fetchall()
    
    return render_template('cabinet/doctor_dashboard.html', 
                         user=user, 
                         doctor=doctor, 
                         appointments=appointments,
                         now=datetime.now)

@cabinet_bp.route('/schedule-appointment', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    user = get_user_by_id(session['user_id'])
    if user['role'] != 'patient':
        return redirect(url_for('cabinet.cabinet'))
    
    db = get_db()
    doctors = db.execute('''
        SELECT d.*, u.name as doctor_name 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id
    ''').fetchall()
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        time = request.form.get('time')
        complaint = request.form.get('complaint')
        
        db.execute('''
            INSERT INTO appointments (user_id, doctor_id, date, time, initial_complaint, status)
            VALUES (?, ?, ?, ?, ?, 'scheduled')
        ''', (user['id'], doctor_id, date, time, complaint))
        db.commit()
        
        flash('Appointment scheduled successfully!', 'success')
        return redirect(url_for('cabinet.patient_dashboard'))
    
    return render_template('cabinet/schedule_appointment.html', user=user, doctors=doctors)

@cabinet_bp.route('/appointment-history/<int:user_id>', methods=['GET'])
@login_required
def appointment_history(user_id=None):
    db = get_db()
    user = get_user_by_id(session['user_id'])
    
    target_user = get_user_by_id(user_id) if user_id else user
    
    if target_user['role'] == 'patient':
        appointments = db.execute('''
            SELECT a.*, d.specialization, u.name as doctor_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE a.user_id = ?
            ORDER BY a.date DESC, a.time DESC
        ''', (target_user['id'],)).fetchall()
    else:
        appointments = db.execute('''
            SELECT a.*, u.name as patient_name, u.birth_date, u.sex
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.doctor_id = (
                SELECT id FROM doctors WHERE user_id = ?
            )
            ORDER BY a.date DESC, a.time DESC
        ''', (target_user['id'],)).fetchall()

    return render_template('cabinet/patient_history.html', 
                         user=user, 
                         target_user=target_user,
                         appointments=appointments)

@cabinet_bp.route('/resolve-appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def resolve_appointment(appointment_id):
    user = get_user_by_id(session['user_id'])
    if user['role'] != 'doctor':
        return redirect(url_for('cabinet.cabinet'))
    
    db = get_db()
    appointment = db.execute('''
        SELECT a.*, u.name as patient_name, u.birth_date, u.sex 
        FROM appointments a 
        JOIN users u ON a.user_id = u.id 
        WHERE a.id = ?
    ''', (appointment_id,)).fetchone()
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        recommendations = request.form.get('recommendations')
        
        db.execute('''
            UPDATE appointments 
            SET diagnosis = ?, recommendations = ?, status = 'completed' 
            WHERE id = ?
        ''', (diagnosis, recommendations, appointment_id))
        db.commit()
        
        flash('Appointment resolved successfully!', 'success')
        return redirect(url_for('cabinet.doctor_dashboard'))
    
    return render_template('cabinet/resolve_appointment.html', user=user, appointment=appointment)

@cabinet_bp.route('/profile-settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    user = get_user_by_id(session['user_id'])
    db = get_db()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Check if email changed and if it's not already taken
        if email != user['email']:
            existing_user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if existing_user:
                flash('Email already exists', 'error')
                return redirect(url_for('cabinet.profile_settings'))
        
        db.execute('''
            UPDATE users 
            SET name = ?, email = ?, phone = ?, address = ?
            WHERE id = ?
        ''', (name, email, phone, address, user['id']))
        db.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('cabinet.profile_settings'))
    
    return render_template('cabinet/profile_settings.html', user=user)

@cabinet_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    db = get_db()
    data = request.get_json()
    
    # Vulnerable part - allows specifying target email
    target_email = data.get('target_email') or get_user_by_id(session['user_id'])['email']
    
    # Get user by email - this is the vulnerable part as it allows modifying any user
    target_user = get_user_by_email(target_email)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    updates = []
    params = []
    
    if 'name' in data and data['name']:
        updates.append('name = ?')
        params.append(data['name'])
    
    if 'email' in data and data['email']:
        # Check if new email is available
        if data['email'] != target_email:
            existing = get_user_by_email(data['email'])
            if existing:
                return jsonify({'error': 'Email already taken'}), 400
        updates.append('email = ?')
        params.append(data['email'])

    if 'password' in data and data['password']:
        updates.append('password_hash = ?')
        params.append(generate_password_hash(data['password']))

    if 'phone' in data and data['phone']:
        updates.append('phone = ?')
        params.append(data['phone'])

    if 'address' in data and data['address']:
        updates.append('address = ?')
        params.append(data['address'])

    if updates:
        params.append(target_email)
        query = f'UPDATE users SET {", ".join(updates)} WHERE email = ?'
        db.execute(query, params)
        db.commit()

    return jsonify({'message': 'Profile updated successfully'})