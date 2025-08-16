from dotenv import load_dotenv
import os
import imaplib
import email
from email.header import decode_header
import re

# Load .env values
load_dotenv()

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT"))

def clean_subject(subject):
    decoded, charset = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or 'utf-8')
    return decoded

def extract_verification_code(text):
    # TikTok usually sends a 6-digit code
    matches = re.findall(r"\b\d{6}\b", text)
    return matches[0] if matches else None

def read_tiktok_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    # Only look for TikTok mails (adjust subject or sender)
    # status, messages = mail.search(None, '(FROM "no-reply@tiktok.com")')
    # status, messages = mail.search(None, '(FROM "noreply@account.tiktok.com")')
    status, messages = mail.search(None, '(SUBJECT "verification code")')



    email_ids = messages[0].split()
    if not email_ids:
        print("No TikTok emails found.")
        return

    latest_id = email_ids[-1]
    status, msg_data = mail.fetch(latest_id, "(RFC822)")

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = clean_subject(msg["Subject"])
            sender = msg["From"]
            print(f"From: {sender}")
            print(f"Subject: {subject}")

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        print("Body:\n", body)

                        # Extract code
                        code = extract_verification_code(body)
                        if code:
                            print(f"\n✅ TikTok verification code: {code}")
                            return code
                        else:
                            print("No code found.")
                        return
            else:
                body = msg.get_payload(decode=True).decode()
                print("Body:\n", body)
                code = extract_verification_code(body)
                if code:
                    print(f"\n✅ TikTok verification code: {code}")
                    return code
                else:
                    print("No code found.")
    mail.logout()

# Run it
read_tiktok_email()
