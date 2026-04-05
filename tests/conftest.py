import pytest

from app import create_app
from app.extensions import db
from app.models import Exam, User
from app.utils.passwords import hash_password


@pytest.fixture
def app():
    app = create_app("config.TestConfig")
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student_user(app):
    with app.app_context():
        u = User(
            username="student1",
            email="student1@test.example",
            password_hash=hash_password("password123"),
            is_admin=False,
        )
        db.session.add(u)
        db.session.commit()
        uid = u.id
    return uid


@pytest.fixture
def auth_client(client, app, student_user):
    client.post(
        "/auth/login",
        data={"username": "student1", "password": "password123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def admin_user(app):
    with app.app_context():
        u = User(
            username="adminx",
            email="adminx@test.example",
            password_hash=hash_password("adminpass123"),
            is_admin=True,
        )
        db.session.add(u)
        db.session.commit()
        uid = u.id
    return uid


@pytest.fixture
def admin_client(client, app, admin_user):
    client.post(
        "/auth/login",
        data={"username": "adminx", "password": "adminpass123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def sample_exam(app):
    from datetime import datetime, timedelta
    from datetime import time as dt_time

    with app.app_context():
        now = datetime.utcnow()
        e = Exam(
            title="Sample Exam",
            exam_date=(now + timedelta(days=20)).date(),
            exam_time=dt_time(10, 0),
            total_seats=10,
            seats_available=10,
            fee=10.0,
            registration_deadline=now + timedelta(days=10),
        )
        db.session.add(e)
        db.session.commit()
        eid = e.id
    return eid
