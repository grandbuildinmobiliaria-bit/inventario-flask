from functools import wraps
from flask import session, flash, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            flash("⚠️ Debes iniciar sesión primero", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("rol") not in roles:
                flash("⛔ No tienes permiso para acceder aquí", "error")
                return redirect(url_for("home"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
