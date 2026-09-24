"""Gmail inbox and drafting tools using IMAP / SMTP with Google App Passwords."""

import email
from email.header import decode_header
from email.message import EmailMessage
import imaplib
import os
import re
import smtplib
import time
from typing import Any

from assistant.config import PROJECT_ROOT


def _get_credentials() -> tuple[str, str]:
    """Retrieve Gmail address and App Password from environment variables."""
    # Check current os.environ or reload from .env if needed
    user_email = os.getenv("GMAIL_ADDRESS", "").strip()
    app_password = os.getenv("GMAIL_APP_PASSWORD", "").strip().replace(" ", "")
    return user_email, app_password


def _decode_mime_header(header_val: str | None) -> str:
    if not header_val:
        return ""
    try:
        parts = decode_header(header_val)
        res = []
        for part, enc in parts:
            if isinstance(part, bytes):
                res.append(part.decode(enc or "utf-8", errors="replace"))
            else:
                res.append(str(part))
        return "".join(res)
    except Exception:
        return str(header_val)


def _extract_email_body(msg: email.message.Message) -> str:
    body = ""
    try:
        if msg.is_multipart():
            plain_part = None
            html_part = None
            for part in msg.walk():
                ctype = part.get_content_type()
                cdisp = str(part.get("Content-Disposition", ""))
                if "attachment" in cdisp:
                    continue
                if ctype == "text/plain" and not plain_part:
                    plain_part = part
                elif ctype == "text/html" and not html_part:
                    html_part = part

            target = plain_part or html_part
            if target:
                payload = target.get_payload(decode=True)
                if payload:
                    charset = target.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    if target == html_part:
                        try:
                            from bs4 import BeautifulSoup
                            body = BeautifulSoup(body, "html.parser").get_text(separator="\n").strip()
                        except Exception:
                            body = re.sub(r"<[^>]+>", " ", body).strip()
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
    except Exception as e:
        body = f"(Could not decode email body: {e})"
    return body.strip()


def _connect_imap() -> tuple[imaplib.IMAP4_SSL | None, str | None]:
    email_addr, app_password = _get_credentials()
    if not email_addr or not app_password:
        return None, (
            "Gmail credentials not configured. Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your .env file. "
            "Generate a 16-character App Password at: https://myaccount.google.com/apppasswords"
        )
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_addr, app_password)
        return mail, None
    except Exception as e:
        return None, f"Failed to connect to Gmail: {str(e)}"


def _find_drafts_folder(mail: imaplib.IMAP4_SSL) -> str:
    """Detect the localized Gmail drafts folder (e.g. '[Gmail]/Drafts' or '[Gmail]/Brouillons')."""
    try:
        typ, data = mail.list()
        if typ == "OK":
            for raw_entry in data:
                if isinstance(raw_entry, bytes):
                    entry = raw_entry.decode("utf-8", errors="ignore")
                    if "\\Drafts" in entry:
                        parts = entry.split(' "/" ')
                        if len(parts) == 2:
                            return parts[1].strip('"')
    except Exception:
        pass
    return "[Gmail]/Drafts"


def list_gmail_messages(folder: str = "INBOX", unread_only: bool = True, limit: int = 5) -> dict[str, Any]:
    """List recent emails from Gmail inbox with sender, subject, date, and message ID."""
    mail, err = _connect_imap()
    if err:
        return {"status": "error", "message": err}

    try:
        mail.select(folder, readonly=True)
        search_criteria = "UNSEEN" if unread_only else "ALL"
        status, response = mail.search(None, search_criteria)

        if status != "OK" or not response[0]:
            if unread_only:
                # Fallback to last emails if no unread
                status, response = mail.search(None, "ALL")

        msg_ids = response[0].split() if (status == "OK" and response[0]) else []
        if not msg_ids:
            mail.logout()
            return {"status": "success", "messages": [], "count": 0, "message": "No emails found in " + folder}

        # Take the most recent 'limit' messages
        recent_ids = msg_ids[-int(limit):]
        recent_ids.reverse()

        summaries = []
        for mid in recent_ids:
            id_str = mid.decode("utf-8")
            res, data = mail.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE MESSAGE-ID)])")
            if res == "OK" and data and isinstance(data[0], tuple):
                msg_header = email.message_from_bytes(data[0][1])
                subj = _decode_mime_header(msg_header.get("Subject", "(No Subject)"))
                sender = _decode_mime_header(msg_header.get("From", "(Unknown Sender)"))
                date = msg_header.get("Date", "")
                summaries.append({
                    "id": id_str,
                    "from": sender,
                    "subject": subj,
                    "date": date,
                })

        mail.logout()
        return {
            "status": "success",
            "count": len(summaries),
            "messages": summaries,
            "message": f"Found {len(summaries)} emails in {folder}.",
        }
    except Exception as e:
        try:
            mail.logout()
        except Exception:
            pass
        return {"status": "error", "message": f"Error retrieving emails: {str(e)}"}


def read_gmail_message(message_id: str) -> dict[str, Any]:
    """Read the full details and body content of a specific Gmail email by ID."""
    mail, err = _connect_imap()
    if err:
        return {"status": "error", "message": err}

    try:
        mail.select("INBOX", readonly=True)
        res, data = mail.fetch(message_id.encode("utf-8"), "(RFC822)")
        if res != "OK" or not data or not isinstance(data[0], tuple):
            mail.logout()
            return {"status": "error", "message": f"Email with ID {message_id} not found."}

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = _decode_mime_header(msg.get("Subject", "(No Subject)"))
        sender = _decode_mime_header(msg.get("From", "(Unknown Sender)"))
        to_addr = _decode_mime_header(msg.get("To", ""))
        date = msg.get("Date", "")
        orig_msg_id = msg.get("Message-ID", "")
        body = _extract_email_body(msg)

        mail.logout()
        return {
            "status": "success",
            "id": message_id,
            "subject": subject,
            "from": sender,
            "to": to_addr,
            "date": date,
            "message_id_header": orig_msg_id,
            "body": body[:4000],  # safety cap for LLM context
        }
    except Exception as e:
        try:
            mail.logout()
        except Exception:
            pass
        return {"status": "error", "message": f"Error reading email {message_id}: {str(e)}"}


def create_gmail_draft(
    recipient: str,
    subject: str,
    body: str,
    in_reply_to_msg_id: str = "",
) -> dict[str, Any]:
    """Create a draft reply or new email in Gmail Drafts folder so the user can review and hit Send."""
    user_email, app_password = _get_credentials()
    mail, err = _connect_imap()
    if err:
        return {"status": "error", "message": err}

    try:
        drafts_folder = _find_drafts_folder(mail)

        msg = EmailMessage()
        msg["From"] = user_email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        if in_reply_to_msg_id:
            msg["In-Reply-To"] = in_reply_to_msg_id
            msg["References"] = in_reply_to_msg_id

        msg.set_content(body)

        internal_date = imaplib.Time2Internaldate(time.time())
        # Append to drafts folder with \Draft flag
        typ, resp = mail.append(f'"{drafts_folder}"', "\\Draft", internal_date, msg.as_bytes())

        mail.logout()
        if typ != "OK":
            return {"status": "error", "message": f"Could not save draft to {drafts_folder}: {resp}"}

        gmail_drafts_url = "https://mail.google.com/mail/u/0/#drafts"
        return {
            "status": "success",
            "message": f"Draft created successfully in Gmail '{drafts_folder}' for {recipient}!\nYou can open Gmail and click 'Send': {gmail_drafts_url}",
            "recipient": recipient,
            "subject": subject,
            "draft_preview": body,
            "gmail_url": gmail_drafts_url,
        }
    except Exception as e:
        try:
            mail.logout()
        except Exception:
            pass
        return {"status": "error", "message": f"Error creating Gmail draft: {str(e)}"}


def send_gmail_message(recipient: str, subject: str, body: str) -> dict[str, Any]:
    """Send an email immediately via Gmail SMTP."""
    user_email, app_password = _get_credentials()
    if not user_email or not app_password:
        return {
            "status": "error",
            "message": "Gmail credentials not configured. Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env",
        }

    try:
        msg = EmailMessage()
        msg["From"] = user_email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(user_email, app_password)
            smtp.send_message(msg)

        return {
            "status": "success",
            "message": f"Email sent successfully to {recipient} with subject '{subject}'.",
            "recipient": recipient,
            "subject": subject,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {str(e)}"}
