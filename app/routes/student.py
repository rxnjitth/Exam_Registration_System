from datetime import datetime

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Exam, Registration
from app.utils.pdf import build_hall_ticket_pdf

bp = Blueprint("student", __name__, url_prefix="/student")


@bp.before_request
@login_required
def ensure_student_area():
    if current_user.is_admin:
        flash("Use the admin area for your dashboard.", "info")
        return redirect(url_for("admin.dashboard"))


@bp.route("/dashboard")
def dashboard():
    my_regs = (
        Registration.query.filter_by(student_id=current_user.id)
        .join(Exam)
        .order_by(Exam.exam_date.asc(), Exam.exam_time.asc())
        .all()
    )
    upcoming = (
        Exam.query.filter(Exam.seats_available > 0)
        .filter(Exam.registration_deadline >= datetime.utcnow())
        .order_by(Exam.exam_date.asc(), Exam.exam_time.asc())
        .limit(12)
        .all()
    )
    return render_template(
        "student/dashboard.html",
        my_registrations=my_regs,
        upcoming_exams=upcoming,
    )


@bp.route("/exams")
def exams():
    all_exams = Exam.query.order_by(Exam.exam_date.asc(), Exam.exam_time.asc()).all()
    return render_template("student/exams.html", exams=all_exams)


@bp.route("/exams/<int:exam_id>/register", methods=["POST"])
def register_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if exam.is_deadline_passed:
        flash("Registration deadline has passed.", "danger")
        return redirect(url_for("student.exams"))
    if exam.seats_available <= 0:
        flash("No seats available for this exam.", "danger")
        return redirect(url_for("student.exams"))
    existing = Registration.query.filter_by(student_id=current_user.id, exam_id=exam_id).first()
    if existing:
        flash("You are already registered for this exam.", "danger")
        return redirect(url_for("student.exams"))

    reg = Registration(student_id=current_user.id, exam_id=exam_id)
    exam.seats_available -= 1
    db.session.add(reg)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Could not complete registration. Please try again.", "danger")
        return redirect(url_for("student.exams"))

    flash("Registration successful.", "success")
    return redirect(url_for("student.registrations"))


@bp.route("/registrations")
def registrations():
    rows = (
        Registration.query.filter_by(student_id=current_user.id)
        .join(Exam)
        .order_by(Exam.exam_date.asc(), Exam.exam_time.asc())
        .all()
    )
    return render_template("student/registrations.html", registrations=rows)


@bp.route("/registrations/<int:reg_id>/hall-ticket")
def hall_ticket(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    if reg.student_id != current_user.id:
        abort(403)
    exam = reg.exam
    student = reg.student
    pdf_bytes = build_hall_ticket_pdf(
        student_name=student.username,
        student_email=student.email,
        exam_title=exam.title,
        exam_date_str=exam.exam_date.isoformat(),
        exam_time_str=exam.exam_time.strftime("%H:%M"),
        registration_id=reg.id,
    )
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="hall-ticket-{reg.id}.pdf"',
        },
    )
