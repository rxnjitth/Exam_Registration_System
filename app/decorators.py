from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied.", "danger")
            return redirect(url_for("student.dashboard"))
        return f(*args, **kwargs)

    return decorated
