import csv
from io import StringIO

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError

from app.decorators import admin_required
from app.extensions import db
from app.forms import ExamForm
from app.models import Exam, Registration, User

bp = Blueprint("admin", __name__, url_prefix="/admin")

SORTABLE_COLUMNS = {
    "title": Exam.title,
    "exam_date": Exam.exam_date,
    "exam_time": Exam.exam_time,
    "total_seats": Exam.total_seats,
    "seats_available": Exam.seats_available,
    "fee": Exam.fee,
    "registration_deadline": Exam.registration_deadline,
    "id": Exam.id,
}


@bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    n_exams = Exam.query.count()
    n_regs = Registration.query.count()
    n_students = User.query.filter_by(is_admin=False).count()
    return render_template(
        "admin/dashboard.html",
        n_exams=n_exams,
        n_registrations=n_regs,
        n_students=n_students,
    )


@bp.route("/exams")
@login_required
@admin_required
def exams():
    sort_key = request.args.get("sort", "exam_date")
    if sort_key not in SORTABLE_COLUMNS:
        sort_key = "exam_date"
    order = request.args.get("order", "asc")
    col = SORTABLE_COLUMNS[sort_key]
    order_fn = desc if order == "desc" else asc
    page = request.args.get("page", 1, type=int)
    q = Exam.query.order_by(order_fn(col), asc(Exam.id))
    pagination = q.paginate(page=page, per_page=10, error_out=False)
    return render_template(
        "admin/exams.html",
        pagination=pagination,
        sort=sort_key,
        order=order,
    )


@bp.route("/exams/new", methods=["GET", "POST"])
@login_required
@admin_required
def exam_new():
    form = ExamForm()
    if form.validate_on_submit():
        exam = Exam(
            title=form.title.data.strip(),
            exam_date=form.exam_date.data,
            exam_time=form._time_only(),
            total_seats=form.total_seats.data,
            seats_available=form.total_seats.data,
            fee=form.fee.data,
            registration_deadline=form.registration_deadline.data,
        )
        db.session.add(exam)
        db.session.commit()
        flash("Exam created.", "success")
        return redirect(url_for("admin.exams"))
    return render_template("admin/exam_form.html", form=form, title="New exam")


@bp.route("/exams/<int:exam_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def exam_edit(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    form = ExamForm(obj=exam)
    if form.validate_on_submit():
        registered = exam.total_seats - exam.seats_available
        new_total = form.total_seats.data
        if new_total < registered:
            flash("Total seats cannot be less than the number already registered.", "danger")
            return render_template("admin/exam_form.html", form=form, title="Edit exam", exam=exam)
        exam.title = form.title.data.strip()
        exam.exam_date = form.exam_date.data
        exam.exam_time = form._time_only()
        exam.total_seats = new_total
        exam.seats_available = new_total - registered
        exam.fee = form.fee.data
        exam.registration_deadline = form.registration_deadline.data
        db.session.commit()
        flash("Exam updated.", "success")
        return redirect(url_for("admin.exams"))
    return render_template("admin/exam_form.html", form=form, title="Edit exam", exam=exam)


@bp.route("/exams/<int:exam_id>/delete", methods=["POST"])
@login_required
@admin_required
def exam_delete(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Could not delete exam.", "danger")
        return redirect(url_for("admin.exams"))
    flash("Exam and its registrations were deleted.", "success")
    return redirect(url_for("admin.exams"))


@bp.route("/exams/<int:exam_id>/registrations")
@login_required
@admin_required
def exam_registrations(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    rows = Registration.query.filter_by(exam_id=exam_id).order_by(Registration.registered_at.asc()).all()
    return render_template("admin/exam_registrations.html", exam=exam, registrations=rows)


@bp.route("/exams/<int:exam_id>/registrations/export")
@login_required
@admin_required
def exam_registrations_export(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    rows = Registration.query.filter_by(exam_id=exam_id).order_by(Registration.registered_at.asc()).all()
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["student_name", "student_email", "exam_title", "registration_date"])
    for r in rows:
        writer.writerow(
            [
                r.student.username,
                r.student.email,
                exam.title,
                r.registered_at.isoformat(),
            ]
        )
    out = buf.getvalue()
    return Response(
        out.encode("utf-8"),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="registrations-exam-{exam_id}.csv"',
        },
    )