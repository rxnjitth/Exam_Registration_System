from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_hall_ticket_pdf(
    student_name: str,
    student_email: str,
    exam_title: str,
    exam_date_str: str,
    exam_time_str: str,
    registration_id: int,
) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    y = height - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "Exam Hall Ticket")
    y -= 36
    c.setFont("Helvetica", 11)
    lines = [
        f"Registration ID: {registration_id}",
        f"Student: {student_name}",
        f"Email: {student_email}",
        "",
        f"Exam: {exam_title}",
        f"Date: {exam_date_str}",
        f"Time: {exam_time_str}",
    ]
    for line in lines:
        c.drawString(72, y, line)
        y -= 18
    c.showPage()
    c.save()
    return buf.getvalue()
