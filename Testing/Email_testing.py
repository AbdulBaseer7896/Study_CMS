"""
test_email.py — Standalone Django SMTP Email Test Script
=========================================================
HOW TO USE:
  1. Fill in your Gmail credentials below (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
  2. Set SEND_TO = "your-real-email@gmail.com"
  3. Run:  python test_email.py
  4. Check your inbox!

GMAIL SETUP (important — do this first):
  - Go to https://myaccount.google.com/security
  - Enable 2-Step Verification
  - Go to https://myaccount.google.com/apppasswords
  - Create an App Password for "Mail"
  - Use that 16-character password as EMAIL_HOST_PASSWORD below
  - Do NOT use your normal Gmail password

POSSIBLE WAYS TO SEND EMAIL IN DJANGO:
  1. Gmail SMTP (this script)     — Free, easy, 500/day limit
  2. SendGrid API                 — Free 100/day, very reliable
  3. Mailgun API                  — Free 100/day, great deliverability
  4. Amazon SES                   — Very cheap ($0.10 per 1000), production grade
  5. Outlook/Office365 SMTP       — Good for business accounts
  6. Brevo (ex-Sendinblue)        — Free 300/day
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ============================================================
# ✏️  CONFIGURE THESE
# ============================================================
EMAIL_HOST_USER     = "abdulbasirqazi7896@gmail.com"       # Your Gmail address
EMAIL_HOST_PASSWORD = "ftpk aumk mmzo gppw"        # 16-char App Password (NOT your real password)
SEND_TO             = "abdulbasirqazi@gmail.com"      # Who receives the test email
# ============================================================

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def build_html_email():
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Test Email</title>
    </head>
    <body style="margin:0; padding:0; background:#f4f6f9; font-family: Arial, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9; padding: 40px 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

              <!-- Header -->
              <tr>
                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 40px 30px; text-align:center;">
                  <h1 style="color:#ffffff; margin:0; font-size:28px; font-weight:700; letter-spacing:-0.5px;">
                    ✅ Email is Working!
                  </h1>
                  <p style="color:rgba(255,255,255,0.85); margin:10px 0 0; font-size:15px;">
                    Your Django SMTP configuration is correct
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding: 40px;">
                  <p style="color:#374151; font-size:16px; line-height:1.6; margin:0 0 20px;">
                    Hello! 👋
                  </p>
                  <p style="color:#374151; font-size:15px; line-height:1.7; margin:0 0 24px;">
                    This is a test HTML email sent via <strong>Django SMTP (Gmail)</strong>. 
                    If you're reading this, your email setup is working perfectly!
                  </p>

                  <!-- Info Card -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:28px;">
                    <tr>
                      <td style="padding:24px;">
                        <p style="margin:0 0 12px; color:#6b7280; font-size:12px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Configuration Details</p>
                        <table width="100%" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="color:#6b7280; font-size:14px; padding:6px 0; border-bottom:1px solid #e5e7eb; width:40%;">SMTP Host</td>
                            <td style="color:#111827; font-size:14px; padding:6px 0; border-bottom:1px solid #e5e7eb; font-weight:500;">smtp.gmail.com</td>
                          </tr>
                          <tr>
                            <td style="color:#6b7280; font-size:14px; padding:6px 0; border-bottom:1px solid #e5e7eb;">Port</td>
                            <td style="color:#111827; font-size:14px; padding:6px 0; border-bottom:1px solid #e5e7eb; font-weight:500;">587 (TLS)</td>
                          </tr>
                          <tr>
                            <td style="color:#6b7280; font-size:14px; padding:6px 0; border-bottom:1px solid #e5e7eb;">Sender</td>
                            <td style="color:#111827; font-size:14px; padding:6px 0; border-bottom:1px solid #e5e7eb; font-weight:500;">{EMAIL_HOST_USER}</td>
                          </tr>
                          <tr>
                            <td style="color:#6b7280; font-size:14px; padding:6px 0;">Sent At</td>
                            <td style="color:#111827; font-size:14px; padding:6px 0; font-weight:500;">{now}</td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- Next Steps -->
                  <p style="color:#374151; font-size:15px; font-weight:600; margin:0 0 12px;">Next Steps — Add to Django settings.py:</p>
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#1e293b; border-radius:8px; margin-bottom:28px;">
                    <tr>
                      <td style="padding:20px; font-family:monospace; font-size:13px; color:#94a3b8; line-height:1.8;">
                        <span style="color:#64748b;"># settings.py</span><br>
                        EMAIL_BACKEND = <span style="color:#86efac;">'django.core.mail.backends.smtp.EmailBackend'</span><br>
                        EMAIL_HOST = <span style="color:#86efac;">'smtp.gmail.com'</span><br>
                        EMAIL_PORT = <span style="color:#fbbf24;">587</span><br>
                        EMAIL_USE_TLS = <span style="color:#fbbf24;">True</span><br>
                        EMAIL_HOST_USER = <span style="color:#86efac;">os.getenv(<span style="color:#fda4af;">'EMAIL_HOST_USER'</span>)</span><br>
                        EMAIL_HOST_PASSWORD = <span style="color:#86efac;">os.getenv(<span style="color:#fda4af;">'EMAIL_HOST_PASSWORD'</span>)</span><br>
                        DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
                      </td>
                    </tr>
                  </table>

                  <p style="color:#374151; font-size:15px; font-weight:600; margin:0 0 12px;">Then send email anywhere in Django:</p>
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#1e293b; border-radius:8px; margin-bottom:28px;">
                    <tr>
                      <td style="padding:20px; font-family:monospace; font-size:13px; color:#94a3b8; line-height:1.8;">
                        <span style="color:#64748b;">from django.core.mail import send_mail</span><br><br>
                        send_mail(<br>
                        &nbsp;&nbsp;subject=<span style="color:#86efac;">'Hello!'</span>,<br>
                        &nbsp;&nbsp;message=<span style="color:#86efac;">'Plain text fallback'</span>,<br>
                        &nbsp;&nbsp;from_email=<span style="color:#86efac;">'you@gmail.com'</span>,<br>
                        &nbsp;&nbsp;recipient_list=[<span style="color:#86efac;">'user@example.com'</span>],<br>
                        &nbsp;&nbsp;html_message=<span style="color:#86efac;">'&lt;h1&gt;Hello HTML!&lt;/h1&gt;'</span>,<br>
                        )
                      </td>
                    </tr>
                  </table>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8fafc; padding:24px 40px; text-align:center; border-top:1px solid #e5e7eb;">
                  <p style="color:#9ca3af; font-size:12px; margin:0;">
                    Sent by <strong>test_email.py</strong> · Django SMTP Test Script
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    return html


def send_test_email():
    print("\n" + "="*55)
    print("  Django SMTP Email Test")
    print("="*55)
    print(f"  From : {EMAIL_HOST_USER}")
    print(f"  To   : {SEND_TO}")
    print(f"  Host : {SMTP_HOST}:{SMTP_PORT}")
    print("="*55)

    # Validate config
    if "your-gmail" in EMAIL_HOST_USER or "xxxx" in EMAIL_HOST_PASSWORD:
        print("\n❌  ERROR: Please fill in EMAIL_HOST_USER and EMAIL_HOST_PASSWORD at the top of this file.")
        print("    Get your App Password from: https://myaccount.google.com/apppasswords\n")
        return

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "✅ Django Email Test — It's Working!"
    msg["From"]    = EMAIL_HOST_USER
    msg["To"]      = SEND_TO

    # Plain text fallback
    plain = (
        "Hello!\n\n"
        "This is a test email sent via Django SMTP (Gmail).\n"
        "If you see this, your email setup is working!\n\n"
        f"Sent from: {EMAIL_HOST_USER}\n"
        f"SMTP: {SMTP_HOST}:{SMTP_PORT}\n"
    )

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(build_html_email(), "html"))

    # Send
    try:
        print("\n⏳  Connecting to Gmail SMTP...")
        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            print("✅  Connected")

            server.starttls(context=context)
            server.ehlo()
            print("✅  TLS started")

            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            print("✅  Logged in")

            server.sendmail(EMAIL_HOST_USER, SEND_TO, msg.as_string())
            print("✅  Email sent!\n")

        print("="*55)
        print(f"  📬  Check your inbox: {SEND_TO}")
        print("="*55 + "\n")

    except smtplib.SMTPAuthenticationError:
        print("\n❌  Authentication failed!")
        print("    → Make sure you're using an App Password, NOT your Gmail password.")
        print("    → Get one at: https://myaccount.google.com/apppasswords")
        print("    → 2-Step Verification must be ON first.\n")

    except smtplib.SMTPConnectError:
        print("\n❌  Could not connect to Gmail SMTP.")
        print("    → Check your internet connection.")
        print("    → Port 587 might be blocked by your firewall/ISP.\n")

    except smtplib.SMTPException as e:
        print(f"\n❌  SMTP Error: {e}\n")

    except Exception as e:
        print(f"\n❌  Unexpected error: {e}\n")


if __name__ == "__main__":
    send_test_email()