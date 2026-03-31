# # myapp/Utils/email_tasks.py
# """
# All email sending via Celery tasks — non-blocking, background thread.

# Tasks:
#   - send_welcome_email_task        → new user/consultant created
#   - send_student_welcome_task      → new student created
#   - send_forgot_password_otp_task  → OTP for password reset
#   - send_application_created_task  → new application created
#   - send_application_updated_task  → application status/fee/offer updated
# """

# from celery import shared_task
# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
# from datetime import datetime


# # ── Shared HTML wrapper ───────────────────────────────────────────────
# def _wrap_html(title, subtitle, body_html, footer_note=""):
#     return f"""
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="UTF-8">
#   <meta name="viewport" content="width=device-width, initial-scale=1.0">
# </head>
# <body style="margin:0;padding:0;background:#0f172a;font-family:Arial,sans-serif;">
#   <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:32px 16px;">
#     <tr><td align="center">
#       <table width="600" cellpadding="0" cellspacing="0"
#         style="background:#1e293b;border-radius:16px;overflow:hidden;border:1px solid #334155;max-width:600px;width:100%;">

#         <!-- Header -->
#         <tr>
#           <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:32px 40px;text-align:center;">
#             <h1 style="color:#fff;margin:0;font-size:24px;font-weight:700;">{title}</h1>
#             <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:14px;">{subtitle}</p>
#           </td>
#         </tr>

#         <!-- Body -->
#         <tr>
#           <td style="padding:32px 40px;color:#cbd5e1;font-size:15px;line-height:1.7;">
#             {body_html}
#           </td>
#         </tr>

#         <!-- Footer -->
#         <tr>
#           <td style="background:#0f172a;padding:20px 40px;text-align:center;border-top:1px solid #334155;">
#             <p style="color:#475569;font-size:12px;margin:0;">
#               StudyCMS &nbsp;·&nbsp; {datetime.now().strftime("%B %d, %Y")}
#               {"&nbsp;·&nbsp;" + footer_note if footer_note else ""}
#             </p>
#           </td>
#         </tr>

#       </table>
#     </td></tr>
#   </table>
# </body>
# </html>
# """


# def _info_row(label, value):
#     return f"""
#     <tr>
#       <td style="color:#94a3b8;font-size:13px;padding:7px 0;border-bottom:1px solid #334155;width:40%;">{label}</td>
#       <td style="color:#f1f5f9;font-size:13px;padding:7px 0;border-bottom:1px solid #334155;font-weight:500;">{value}</td>
#     </tr>"""


# def _info_table(rows_html):
#     return f"""
#     <table width="100%" cellpadding="0" cellspacing="0"
#       style="background:#0f172a;border-radius:10px;border:1px solid #334155;margin:20px 0;padding:4px 20px;">
#       {rows_html}
#     </table>"""


# def _send(subject, to_list, html, cc_list=None, plain=""):
#     """Low-level send helper."""
#     from_email = settings.DEFAULT_FROM_EMAIL
#     msg = EmailMultiAlternatives(subject, plain or "Please view this email in an HTML-capable client.", from_email, to_list, cc=cc_list or [])
#     msg.attach_alternative(html, "text/html")
#     msg.send(fail_silently=False)


# # ════════════════════════════════════════════════════════════════════
# #  TASK 1 — Welcome email for Admin / Consultant
# # ════════════════════════════════════════════════════════════════════
# @shared_task(bind=True, max_retries=3, default_retry_delay=30)
# def send_welcome_email_task(self, user_id):
#     try:
#         from myapp.Models.Auth_models import User
#         user = User.objects.get(id=user_id)

#         role_label = user.role.capitalize()
#         body = f"""
#         <p>Hello <strong style="color:#a5b4fc;">{user.name}</strong>,</p>
#         <p>Your <strong>{role_label}</strong> account has been created on <strong>StudyCMS</strong>.
#         You can now log in to the portal with your credentials.</p>

#         {_info_table(
#             _info_row("Full Name", user.name) +
#             _info_row("Email", user.email) +
#             _info_row("Role", role_label) +
#             _info_row("Phone", user.phone or "—")
#         )}

#         <p>If you have any questions, please contact your administrator.</p>
#         <p style="color:#6366f1;font-weight:600;">Welcome aboard! 🎉</p>
#         """

#         html = _wrap_html(
#             f"Welcome to StudyCMS, {user.name}!",
#             f"Your {role_label} account is ready",
#             body
#         )
#         _send(f"Welcome to StudyCMS — {user.name}", [user.email], html)

#     except Exception as exc:
#         raise self.retry(exc=exc)


# # ════════════════════════════════════════════════════════════════════
# #  TASK 2 — Welcome email for Student
# # ════════════════════════════════════════════════════════════════════
# @shared_task(bind=True, max_retries=3, default_retry_delay=30)
# def send_student_welcome_task(self, student_id):
#     try:
#         from myapp.Models.Auth_models import User
#         student = User.objects.get(id=student_id)

#         consultant_name = student.assigned_to.name if student.assigned_to else "Our Team"

#         body = f"""
#         <p>Dear <strong style="color:#a5b4fc;">{student.name}</strong>,</p>
#         <p>Welcome to <strong>StudyCMS</strong>! Your student profile has been set up successfully.
#         Your assigned consultant is <strong>{consultant_name}</strong>, who will guide you
#         through your study abroad journey.</p>

#         {_info_table(
#             _info_row("Full Name", student.name) +
#             _info_row("Email", student.email) +
#             _info_row("Phone", student.phone or "—") +
#             _info_row("Assigned Consultant", consultant_name) +
#             _info_row("Reference", student.reference.name if student.reference else "—")
#         )}

#         <p>Our team will keep you updated on every step of your application process.
#         Whenever a new application is created or updated for you, you'll receive an email.</p>

#         <p style="color:#10b981;font-weight:600;">Best of luck on your journey! 🌍</p>
#         """

#         html = _wrap_html(
#             f"Welcome, {student.name}!",
#             "Your StudyCMS student profile is ready",
#             body
#         )
#         _send(f"Welcome to StudyCMS — {student.name}", [student.email], html)

#     except Exception as exc:
#         raise self.retry(exc=exc)


# # ════════════════════════════════════════════════════════════════════
# #  TASK 3 — Forgot Password OTP
# # ════════════════════════════════════════════════════════════════════
# @shared_task(bind=True, max_retries=3, default_retry_delay=10)
# def send_forgot_password_otp_task(self, user_id, otp):
#     try:
#         from myapp.Models.Auth_models import User
#         user = User.objects.get(id=user_id)

#         body = f"""
#         <p>Hello <strong style="color:#a5b4fc;">{user.name}</strong>,</p>
#         <p>You requested a password reset for your StudyCMS account.
#         Use the OTP below to reset your password:</p>

#         <div style="text-align:center;margin:28px 0;">
#           <div style="display:inline-block;background:#1e293b;border:2px solid #6366f1;
#             border-radius:14px;padding:20px 48px;">
#             <span style="font-size:42px;font-weight:800;letter-spacing:12px;color:#a5b4fc;font-family:monospace;">
#               {otp}
#             </span>
#           </div>
#           <p style="color:#ef4444;font-size:13px;margin:12px 0 0;">
#             ⏱ This OTP expires in <strong>40 seconds</strong>
#           </p>
#         </div>

#         <p style="color:#64748b;font-size:13px;">
#           If you did not request this, please ignore this email. Your account is safe.
#         </p>
#         """

#         html = _wrap_html(
#             "Password Reset OTP",
#             "Use this OTP to reset your password — expires in 40 seconds",
#             body,
#             footer_note="Do not share this OTP with anyone"
#         )
#         _send("StudyCMS — Password Reset OTP", [user.email], html)

#     except Exception as exc:
#         raise self.retry(exc=exc)


# # ════════════════════════════════════════════════════════════════════
# #  TASK 4 — New Application Created
# # ════════════════════════════════════════════════════════════════════
# @shared_task(bind=True, max_retries=3, default_retry_delay=30)
# def send_application_created_task(self, application_id):
#     try:
#         from myapp.Models.Application_models import Application
#         from myapp.Models.Auth_models import User

#         app = Application.objects.select_related(
#             'student', 'student__assigned_to', 'created_by'
#         ).get(id=application_id)

#         student   = app.student
#         consultant = student.assigned_to

#         # Get all admin emails for CC
#         admin_emails = list(User.objects.filter(role='admin').values_list('email', flat=True))
#         cc_emails = admin_emails.copy()
#         if consultant and consultant.email not in cc_emails:
#             cc_emails.append(consultant.email)

#         body = f"""
#         <p>Dear <strong style="color:#a5b4fc;">{student.name}</strong>,</p>
#         <p>A new university application has been created for you by
#         <strong>{app.created_by.name if app.created_by else "our team"}</strong>.
#         Here are the details:</p>

#         {_info_table(
#             _info_row("Application", app.application_name) +
#             _info_row("University", app.university) +
#             _info_row("Country", app.country) +
#             _info_row("City", app.city) +
#             _info_row("Degree", app.degree_name) +
#             _info_row("Course", app.course_title) +
#             _info_row("Status", app.get_status_display()) +
#             _info_row("Apply Fee", f"${app.apply_fee}" if app.apply_fee else "—") +
#             _info_row("Yearly Fee", f"${app.yearly_fee}" if app.yearly_fee else "—") +
#             _info_row("Last Date to Apply", str(app.last_date_to_apply) if app.last_date_to_apply else "—") +
#             _info_row("Expected Offer Date", str(app.expected_offer_date) if app.expected_offer_date else "—")
#         )}

#         <p>Your consultant <strong>{consultant.name if consultant else "our team"}</strong>
#         will keep you updated on the progress. You will receive an email for every update.</p>
#         <p style="color:#6366f1;font-weight:600;">Good luck! 🎓</p>
#         """

#         html = _wrap_html(
#             "New Application Created",
#             f"{app.university} — {app.course_title}",
#             body
#         )
#         _send(
#             f"New Application: {app.application_name}",
#             [student.email],
#             html,
#             cc_list=cc_emails
#         )

#     except Exception as exc:
#         raise self.retry(exc=exc)


# # ════════════════════════════════════════════════════════════════════
# #  TASK 5 — Application Updated (status, fee, offer letter, etc.)
# # ════════════════════════════════════════════════════════════════════
# @shared_task(bind=True, max_retries=3, default_retry_delay=30)
# def send_application_updated_task(self, application_id, updated_fields, updated_by_name):
#     try:
#         from myapp.Models.Application_models import Application
#         from myapp.Models.Auth_models import User

#         app = Application.objects.select_related(
#             'student', 'student__assigned_to'
#         ).get(id=application_id)

#         student   = app.student
#         consultant = student.assigned_to

#         admin_emails = list(User.objects.filter(role='admin').values_list('email', flat=True))
#         cc_emails = admin_emails.copy()
#         if consultant and consultant.email not in cc_emails:
#             cc_emails.append(consultant.email)

#         # Build changes section
#         changes_html = ""
#         if updated_fields:
#             rows = ""
#             for field, value in updated_fields.items():
#                 rows += _info_row(field, value)
#             changes_html = f"""
#             <p style="color:#94a3b8;font-size:13px;font-weight:600;margin:20px 0 4px;text-transform:uppercase;letter-spacing:1px;">
#               What Changed
#             </p>
#             {_info_table(rows)}
#             """

#         # Status badge color
#         status_colors = {
#             'draft':          '#64748b',
#             'applied':        '#3b82f6',
#             'under_review':   '#f59e0b',
#             'offer_received': '#8b5cf6',
#             'accepted':       '#10b981',
#             'rejected':       '#ef4444',
#             'withdrawn':      '#94a3b8',
#             'enrolled':       '#06b6d4',
#         }
#         status_color = status_colors.get(app.status, '#6366f1')

#         body = f"""
#         <p>Dear <strong style="color:#a5b4fc;">{student.name}</strong>,</p>
#         <p>Your application has been updated by <strong>{updated_by_name}</strong>.
#         Here is the current status:</p>

#         <div style="text-align:center;margin:20px 0;">
#           <span style="display:inline-block;background:{status_color}22;border:1px solid {status_color};
#             color:{status_color};font-weight:700;font-size:14px;padding:8px 24px;border-radius:999px;text-transform:uppercase;letter-spacing:1px;">
#             {app.get_status_display()}
#           </span>
#         </div>

#         {_info_table(
#             _info_row("Application", app.application_name) +
#             _info_row("University", app.university) +
#             _info_row("Country", app.country) +
#             _info_row("Course", app.course_title) +
#             _info_row("Apply Fee", f"${app.apply_fee}" if app.apply_fee else "—") +
#             _info_row("Yearly Fee", f"${app.yearly_fee}" if app.yearly_fee else "—") +
#             _info_row("Offer Letter", "✅ Attached" if app.offer_letter else "—") +
#             _info_row("Fee Slip", "✅ Uploaded" if app.fee_slip else "—") +
#             _info_row("Last Date to Apply", str(app.last_date_to_apply) if app.last_date_to_apply else "—") +
#             _info_row("Expected Offer Date", str(app.expected_offer_date) if app.expected_offer_date else "—")
#         )}

#         {changes_html}

#         <p>Your assigned consultant <strong>{consultant.name if consultant else "our team"}</strong>
#         is monitoring your application. We'll notify you of every update.</p>
#         """

#         html = _wrap_html(
#             "Application Updated",
#             f"{app.university} — {app.application_name}",
#             body
#         )
#         _send(
#             f"Application Update: {app.application_name}",
#             [student.email],
#             html,
#             cc_list=cc_emails
#         )

#     except Exception as exc:
#         raise self.retry(exc=exc)












# myapp/Utils/email_tasks.py
"""
All email sending via Celery tasks — non-blocking, background thread.

Tasks:
  - send_welcome_email_task        → new user/consultant created
  - send_student_welcome_task      → new student created
  - send_forgot_password_otp_task  → OTP for password reset
  - send_application_created_task  → new application created
  - send_application_updated_task  → application status/fee/offer updated
"""

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime


# ── Shared HTML wrapper ───────────────────────────────────────────────
def _wrap_html(title, subtitle, body_html, footer_note=""):
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:32px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
        style="background:#1e293b;border-radius:16px;overflow:hidden;border:1px solid #334155;max-width:600px;width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:32px 40px;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:24px;font-weight:700;">{title}</h1>
            <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:14px;">{subtitle}</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px 40px;color:#cbd5e1;font-size:15px;line-height:1.7;">
            {body_html}
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#0f172a;padding:20px 40px;text-align:center;border-top:1px solid #334155;">
            <p style="color:#475569;font-size:12px;margin:0;">
              StudyCMS &nbsp;·&nbsp; {datetime.now().strftime("%B %d, %Y")}
              {"&nbsp;·&nbsp;" + footer_note if footer_note else ""}
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def _info_row(label, value):
    return f"""
    <tr>
      <td style="color:#94a3b8;font-size:13px;padding:7px 0;border-bottom:1px solid #334155;width:40%;">{label}</td>
      <td style="color:#f1f5f9;font-size:13px;padding:7px 0;border-bottom:1px solid #334155;font-weight:500;">{value}</td>
    </tr>"""


def _info_table(rows_html):
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
      style="background:#0f172a;border-radius:10px;border:1px solid #334155;margin:20px 0;padding:4px 20px;">
      {rows_html}
    </table>"""


def _send(subject, to_list, html, cc_list=None, plain=""):
    """Low-level send helper."""
    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, plain or "Please view this email in an HTML-capable client.", from_email, to_list, cc=cc_list or [])
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)


# ════════════════════════════════════════════════════════════════════
#  TASK 1 — Welcome email for Admin / Consultant
# ════════════════════════════════════════════════════════════════════
@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email_task(self, user_id):
    try:
        from myapp.Models.Auth_models import User
        user = User.objects.get(id=user_id)

        role_label = user.role.capitalize()
        body = f"""
        <p>Hello <strong style="color:#a5b4fc;">{user.name}</strong>,</p>
        <p>Your <strong>{role_label}</strong> account has been created on <strong>StudyCMS</strong>.
        You can now log in to the portal with your credentials.</p>

        {_info_table(
            _info_row("Full Name", user.name) +
            _info_row("Email", user.email) +
            _info_row("Role", role_label) +
            _info_row("Phone", user.phone or "—")
        )}

        <p>If you have any questions, please contact your administrator.</p>
        <p style="color:#6366f1;font-weight:600;">Welcome aboard! 🎉</p>
        """

        html = _wrap_html(
            f"Welcome to StudyCMS, {user.name}!",
            f"Your {role_label} account is ready",
            body
        )
        _send(f"Welcome to StudyCMS — {user.name}", [user.email], html)

    except Exception as exc:
        raise self.retry(exc=exc)


# ════════════════════════════════════════════════════════════════════
#  TASK 2 — Welcome email for Student
# ════════════════════════════════════════════════════════════════════
@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_student_welcome_task(self, student_id):
    try:
        from myapp.Models.Auth_models import User
        student = User.objects.get(id=student_id)

        consultant_name = student.assigned_to.name if student.assigned_to else "Our Team"

        body = f"""
        <p>Dear <strong style="color:#a5b4fc;">{student.name}</strong>,</p>
        <p>Welcome to <strong>StudyCMS</strong>! Your student profile has been set up successfully.
        Your assigned consultant is <strong>{consultant_name}</strong>, who will guide you
        through your study abroad journey.</p>

        {_info_table(
            _info_row("Full Name", student.name) +
            _info_row("Email", student.email) +
            _info_row("Phone", student.phone or "—") +
            _info_row("Assigned Consultant", consultant_name) +
            _info_row("Reference", student.reference.name if student.reference else "—")
        )}

        <p>Our team will keep you updated on every step of your application process.
        Whenever a new application is created or updated for you, you'll receive an email.</p>

        <p style="color:#10b981;font-weight:600;">Best of luck on your journey! 🌍</p>
        """

        html = _wrap_html(
            f"Welcome, {student.name}!",
            "Your StudyCMS student profile is ready",
            body
        )
        _send(f"Welcome to StudyCMS — {student.name}", [student.email], html)

    except Exception as exc:
        raise self.retry(exc=exc)


# ════════════════════════════════════════════════════════════════════
#  TASK 3 — Forgot Password OTP
# ════════════════════════════════════════════════════════════════════
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_forgot_password_otp_task(self, user_id, otp):
    try:
        from myapp.Models.Auth_models import User
        user = User.objects.get(id=user_id)

        body = f"""
        <p>Hello <strong style="color:#a5b4fc;">{user.name}</strong>,</p>
        <p>You requested a password reset for your StudyCMS account.
        Use the OTP below to reset your password:</p>

        <div style="text-align:center;margin:28px 0;">
          <div style="display:inline-block;background:#1e293b;border:2px solid #6366f1;
            border-radius:14px;padding:20px 48px;">
            <span style="font-size:42px;font-weight:800;letter-spacing:12px;color:#a5b4fc;font-family:monospace;">
              {otp}
            </span>
          </div>
          <p style="color:#ef4444;font-size:13px;margin:12px 0 0;">
            ⏱ This OTP expires in <strong>40 seconds</strong>
          </p>
        </div>

        <p style="color:#64748b;font-size:13px;">
          If you did not request this, please ignore this email. Your account is safe.
        </p>
        """

        html = _wrap_html(
            "Password Reset OTP",
            "Use this OTP to reset your password — expires in 40 seconds",
            body,
            footer_note="Do not share this OTP with anyone"
        )
        _send("StudyCMS — Password Reset OTP", [user.email], html)

    except Exception as exc:
        raise self.retry(exc=exc)


# ════════════════════════════════════════════════════════════════════
#  TASK 4 — New Application Created
# ════════════════════════════════════════════════════════════════════
@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_application_created_task(self, application_id):
    try:
        from myapp.Models.Application_models import Application
        from myapp.Models.Auth_models import User

        app = Application.objects.select_related(
            'student', 'student__assigned_to', 'created_by'
        ).get(id=application_id)

        student   = app.student
        consultant = student.assigned_to

        # Get all admin emails for CC
        admin_emails = list(User.objects.filter(role='admin').values_list('email', flat=True))
        cc_emails = admin_emails.copy()
        if consultant and consultant.email not in cc_emails:
            cc_emails.append(consultant.email)

        body = f"""
        <p>Dear <strong style="color:#a5b4fc;">{student.name}</strong>,</p>
        <p>A new university application has been created for you by
        <strong>{app.created_by.name if app.created_by else "our team"}</strong>.
        Here are the details:</p>

        {_info_table(
            _info_row("Application", app.application_name) +
            _info_row("University", app.university) +
            _info_row("Country", app.country) +
            _info_row("City", app.city) +
            _info_row("Degree", app.degree_name) +
            _info_row("Course", app.course_title) +
            _info_row("Status", app.get_status_display()) +
            _info_row("Apply Fee", f"${app.apply_fee}" if app.apply_fee else "—") +
            _info_row("Yearly Fee", f"${app.yearly_fee}" if app.yearly_fee else "—") +
            _info_row("Last Date to Apply", str(app.last_date_to_apply) if app.last_date_to_apply else "—") +
            _info_row("Expected Offer Date", str(app.expected_offer_date) if app.expected_offer_date else "—")
        )}

        <p>Your consultant <strong>{consultant.name if consultant else "our team"}</strong>
        will keep you updated on the progress. You will receive an email for every update.</p>
        <p style="color:#6366f1;font-weight:600;">Good luck! 🎓</p>
        """

        html = _wrap_html(
            "New Application Created",
            f"{app.university} — {app.course_title}",
            body
        )
        _send(
            f"New Application: {app.application_name}",
            [student.email],
            html,
            cc_list=cc_emails
        )

    except Exception as exc:
        raise self.retry(exc=exc)


# ════════════════════════════════════════════════════════════════════
#  TASK 5 — Application Updated (status, fee, offer letter, etc.)
# ════════════════════════════════════════════════════════════════════
@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_application_updated_task(self, application_id, updated_fields, updated_by_name):
    try:
        from myapp.Models.Application_models import Application
        from myapp.Models.Auth_models import User

        app = Application.objects.select_related(
            'student', 'student__assigned_to'
        ).get(id=application_id)

        student   = app.student
        consultant = student.assigned_to

        admin_emails = list(User.objects.filter(role='admin').values_list('email', flat=True))
        cc_emails = admin_emails.copy()
        if consultant and consultant.email not in cc_emails:
            cc_emails.append(consultant.email)

        # Build changes section
        # If a value looks like a URL (starts with http), render as a clickable link
        changes_html = ""
        if updated_fields:
            rows = ""
            for field, value in updated_fields.items():
                if value.startswith('http'):
                    # Plain <a> tag — works in every email client including Gmail
                    cell = f'<a href="{value}" target="_blank" style="color:#a5b4fc;font-weight:600;text-decoration:underline;">View File</a>'
                    rows += _info_row(field, cell)
                else:
                    rows += _info_row(field, value)
            changes_html = f"""
            <p style="color:#94a3b8;font-size:13px;font-weight:600;margin:20px 0 4px;text-transform:uppercase;letter-spacing:1px;">
              What Changed
            </p>
            {_info_table(rows)}
            """

        # Status badge color
        status_colors = {
            'draft':          '#64748b',
            'applied':        '#3b82f6',
            'under_review':   '#f59e0b',
            'offer_received': '#8b5cf6',
            'accepted':       '#10b981',
            'rejected':       '#ef4444',
            'withdrawn':      '#94a3b8',
            'enrolled':       '#06b6d4',
        }
        status_color = status_colors.get(app.status, '#6366f1')

        body = f"""
        <p>Dear <strong style="color:#a5b4fc;">{student.name}</strong>,</p>
        <p>Your application has been updated by <strong>{updated_by_name}</strong>.
        Here is the current status:</p>

        <div style="text-align:center;margin:20px 0;">
          <span style="display:inline-block;background:{status_color}22;border:1px solid {status_color};
            color:{status_color};font-weight:700;font-size:14px;padding:8px 24px;border-radius:999px;text-transform:uppercase;letter-spacing:1px;">
            {app.get_status_display()}
          </span>
        </div>

        {_info_table(
            _info_row("Application", app.application_name) +
            _info_row("University", app.university) +
            _info_row("Country", app.country) +
            _info_row("Course", app.course_title) +
            _info_row("Apply Fee", f"${app.apply_fee}" if app.apply_fee else "—") +
            _info_row("Yearly Fee", f"${app.yearly_fee}" if app.yearly_fee else "—") +
            _info_row("Offer Letter", "✅ Attached" if app.offer_letter else "—") +
            _info_row("Fee Slip", "✅ Uploaded" if app.fee_slip else "—") +
            _info_row("Last Date to Apply", str(app.last_date_to_apply) if app.last_date_to_apply else "—") +
            _info_row("Expected Offer Date", str(app.expected_offer_date) if app.expected_offer_date else "—")
        )}

        {changes_html}

        <p>Your assigned consultant <strong>{consultant.name if consultant else "our team"}</strong>
        is monitoring your application. We'll notify you of every update.</p>
        """

        html = _wrap_html(
            "Application Updated",
            f"{app.university} — {app.application_name}",
            body
        )
        _send(
            f"Application Update: {app.application_name}",
            [student.email],
            html,
            cc_list=cc_emails
        )

    except Exception as exc:
        raise self.retry(exc=exc)