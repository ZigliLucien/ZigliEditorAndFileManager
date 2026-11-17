"""QuickMail draft handoff, without hidden SMTP configuration or auto-send.

A mailto link passes a short buffer draft to the system's configured mail
application. ZEFM never sends mail. Long text must be handled by an external
composer instead of silently truncating a draft.
"""
from __future__ import annotations

from email.utils import parseaddr
from urllib.parse import urlencode

MAX_BODY = 12000
MAX_SUBJECT = 250


def validate_recipient(value):
    if not isinstance(value, str):
        raise ValueError("Recipient must be an email address")
    value = value.strip()
    if not value or len(value) > 320 or any(c in value for c in "\r\n\x00"):
        raise ValueError("Invalid email address")
    _name, addr = parseaddr(value)
    if addr != value or addr.count("@") != 1:
        raise ValueError("Enter a single email address without a display name")
    local, domain = addr.rsplit("@", 1)
    if (not local or not domain or "." not in domain
            or any(c.isspace() for c in addr)
            or any(c in addr for c in "/?&#%")):
        raise ValueError("Invalid email address")
    return addr


def quickmail_url(recipient, subject, body):
    address = validate_recipient(recipient)
    if not isinstance(subject, str) or not isinstance(body, str):
        raise ValueError("Subject and body must be strings")
    if len(subject) > MAX_SUBJECT or any(c in subject for c in "\r\n\x00"):
        raise ValueError("Subject is too long or contains a newline")
    if len(body) > MAX_BODY:
        raise ValueError(
            "Buffer is too long for a mailto draft; copy it into your mail editor")
    return "mailto:" + address + "?" + urlencode(
        {"subject": subject, "body": body})
