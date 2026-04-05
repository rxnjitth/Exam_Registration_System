from app.extensions import db
from app.models import Exam, User
from app.seed import seed_defaults


def test_seed_creates_admin_and_exams(app):
    with app.app_context():
        seed_defaults()
        admin = User.query.filter_by(username="admin").first()
        assert admin is not None
        assert admin.is_admin is True
        assert Exam.query.count() >= 4
