from flask import Blueprint, session, redirect, url_for, flash
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator untuk memastikan user sudah login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_role(allowed_roles):
    """Decorator untuk membatasi akses berdasarkan role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('login'))
            
            if session['role'] not in allowed_roles:
                flash('Anda tidak memiliki akses ke halaman ini.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
