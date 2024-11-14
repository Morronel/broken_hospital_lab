from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from routes.auth import login_required
from database.db import get_db, get_user_by_id
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        user = get_user_by_id(session['user_id'])
        if user['role'] != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('cabinet.cabinet'))
        return view(**kwargs)
    return wrapped_view

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    db = get_db()
    user = get_user_by_id(session['user_id'])
    
    # Get statistics
    stats = {
        'total_users': db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count'],
        'total_doctors': db.execute('SELECT COUNT(*) as count FROM doctors').fetchone()['count'],
        'total_appointments': db.execute('SELECT COUNT(*) as count FROM appointments').fetchone()['count']
    }
    
    # Get recent activity (last 10 events)
    recent_activity = db.execute('''
        SELECT * FROM (
            SELECT 'New User' as action, 
                   'User ' || name || ' registered' as description,
                   created_at as timestamp
            FROM users
            UNION ALL
            SELECT 'New Appointment' as action,
                   'Appointment scheduled for ' || date || ' ' || time as description,
                   created_at as timestamp
            FROM appointments
        ) as activity
        ORDER BY timestamp DESC
        LIMIT 10
    ''').fetchall()
    
    return render_template('admin/admin.html', 
                         user=user, 
                         stats=stats, 
                         recent_activity=recent_activity)

@admin_bp.route('/get-users', methods=['GET'])
def get_users():
    """Vulnerable API endpoint - no authentication required"""
    db = get_db()
    users = db.execute('''
        SELECT u.id, u.email, u.name, u.role, u.phone, u.address, u.birth_date,
               d.specialization 
        FROM users u
        LEFT JOIN doctors d ON u.id = d.user_id
        ORDER BY u.id
    ''').fetchall()
    
    return jsonify([{
        'id': user['id'],
        'email': user['email'],
        'name': user['name'],
        'role': user['role'],
        'phone': user['phone'],
        'address': user['address'],
        'birth_date': user['birth_date'],
        'specialization': user['specialization'] if user['role'] == 'doctor' else None
    } for user in users])

@admin_bp.route('/manage-users')
@login_required
@admin_required
def manage_users():
    user = get_user_by_id(session['user_id'])
    return render_template('admin/manage_users.html', user=user)

@admin_bp.route('/manage-appointments')
@login_required
@admin_required
def manage_appointments():
    db = get_db()
    user = get_user_by_id(session['user_id'])
    
    appointments = db.execute('''
        SELECT a.*, 
               p.name as patient_name,
               d.name as doctor_name,
               doc.specialization,
               a.diagnosis,
               a.recommendations
        FROM appointments a
        JOIN users p ON a.user_id = p.id
        JOIN doctors doc ON a.doctor_id = doc.id
        JOIN users d ON doc.user_id = d.id
        ORDER BY a.date DESC, a.time DESC
    ''').fetchall()
    
    # Convert appointments to list of dictionaries
    appointments_list = []
    for appointment in appointments:
        appointment_dict = dict(appointment)
        appointments_list.append(appointment_dict)
    
    return render_template('admin/manage_appointments.html', 
                         user=user, 
                         appointments=appointments_list)

# Add CRUD operations for users
@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """
    Vulnerable endpoint - any authenticated user can delete any user
    Just needs to know the user_id to delete
    """
    db = get_db()
    
    # No authorization check here - IDOR vulnerability
    
    # First delete from doctors table if they're a doctor
    db.execute('DELETE FROM doctors WHERE user_id = ?', (user_id,))
    
    # Then delete from users table
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    
    return jsonify({'message': 'User deleted successfully'})

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required  # Only requires authentication, not admin rights
def edit_user(user_id):
    current_user = get_user_by_id(session['user_id'])
    
    # Allow access only for admins and doctors
    if current_user['role'] not in ['admin', 'doctor']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        specialization = request.form.get('specialization')
        
        db = get_db()
        
        # If user is doctor (not admin), restrict some operations
        if current_user['role'] == 'doctor':
            # Doctors can't change roles or their own data
            if user_id == current_user['id']:
                return jsonify({'error': 'Cannot modify own account'}), 403
            
            # Doctors can only edit patient data, not other doctors or admins
            target_user = get_user_by_id(user_id)
            if target_user['role'] != 'patient':
                return jsonify({'error': 'Can only modify patient data'}), 403
            
            # Doctors can't change user roles
            role = target_user['role']
        
        db.execute('UPDATE users SET name = ?, email = ?, role = ? WHERE id = ?',
                  (name, email, role, user_id))
        
        if role == 'doctor':
            doctor = db.execute('SELECT * FROM doctors WHERE user_id = ?', 
                              (user_id,)).fetchone()
            if doctor:
                db.execute('UPDATE doctors SET specialization = ? WHERE user_id = ?',
                          (specialization, user_id))
            else:
                db.execute('INSERT INTO doctors (user_id, specialization) VALUES (?, ?)',
                          (user_id, specialization))
        
        db.commit()
        
        if request.is_json:
            return jsonify({'message': 'User updated successfully'})
        
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    db = get_db()
    user_to_edit = db.execute('''
        SELECT u.*, d.specialization 
        FROM users u 
        LEFT JOIN doctors d ON u.id = d.user_id 
        WHERE u.id = ?
    ''', (user_id,)).fetchone()
    
    if request.is_json:
        return jsonify({
            'id': user_to_edit['id'],
            'name': user_to_edit['name'],
            'email': user_to_edit['email'],
            'role': user_to_edit['role'],
            'specialization': user_to_edit['specialization']
        })
    
    return render_template('admin/edit_user.html', 
                         user=current_user,
                         user_to_edit=user_to_edit)

# Add CRUD operations for appointments
@admin_bp.route('/appointment/<int:appointment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_appointment(appointment_id):
    db = get_db()
    db.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
    db.commit()
    flash('Appointment deleted successfully', 'success')
    return redirect(url_for('admin.manage_appointments'))

@admin_bp.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_appointment(appointment_id):
    db = get_db()
    db.execute('UPDATE appointments SET status = "cancelled" WHERE id = ?', (appointment_id,))
    db.commit()
    flash('Appointment cancelled successfully', 'success')
    return redirect(url_for('admin.manage_appointments'))

# Add more routes for CRUD operations... 