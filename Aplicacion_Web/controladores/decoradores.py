from functools import wraps
from flask import session, redirect, url_for, flash

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorada
