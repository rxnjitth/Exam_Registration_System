from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import DateField, DateTimeField, FloatField, IntegerField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError


class ExamForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"class": "form-control"},
    )
    exam_date = DateField(
        "Exam date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        render_kw={"class": "form-control", "type": "date"},
    )
    exam_time = TimeField(
        "Exam time",
        validators=[DataRequired()],
        format="%H:%M",
        render_kw={"class": "form-control", "type": "time"},
    )
    total_seats = IntegerField(
        "Total seats",
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={"class": "form-control", "min": 1},
    )
    fee = FloatField(
        "Fee",
        validators=[DataRequired(), NumberRange(min=0)],
        render_kw={"class": "form-control", "min": 0, "step": "0.01"},
    )
    registration_deadline = DateTimeField(
        "Registration deadline",
        validators=[DataRequired()],
        format="%Y-%m-%dT%H:%M",
        render_kw={"class": "form-control", "type": "datetime-local"},
    )
    submit = SubmitField("Save")

    def validate_registration_deadline(self, field):
        if not self.exam_date.data:
            return
        time_part = self._time_only()
        if time_part is None:
            return
        exam_dt = datetime.combine(self.exam_date.data, time_part)
        if field.data >= exam_dt:
            raise ValidationError("Registration deadline must be before the exam start.")

    def _time_only(self):
        return self.exam_time.data
