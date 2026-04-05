from app.extensions import db
from app.models import Exam, Registration


def test_browse_exams_requires_login(client):
    r = client.get("/student/exams", follow_redirects=False)
    assert r.status_code == 302


def test_register_for_exam(auth_client, app, sample_exam):
    r = auth_client.post(f"/student/exams/{sample_exam}/register", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        reg = Registration.query.filter_by(exam_id=sample_exam).first()
        assert reg is not None
        ex = db.session.get(Exam, sample_exam)
        assert ex.seats_available == 9


def test_hall_ticket_forbidden_other_student(client, app, sample_exam):
    from app.models import User
    from app.utils.passwords import hash_password

    with app.app_context():
        a = User(
            username="a",
            email="a@test.example",
            password_hash=hash_password("password123"),
            is_admin=False,
        )
        b = User(
            username="b",
            email="b@test.example",
            password_hash=hash_password("password123"),
            is_admin=False,
        )
        db.session.add_all([a, b])
        db.session.commit()
        reg = Registration(student_id=a.id, exam_id=sample_exam)
        ex = db.session.get(Exam, sample_exam)
        ex.seats_available -= 1
        db.session.add(reg)
        db.session.commit()
        rid = reg.id

    client.post("/auth/login", data={"username": "b", "password": "password123"})
    r = client.get(f"/student/registrations/{rid}/hall-ticket")
    assert r.status_code == 403


def test_hall_ticket_pdf_contains_fields(auth_client, app, sample_exam):
    with app.app_context():
        from flask_login import login_user
        from app.models import User

        u = User.query.filter_by(username="student1").first()
        reg = Registration(student_id=u.id, exam_id=sample_exam)
        ex = db.session.get(Exam, sample_exam)
        ex.seats_available -= 1
        db.session.add(reg)
        db.session.commit()
        rid = reg.id

    r = auth_client.get(f"/student/registrations/{rid}/hall-ticket")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert b"Sample Exam" in r.data
    assert str(rid).encode() in r.data or b"Registration ID" in r.data
