from sqlmodel import Session, select

from app.celery_app import celery_app
from app.database import engine
from app.models import LoginLog, User


@celery_app.task
def check_login_location(user_id: str, current_ip: str):
    with Session(engine) as session:
        statement = (
            select(LoginLog)
            .where(LoginLog.user_id == user_id)
            .order_by(LoginLog.login_timestamp.desc())
            .limit(6)
        )
        all_logins = session.exec(statement).all()

        recent_logins = all_logins[1:6] if len(all_logins) > 1 else []
        recent_ips = [login.ip_address for login in recent_logins if login.ip_address]

        if current_ip not in recent_ips and len(recent_ips) > 0:
            user = session.get(User, user_id)
            if user:
                send_location_alert_email.delay(user.email, current_ip, recent_ips)


@celery_app.task
def send_location_alert_email(email: str, current_ip: str, recent_ips: list[str]):
    print(f"EMAIL NOTIFICATION:")
    print(f"To: {email}")
    print(f"Subject: Login from new location detected")
    print(f"Message: You are logging in from IP {current_ip}.")
    print(
        f"This IP is different from your recent login locations: {', '.join(recent_ips)}"
    )
    print(f"If this was not you, please secure your account immediately.")
