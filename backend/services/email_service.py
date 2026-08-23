import re
import smtplib
import logging
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from backend.config import Config

logger = logging.getLogger('EmailService')

class EmailService:
    @staticmethod
    def send_contact_notification(name: str, email: str, subject: str, message: str) -> tuple[bool, str]:
        """
        Sends an email notification to the portfolio owner when a visitor submits a contact message.
        - Uses SMTP credentials securely from environment variables.
        - Never exposes credentials or failure details to the public visitor.
        - Sets visitor's validated email as Reply-To.
        - Uses configured owner/sender address as authenticated SMTP sender.
        - Fails safely without impacting contact message database storage.
        """
        server_host = Config.MAIL_SERVER.strip() if Config.MAIL_SERVER else ''
        recipient = Config.MAIL_RECIPIENT.strip() if Config.MAIL_RECIPIENT else (Config.ADMIN_NOTIFICATION_EMAIL.strip() if Config.ADMIN_NOTIFICATION_EMAIL else '')

        if not server_host or not recipient:
            logger.info("[SMTP] Notification skipped: MAIL_SERVER or MAIL_RECIPIENT not configured in environment.")
            return False, "SMTP server or recipient not configured"

        port = Config.MAIL_PORT
        use_tls = Config.MAIL_USE_TLS
        use_ssl = Config.MAIL_USE_SSL
        username = Config.MAIL_USERNAME.strip() if Config.MAIL_USERNAME else ''
        password = Config.MAIL_PASSWORD.strip() if Config.MAIL_PASSWORD else ''

        # Support Gmail App Passwords with or without spaces
        if 'gmail' in server_host.lower() and password:
            password = password.replace(' ', '')

        sender = Config.MAIL_DEFAULT_SENDER.strip() if Config.MAIL_DEFAULT_SENDER else (username or 'noreply@portfolio.local')

        # Clean & validate visitor email for Reply-To
        clean_email = email.strip()
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', clean_email):
            clean_email = sender

        clean_name = re.sub(r'[\r\n]+', ' ', name.strip())
        clean_subject = re.sub(r'[\r\n]+', ' ', subject.strip())

        try:
            # Build MIME Message
            msg = MIMEMultipart('alternative')
            subject_str = f"New Portfolio Contact Message — {clean_name}: {clean_subject}" if clean_subject else f"New Portfolio Contact Message — {clean_name}"
            msg['Subject'] = Header(subject_str, 'utf-8')
            msg['From'] = f"Portfolio Contact Form <{sender}>"
            msg['To'] = recipient
            msg['Reply-To'] = f"{clean_name} <{clean_email}>"

            received_time = datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')

            # Plain text version
            text_body = f"""New Portfolio Contact Message — {clean_name}

A new message was submitted via the contact form on your portfolio website.

==================================================
Date / Time:   {received_time}
Visitor Name:  {clean_name}
Visitor Email: {clean_email}
Subject:       {clean_subject}
==================================================

Message:
--------------------------------------------------
{message.strip()}
--------------------------------------------------

* Reply directly to this email to respond to {clean_name} ({clean_email}).
* You can also review and manage all inquiries in your private Admin Dashboard: /admin
"""

            # HTML version
            html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #070B14; color: #F8FAFC; margin: 0; padding: 24px; }}
    .card {{ background-color: #0E1424; border: 1px solid rgba(129, 140, 248, 0.25); border-radius: 12px; max-width: 600px; margin: 0 auto; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .header {{ background: linear-gradient(135deg, #4F46E5, #8B5CF6); padding: 24px; text-align: left; }}
    .header h2 {{ margin: 0; color: #FFFFFF; font-size: 20px; font-weight: 700; }}
    .header p {{ margin: 6px 0 0 0; color: rgba(255,255,255,0.9); font-size: 13px; }}
    .content {{ padding: 24px; }}
    .field {{ margin-bottom: 18px; }}
    .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: #94A3B8; font-weight: 600; margin-bottom: 4px; }}
    .value {{ font-size: 15px; color: #FFFFFF; font-weight: 600; }}
    .value a {{ color: #818CF8; text-decoration: none; }}
    .msg-box {{ background-color: #070B14; border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 8px; padding: 16px; color: #E2E8F0; font-size: 14px; line-height: 1.6; white-space: pre-wrap; margin-top: 16px; }}
    .footer {{ padding: 16px 24px; background-color: #070B14; border-top: 1px solid rgba(148, 163, 184, 0.12); font-size: 12px; color: #64748B; text-align: center; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h2>📬 New Portfolio Contact Message</h2>
      <p>Received via your portfolio website contact form on {received_time}</p>
    </div>
    <div class="content">
      <div class="field">
        <div class="label">Sender Name</div>
        <div class="value">{clean_name}</div>
      </div>
      <div class="field">
        <div class="label">Sender Email</div>
        <div class="value"><a href="mailto:{clean_email}">{clean_email}</a></div>
      </div>
      <div class="field">
        <div class="label">Subject</div>
        <div class="value">{clean_subject}</div>
      </div>
      <div class="field">
        <div class="label">Message Body</div>
        <div class="msg-box">{message.strip()}</div>
      </div>
    </div>
    <div class="footer">
      💡 This notification was sent by your portfolio application. Simply hit <strong>Reply</strong> to email {clean_name} directly.
    </div>
  </div>
</body>
</html>"""

            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # Send via SMTP
            if use_ssl:
                server = smtplib.SMTP_SSL(server_host, port, timeout=12)
            else:
                server = smtplib.SMTP(server_host, port, timeout=12)
                if use_tls:
                    server.starttls()

            if username and password:
                server.login(username, password)

            server.sendmail(sender, [recipient], msg.as_string())
            server.quit()

            logger.info(f"[SMTP] Notification email successfully sent to {recipient}")
            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[SMTP] Authentication failed on {server_host}:{port}. Check MAIL_USERNAME and MAIL_PASSWORD (use an App Password for Gmail). Error: {e}")
            return False, f"SMTP Authentication Error: {str(e)}"
        except smtplib.SMTPConnectError as e:
            logger.error(f"[SMTP] Failed to connect to SMTP server {server_host}:{port}. Error: {e}")
            return False, f"SMTP Connection Error: {str(e)}"
        except Exception as e:
            logger.warning(f"[SMTP] Error during email delivery: {e}")
            return False, f"SMTP Error: {str(e)}"
