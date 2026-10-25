"""
Project 4 (Automation): Email Automation System
Sends personalized bulk emails from a template + a recipient list (CSV-style),
using Python's built-in smtplib. Supports a DRY-RUN mode (default) that
prints exactly what would be sent without connecting anywhere — so you can
safely test before sending real mail.

REAL SENDING: fill in SMTP_CONFIG with your provider (e.g. Gmail requires an
"app password", not your normal password) and run with --send. The sending
code is production-correct; dry-run is the default for safety.

Run: pip install (nothing — smtplib is built in)
     python 04_email_automation_system.py           # dry run (safe)
     python 04_email_automation_system.py --send     # actually sends

Concepts practiced: templated personalization, MIME multipart email
construction, smtplib/TLS flow, and a safe dry-run default — a real-world
automation-safety habit.
"""

import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Fill these in to actually send. Left blank so dry-run is the only thing
# that works out of the box (no accidental sends).
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "",          # your email
    "password": "",          # app password, NOT your login password
    "from_name": "Darshini N",
}

# In a real project this comes from a CSV: pandas.read_csv("recipients.csv")
RECIPIENTS = [
    {"email": "alice@example.com", "name": "Alice", "company": "Acme"},
    {"email": "bob@example.com", "name": "Bob", "company": "Globex"},
    {"email": "carol@example.com", "name": "Carol", "company": "Initech"},
]

SUBJECT_TEMPLATE = "Quick question about {company}"
BODY_TEMPLATE = """Hi {name},

I came across {company} and wanted to reach out about a project I think
could be a good fit.

Would you be open to a short call next week?

Best,
Darshini
"""


def build_message(recipient, from_addr):
    msg = MIMEMultipart()
    msg["From"] = f"{SMTP_CONFIG['from_name']} <{from_addr}>"
    msg["To"] = recipient["email"]
    msg["Subject"] = SUBJECT_TEMPLATE.format(**recipient)
    body = BODY_TEMPLATE.format(**recipient)
    msg.attach(MIMEText(body, "plain"))
    return msg


def send_all(dry_run=True):
    from_addr = SMTP_CONFIG["username"] or "you@example.com"

    if dry_run:
        print(">>> DRY RUN — no emails will actually be sent.\n")
        for r in RECIPIENTS:
            msg = build_message(r, from_addr)
            print(f"--- To: {r['email']} ---")
            print(f"Subject: {msg['Subject']}")
            print(msg.get_payload()[0].get_payload())
            print()
        print(f"{len(RECIPIENTS)} email(s) prepared (dry run).")
        return

    # Real sending path.
    if not SMTP_CONFIG["username"] or not SMTP_CONFIG["password"]:
        print("ERROR: fill in SMTP_CONFIG username/password to send for real.")
        return

    print("Connecting to SMTP server...")
    with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
        server.starttls()  # upgrade to encrypted connection
        server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
        for r in RECIPIENTS:
            msg = build_message(r, from_addr)
            server.send_message(msg)
            print(f"  Sent to {r['email']}")
    print(f"\nDone — {len(RECIPIENTS)} email(s) sent.")


def main():
    print("=== Email Automation System ===")
    send = "--send" in sys.argv
    send_all(dry_run=not send)


if __name__ == "__main__":
    main()