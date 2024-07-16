import imaplib
import email
from email import policy
import re
from pathlib import Path
from fotoviewer import FOTOVIEWER_ADDRES, FOTOVIEWER_PASS, INBOX, create_sub_dirs, date_time_file_prefix


def sanitize_filename(filename):
    """Sanitize file-name so it can be read"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

def eml_file_name(subject, date_time):
    """Construct new file name from date_time, sender and file_name"""

    eml_file_name = ""

    if date_time is not None:
        eml_file_name = date_time_file_prefix(date_time)
    
    return sanitize_filename(f"{eml_file_name}_{subject}.eml")

def read_mailbox(inbox:Path|None = INBOX, email_address:str | None = FOTOVIEWER_ADDRES, password:str | None = FOTOVIEWER_PASS):
    """Read a simple mailbox (works for hotmail)."""
    if (email_address is None) | (password is None):
        raise ValueError(f"Both 'email_address'{email_address} and 'password' {password} shouldn't be None")
    
    # Create inbox and other dirs if do not exist
    if inbox is None:
        raise FileNotFoundError(f"Inbox not found: {inbox}")
    else:
        create_sub_dirs(inbox.parent)

    # Connect to the server
    mail = imaplib.IMAP4_SSL("imap-mail.outlook.com")

    # Log in to your account
    mail.login(email_address, password)

    # Select the mailbox you want to download from
    mail.select("inbox")

    # Search for all emails in the mailbox
    status, messages = mail.search(None, "ALL")

    # Convert messages to a list of email IDs
    email_ids = messages[0].split()

    # Loop through email IDs and fetch the emails
    for email_id in email_ids:
        # Fetch the email by ID
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        
        # Get the email content
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1], policy=policy.default)
                
                # Extract subject and date
                subject = msg["subject"]
                date = msg["date"]
                
                # Parse the date
                email_date = email.utils.parsedate_to_datetime(date)
                
                # Save the email with the formatted filename
                eml_file_path = inbox / eml_file_name(subject, email_date)
                eml_file_path.write_bytes(response_part[1])

                # Copy the email to the Archive folder
                mail.copy(email_id, 'Archive')
                
                # Mark the email as deleted in the current folder
                mail.store(email_id, '+FLAGS', '\\Deleted')

    # Expunge to permanently remove the deleted emails
    mail.expunge()

    # Logout and close the connection
    mail.logout()