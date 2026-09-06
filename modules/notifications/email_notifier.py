"""
Email Integration — follows up on applications automatically.
Uses smtplib (stdlib, no new dependencies).
Sends follow-up emails for applications past follow-up date.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import sqlite3
from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmailConfig:
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_user: str = ""  # Set via env: EMAIL_SMTP_USER
    smtp_password: str = ""  # Set via env: EMAIL_SMTP_PASSWORD
    from_name: str = "Mojerry Career OS"
    enabled: bool = False  # Must be explicitly enabled


class Emailer:
    """Send career-related emails via SMTP. Follow-up dates from DB."""

    def __init__(self, config: EmailConfig = None):
        import os
        if config is None:
            self.config = EmailConfig(
                smtp_user=os.getenv("EMAIL_SMTP_USER", ""),
                smtp_password=os.getenv("EMAIL_SMTP_PASSWORD", ""),
                enabled=os.getenv("EMAIL_ENABLED", "false").lower() == "true",
            )
        else:
            self.config = config

    def get_due_followups(self, db_path: str = "career_os.db") -> List[Dict]:
        """Get applications past their follow-up date."""
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, company, title as role, url, follow_up_date, status
                FROM applications
                WHERE follow_up_date IS NOT NULL
                AND follow_up_date <= ?
                AND status IN ('applied', 'interview')
                ORDER BY follow_up_date ASC
            """, (datetime.now().isoformat(),)).fetchall()
        return [dict(r) for r in rows]

    def build_followup_email(self, app: Dict) -> tuple[str, str]:
        """Build subject + body for a follow-up. Returns (subject, body)."""
        subject = f"Following up — {app['role']} at {app['company']}"
        body = (
            f"Hi,\n\n"
            f"I wanted to follow up on my application for the {app['role']} position at {app['company']}. "
            f"I remain very interested in this opportunity and would love to discuss how my skills "
            f"in Python, SQL, data analysis, and automation could contribute to your team.\n\n"
            f"Following up again in one week if no response.\n\n"
            f"Best regards,\nMojerry"
        )
        return subject, body

    def send_email(self, to_email: str, subject: str, body: str) -> Dict:
        """Send an email via SMTP. Returns status dict."""
        if not self.config.enabled:
            return {"status": "disabled", "message": "Email not enabled. Set EMAIL_ENABLED=true."}
        if not self.config.smtp_user or not self.config.smtp_password:
            return {"status": "config_error", "message": "SMTP credentials not configured."}

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.config.from_name} <{self.config.smtp_user}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port, context=context) as server:
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.sendmail(self.config.smtp_user, to_email, msg.as_string())

            return {"status": "sent", "to": to_email, "subject": subject}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_followups(self, to_email: str = None, db_path: str = "career_os.db") -> Dict:
        """Send follow-up emails for all due applications."""
        due = self.get_due_followups(db_path)
        if not due:
            return {"status": "no_followups_due", "count": 0}

        results = []
        for app in due:
            subject, body = self.build_followup_email(app)
            result = self.send_email(to_email or self.config.smtp_user, subject, body)
            results.append({
                "company": app["company"],
                "role": app["role"],
                "result": result,
            })
            # Log to DB
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    INSERT INTO application_followups (application_id, follow_up_date, notes, sent)
                    VALUES (?, ?, ?, ?)
                """, (app["id"], datetime.now().isoformat(), f"Follow-up sent: {subject}", 1 if result["status"] == "sent" else 0))
                conn.commit()

        sent = sum(1 for r in results if r["result"].get("status") == "sent")
        return {"status": "complete", "total_due": len(due), "sent": sent, "results": results}

    def health_check(self) -> Dict:
        """Return email system health."""
        if not self.config.enabled:
            return {"status": "disabled", "configured": False, "smtp_host": self.config.smtp_host}
        return {
            "status": "enabled",
            "configured": bool(self.config.smtp_user and self.config.smtp_password),
            "smtp_host": self.config.smtp_host,
            "due_followups": len(self.get_due_followups()),
        }
