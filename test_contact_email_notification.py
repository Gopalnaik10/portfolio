"""
Automated Test Suite for Contact Form Submission & Email Notification Pipeline
"""
import urllib.request, urllib.error, json, http.cookiejar
from unittest.mock import patch, MagicMock
from backend.services.email_service import EmailService
from backend.services.portfolio_service import PortfolioService
from backend.models import db, Message, ActivityLog
from backend.app import create_app
from backend.config import Config

print("=== STARTING CONTACT FORM & EMAIL NOTIFICATION VERIFICATION ===")

app = create_app()

with app.app_context():
    
    # 1. Test EmailService Message Construction & Reply-To Headers
    
    # Configure mock test SMTP server
    Config.MAIL_SERVER = 'smtp.example.com'
    Config.MAIL_PORT = 587
    Config.MAIL_USERNAME = 'sender@example.com'
    Config.MAIL_PASSWORD = 'secretpassword'
    Config.MAIL_DEFAULT_SENDER = 'portfolio-notifications@example.com'
    Config.MAIL_RECIPIENT = 'owner@example.com'

    captured_sent_messages = []

    def mock_smtp_sendmail(sender, recipients, msg_str):
        captured_sent_messages.append({
            'sender': sender,
            'recipients': recipients,
            'raw_message': msg_str
        })
        return {}

    with patch('smtplib.SMTP') as mock_smtp_cls:
        mock_smtp_instance = MagicMock()
        mock_smtp_cls.return_value = mock_smtp_instance
        mock_smtp_instance.sendmail.side_effect = mock_smtp_sendmail

        success, msg = EmailService.send_contact_notification(
            name="Sarah Connor",
            email="sarah.connor@cyberdyne.org",
            subject="AI Collaboration Proposal",
            message="Hi Gopal, I reviewed your AI Gym Trainer and Emotion Detection projects. We would love to collaborate on computer vision models!"
        )

        assert success is True
        assert len(captured_sent_messages) == 1
        sent = captured_sent_messages[0]

        # Verify Sender & Recipient
        assert sent['sender'] == 'portfolio-notifications@example.com'
        assert sent['recipients'] == ['owner@example.com']

        import email
        parsed_msg = email.message_from_string(sent['raw_message'])
        assert parsed_msg['Reply-To'] == 'Sarah Connor <sarah.connor@cyberdyne.org>'
        assert parsed_msg['From'] == 'Portfolio Contact Form <portfolio-notifications@example.com>'
        assert parsed_msg['To'] == 'owner@example.com'

        # Check payload bodies
        body_payload = ''
        for part in parsed_msg.walk():
            if part.get_content_type() in ('text/plain', 'text/html'):
                body_payload += part.get_payload(decode=True).decode('utf-8', errors='ignore')

        assert 'Sarah Connor' in body_payload
        assert 'sarah.connor@cyberdyne.org' in body_payload
        assert 'AI Collaboration Proposal' in body_payload
        assert 'AI Gym Trainer and Emotion Detection' in body_payload
        assert 'portfolio website contact form' in body_payload

    print("[PASS] 1. EmailService properly constructed MIME message with Reply-To, subject, and visitor content.")

    
    # 2. Test End-to-End Contact Submission Pipeline via PortfolioService
    
    with patch('backend.services.email_service.EmailService.send_contact_notification') as mock_email_fn:
        mock_email_fn.return_value = (True, "Email sent successfully")

        # Submit contact message
        result = PortfolioService.submit_contact_message(
            name="John Doe",
            email="john.doe@example.com",
            subject="Internship Opportunity",
            message="We have an exciting Data Science internship role available."
        )

        # 1. Verify Message saved in DB
        db_msg = Message.query.filter_by(email="john.doe@example.com").first()
        assert db_msg is not None
        assert db_msg.name == "John Doe"
        assert db_msg.subject == "Internship Opportunity"
        assert db_msg.is_read is False

        # 2. Verify EmailService was invoked with exact visitor fields
        mock_email_fn.assert_called_once_with(
            name="John Doe",
            email="john.doe@example.com",
            subject="Internship Opportunity",
            message="We have an exciting Data Science internship role available."
        )

        # 3. Clean up test record
        db.session.delete(db_msg)
        db.session.commit()

    print("[PASS] 2. Contact submission pipeline saves to DB and triggers EmailService.")

    
    # 3. Test Failure Resilience (DB message preserved when SMTP fails)
    
    with patch('backend.services.email_service.EmailService.send_contact_notification') as mock_email_fn_fail:
        # Simulate SMTP timeout / authentication error
        mock_email_fn_fail.return_value = (False, "SMTP Authentication Error: Bad credentials")

        result = PortfolioService.submit_contact_message(
            name="Resilience Tester",
            email="tester@resilience.org",
            subject="System Test Subject",
            message="Testing that database message remains preserved even if SMTP server is down."
        )

        # Confirm DB message is 100% saved and intact
        db_msg = Message.query.filter_by(email="tester@resilience.org").first()
        assert db_msg is not None, "Message MUST be preserved in database when email fails"
        assert db_msg.name == "Resilience Tester"
        assert result['id'] == db_msg.id

        # Clean up
        db.session.delete(db_msg)
        db.session.commit()

    print("[PASS] 3. Database message is safely preserved when SMTP delivery encounters an error.")

    
    # 4. Test API Route via HTTP
    
    BASE = 'http://127.0.0.1:5000'
    contact_payload = json.dumps({
        'name': 'API Visitor',
        'email': 'api.visitor@example.com',
        'subject': 'Portfolio Inquiry',
        'message': 'Testing public API contact route.'
    }).encode('utf-8')

    req = urllib.request.Request(
        f"{BASE}/api/public/contact",
        data=contact_payload,
        headers={'Content-Type': 'application/json'}
    )
    api_res = json.loads(urllib.request.urlopen(req).read())
    assert api_res['success'] is True
    assert 'Thank you' in api_res['message']

    # Verify message in DB and in Admin Messages
    saved_msg = Message.query.filter_by(email='api.visitor@example.com').first()
    assert saved_msg is not None
    db.session.delete(saved_msg)
    db.session.commit()

    print("[PASS] 4. Public API endpoint /api/public/contact executed successfully.")

print("\n=== ALL CONTACT EMAIL NOTIFICATION TESTS PASSED SUCCESSFULLY ===")
