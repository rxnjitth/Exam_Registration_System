from datetime import datetime

from app.extensions import db


class Exam(db.Model):
    __tablename__ = "exam"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.Time, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    registrations = db.relationship(
        "Registration",
        backref="exam",
        lazy=True,
        cascade="all, delete-orphan",
    )

    @property
    def is_deadline_passed(self):
        return datetime.utcnow() > self.registration_deadline

    @property
    def is_full(self):
        return self.seats_available <= 0

    @property
    def is_open(self):
        return not self.is_deadline_passed and not self.is_full


class Registration(db.Model):
    __tablename__ = "registration"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    __table_args__ = (db.UniqueConstraint("student_id", "exam_id", name="uq_student_exam"),)
