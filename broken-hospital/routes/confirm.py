from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db

confirm_bp = Blueprint('confirm', __name__)

@confirm_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        with get_db() as db:
            # Find user with this confirmation token
            user = db.execute(
                'SELECT id FROM users WHERE confirmation_token = ?',
                (token,)
            ).fetchone()
            
            if user:
                # Update user's confirmation status
                db.execute(
                    'UPDATE users SET is_confirmed = 1, confirmation_token = NULL WHERE id = ?',
                    (user['id'],)
                )
                db.commit()
                flash('Email confirmed successfully! You can now log in.', 'success')
                return redirect(url_for('login.login'))
            else:
                flash('Invalid or expired confirmation token.', 'error')
                return redirect(url_for('home'))
                
    except sqlite3.Error as e:
        print(f"Database error during confirmation: {e}")
        flash('An error occurred during confirmation.', 'error')
        return redirect(url_for('home')) 