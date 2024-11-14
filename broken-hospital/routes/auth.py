from functools import wraps
from flask import Blueprint, session, redirect, url_for
from database.db import get_user_by_id

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login.login'))
            
            user = get_user_by_id(session['user_id'])
            if not user or user['role'] != role:
                return redirect(url_for('home.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

# Instead of a separate admin_required, use role_required('admin')