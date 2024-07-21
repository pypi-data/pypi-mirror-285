# © 2024 | All Rights reserved by Around With Us
# bounce_mail_identifier/email_extractor.py

import re

def extract_sender_address(text):
    sender_pattern = r'From:\s*(.*)'
    match = re.search(sender_pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return None

def extract_failed_recipients(text):
    recipient_pattern = r'X-Failed-Recipients:\s*([\w\.-]+@[\w\.-]+)'
    matches = re.findall(recipient_pattern, text)
    return [match.strip() for match in matches] if matches else []
