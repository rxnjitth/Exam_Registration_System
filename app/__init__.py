import os

from flask import Flask, render_template

from app.extensions import csrf, db, login_manager
from app.models import User
from app.routes import admin as admin_routes
from app.routes import auth as auth_routes
from app.routes import main as main_routes
from app.routes import student as student_routes
from app.seed import seed_defaults


def create_app(config_object="config.Config"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(student_routes.bp)
    app.register_blueprint(admin_routes.bp)

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("errors/500.html"), 500

    with app.app_context():
        db.create_all()
        if not app.config.get("TESTING"):
            seed_defaults()

    return app
