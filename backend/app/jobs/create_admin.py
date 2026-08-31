"""
Bootstraps the first admin: creates (or reuses) a regular user account for the given
email/password and adds that email to admin_users. There's no other way to get the
first admin in, since /admin/api/* is gated on already being in admin_users.

Run via: python -m app.jobs.create_admin you@example.com yourpassword
"""
import sys

from app.core.security import hash_password
from app.db import SessionLocal
from app.models.admin_user import AdminUser
from app.models.user import User


def run(email: str, password: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(email=email, password_hash=hash_password(password))
            db.add(user)
            db.flush()
            print(f"Created user account for {email}")
        else:
            print(f"User account for {email} already exists - leaving password unchanged")

        admin = db.query(AdminUser).filter(AdminUser.email == email).first()
        if admin is None:
            db.add(AdminUser(email=email))
            print(f"Added {email} to admin_users")
        else:
            print(f"{email} is already an admin")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m app.jobs.create_admin <email> <password>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
