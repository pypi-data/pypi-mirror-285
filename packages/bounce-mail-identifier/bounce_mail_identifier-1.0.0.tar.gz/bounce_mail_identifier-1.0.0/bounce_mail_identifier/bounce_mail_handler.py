# bounce_mail_identifier/bounce_mail_handler.py
# © 2024 | All Rights reserved by Around With Us

import imaplib
import email
import pandas as pd
from bounce_mail_identifier.email_extractor import extract_sender_address, extract_failed_recipients

def fetch_bounce_emails(username, app_password, imap_server, imap_port=993):
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(username, app_password)

        mailbox = "inbox"
        mail.select(mailbox)

        search_criteria = '(SUBJECT "Delivery Status Notification (Failure)")'
        result, email_data = mail.search(None, search_criteria)

        bounces = []

        for num in email_data[0].split():
            result, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_string(msg_data[0][1].decode('utf-8'))
            sender_address = extract_sender_address(msg.as_string())
            failed_recipients = extract_failed_recipients(msg.as_string())

            if failed_recipients:
                for recipient in failed_recipients:
                    bounces.append({'Sender': sender_address, 'Failed Recipient': recipient})

        mail.logout()

        return bounces

    except Exception as e:
        print(f"Error fetching bounce emails: {str(e)}")
        return []

def save_bounces_to_excel(bounces, file_path):
    df = pd.DataFrame(bounces)
    df.to_excel(file_path, index=False)

def main():
    # Example usage:
    username = 'your-email@example.com'
    app_password = 'your-app-password'
    imap_server = 'imap.example.com'
    bounces = fetch_bounce_emails(username, app_password, imap_server)
    save_bounces_to_excel(bounces, 'bounces.xlsx')

if __name__ == "__main__":
    main()
