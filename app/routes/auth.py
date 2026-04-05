from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, UserRegisterForm
from app.models import User
from app.utils.passwords import hash_password, verify_password

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            password_hash=hash_password(form.password.data),
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created. You can log in now.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and verify_password(form.password.data, user.password_hash):
            login_user(user, remember=False)
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("student.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
