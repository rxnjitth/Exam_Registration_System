from app.extensions import db
from app.models import User
from app.utils.passwords import verify_password


def test_register_creates_student(client, app):
    resp = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "new@test.example",
            "password": "longenough",
            "confirm_password": "longenough",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        u = User.query.filter_by(username="newuser").first()
        assert u is not None
        assert verify_password("longenough", u.password_hash)


def test_register_rejects_short_password(client, app):
    client.post(
        "/auth/register",
        data={
            "username": "u2",
            "email": "u2@test.example",
            "password": "short",
            "confirm_password": "short",
        },
    )
    with app.app_context():
        assert User.query.filter_by(username="u2").first() is None


def test_login_redirect_student(client, app, student_user):
    resp = client.post(
        "/auth/login",
        data={"username": "student1", "password": "password123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/student/dashboard" in resp.headers.get("Location", "")


def test_login_redirect_admin(client, app, admin_user):
    resp = client.post(
        "/auth/login",
        data={"username": "adminx", "password": "adminpass123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/admin/dashboard" in resp.headers.get("Location", "")


def test_logout(client, student_user):
    client.post("/auth/login", data={"username": "student1", "password": "password123"})
    resp = client.get("/auth/logout", follow_redirects=False)
    assert resp.status_code == 302
