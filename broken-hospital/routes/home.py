from flask import Blueprint, render_template, session
from database.db import get_user_by_id

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return render_template('home/index.html', user=user)

# Make sure this blueprint is registered in __init__.py