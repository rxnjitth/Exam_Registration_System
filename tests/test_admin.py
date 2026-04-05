from app.extensions import db
from app.models import Exam, Registration, User


def test_admin_dashboard_counts(admin_client, app, sample_exam, student_user):
    with app.app_context():
        u = db.session.get(User, student_user)
        db.session.add(Registration(student_id=u.id, exam_id=sample_exam))
        ex = db.session.get(Exam, sample_exam)
        ex.seats_available -= 1
        db.session.commit()

    r = admin_client.get("/admin/dashboard")
    assert r.status_code == 200
    assert b"Admin dashboard" in r.data
    assert b"Registrations" in r.data


def test_non_admin_redirect_from_admin(auth_client):
    r = auth_client.get("/admin/dashboard", follow_redirects=True)
    assert r.status_code == 200
    assert b"Access denied" in r.data or b"student" in r.data.lower()


def test_csv_export_headers(admin_client, app, sample_exam, student_user):
    with app.app_context():
        u = db.session.get(User, student_user)
        db.session.add(Registration(student_id=u.id, exam_id=sample_exam))
        ex = db.session.get(Exam, sample_exam)
        ex.seats_available -= 1
        db.session.commit()

    r = admin_client.get(f"/admin/exams/{sample_exam}/registrations/export")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("Content-Disposition", "")
    assert b"student_name" in r.data
    assert b"Sample Exam" in r.data


def test_delete_exam_removes_registrations(admin_client, app, sample_exam, student_user):
    with app.app_context():
        u = db.session.get(User, student_user)
        db.session.add(Registration(student_id=u.id, exam_id=sample_exam))
        ex = db.session.get(Exam, sample_exam)
        ex.seats_available -= 1
        db.session.commit()
        eid = sample_exam

    admin_client.post(f"/admin/exams/{eid}/delete", follow_redirects=True)
    with app.app_context():
        assert db.session.get(Exam, eid) is None
        assert Registration.query.filter_by(exam_id=eid).count() == 0
