from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import get_user_by_id

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login.login'))
    
    # Get user data
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login.login'))
    
    return render_template('profile.html', user=user) 