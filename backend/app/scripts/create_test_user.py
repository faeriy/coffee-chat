"""
Create a test user (coffee / coffee) for immediate auth testing after first run.
- Called from FastAPI startup (same process, no env issues).
- Run locally: poetry run python -m app.scripts.create_test_user
"""
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

TEST_USERNAME = "coffee"
TEST_EMAIL = "coffee@example.com"
TEST_PASSWORD = "coffee"


def ensure_test_user_exists() -> None:
    """Create test user if missing. Safe to call on every startup."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == TEST_USERNAME).first()
        if existing:
            return
        user = User(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            hashed_password=get_password_hash(TEST_PASSWORD),
        )
        db.add(user)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    ensure_test_user_exists()
    print(f"Test user ready: username={TEST_USERNAME}, password={TEST_PASSWORD}")


if __name__ == "__main__":
    main()
