"""
Safe Diagnostic Script for SMTP Environment & Delivery
NEVER prints or exposes secrets / passwords.
"""
import os
import smtplib
import socket
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

print("=== SAFE SMTP DIAGNOSTIC AUDIT ===")

# 1. Check .env file presence
if env_path.exists():
    print(f"[ENV FILE] .env file FOUND at: {env_path}")
    load_dotenv(env_path)
else:
    print(f"[ENV FILE] WARNING: No .env file found at {env_path}!")

# 2. Check each variable configuration state
mail_server = os.getenv('MAIL_SERVER', '').strip()
mail_port = os.getenv('MAIL_PORT', '587').strip()
mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').strip()
mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False').strip()
mail_username = os.getenv('MAIL_USERNAME', '').strip()
mail_password = os.getenv('MAIL_PASSWORD', '').strip()
mail_default_sender = os.getenv('MAIL_DEFAULT_SENDER', '').strip()
mail_recipient = os.getenv('MAIL_RECIPIENT', os.getenv('ADMIN_NOTIFICATION_EMAIL', os.getenv('ADMIN_EMAIL', ''))).strip()

print("\n--- ENVIRONMENT VARIABLES CONFIGURATION STATUS ---")
print(f"MAIL_SERVER:         {'[CONFIGURED] ' + mail_server if mail_server else '[NOT SET / EMPTY]'}")
print(f"MAIL_PORT:           {'[CONFIGURED] ' + mail_port if mail_port else '[DEFAULT: 587]'}")
print(f"MAIL_USE_TLS:        {mail_use_tls}")
print(f"MAIL_USE_SSL:        {mail_use_ssl}")
print(f"MAIL_USERNAME:       {'[CONFIGURED] ' + mail_username if mail_username else '[NOT SET / EMPTY]'}")
print(f"MAIL_PASSWORD:       {'[CONFIGURED] (Length: ' + str(len(mail_password)) + ' chars, Hidden for security)' if mail_password else '[NOT SET / EMPTY]'}")
print(f"MAIL_DEFAULT_SENDER: {'[CONFIGURED] ' + mail_default_sender if mail_default_sender else '[NOT SET / EMPTY]'}")
print(f"MAIL_RECIPIENT:      {'[CONFIGURED] ' + mail_recipient if mail_recipient else '[NOT SET / EMPTY]'}")

# 3. Analyze Missing Parameters
missing = []
if not mail_server: missing.append("MAIL_SERVER")
if not mail_username: missing.append("MAIL_USERNAME")
if not mail_password: missing.append("MAIL_PASSWORD")
if not mail_recipient: missing.append("MAIL_RECIPIENT")

if missing:
    print(f"\n[DIAGNOSTIC RESULT] Missing required SMTP configuration: {', '.join(missing)}")
    print("Reason: Email cannot be dispatched because the SMTP credentials or server are not set in .env.")
else:
    print("\n--- ATTEMPTING LIVE SMTP CONNECTION & AUTHENTICATION TEST ---")
    try:
        port = int(mail_port)
        use_ssl = mail_use_ssl.lower() in ('true', '1', 't') or port == 465
        use_tls = mail_use_tls.lower() in ('true', '1', 't')
        
        pw = mail_password.replace(' ', '') if 'gmail' in mail_server.lower() else mail_password

        print(f"Connecting to {mail_server}:{port} (SSL={use_ssl}, TLS={use_tls})...")
        if use_ssl:
            server = smtplib.SMTP_SSL(mail_server, port, timeout=10)
        else:
            server = smtplib.SMTP(mail_server, port, timeout=10)
            if use_tls:
                server.starttls()

        print("Connection established. Authenticating...")
        server.login(mail_username, pw)
        print("[SUCCESS] SMTP Authentication SUCCESSFUL!")
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EXACT SMTP ERROR] Authentication Failed (Error Code {e.smtp_code}): {e.smtp_error.decode('utf-8', errors='ignore') if isinstance(e.smtp_error, bytes) else str(e.smtp_error)}")
    except (smtplib.SMTPConnectError, socket.timeout, socket.gaierror) as e:
        print(f"[EXACT SMTP ERROR] Connection / Network Error: {str(e)}")
    except Exception as e:
        print(f"[EXACT SMTP ERROR] {type(e).__name__}: {str(e)}")
