from datetime import datetime, timedelta
from datetime import time as dt_time

from app.extensions import db
from app.models import Exam, User
from app.utils.passwords import hash_password


def seed_defaults():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin"),
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()

    if Exam.query.count() >= 4:
        return

    now = datetime.utcnow()
    samples = [
        (
            "Mathematics Proficiency",
            (now + timedelta(days=45)).date(),
            dt_time(9, 30),
            80,
            29.99,
            now + timedelta(days=35),
        ),
        (
            "English Composition",
            (now + timedelta(days=60)).date(),
            dt_time(13, 0),
            120,
            0.0,
            now + timedelta(days=50),
        ),
        (
            "Computer Science Fundamentals",
            (now + timedelta(days=14)).date(),
            dt_time(10, 0),
            40,
            49.5,
            now + timedelta(days=7),
        ),
        (
            "General Science (Past deadline demo)",
            (now + timedelta(days=90)).date(),
            dt_time(11, 15),
            200,
            15.0,
            now - timedelta(days=1),
        ),
        (
            "History & Civics",
            (now + timedelta(days=75)).date(),
            dt_time(15, 45),
            25,
            19.0,
            now + timedelta(days=65),
        ),
    ]
    for title, d, t, seats, fee, deadline in samples:
        if Exam.query.filter_by(title=title).first():
            continue
        ex = Exam(
            title=title,
            exam_date=d,
            exam_time=t,
            total_seats=seats,
            seats_available=seats,
            fee=fee,
            registration_deadline=deadline,
        )
        db.session.add(ex)
    db.session.commit()
