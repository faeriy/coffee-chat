"""SQLAdmin authentication: login with app User (username/password)."""
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import verify_password
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse


class AdminAuth(AuthenticationBackend):
    """Validate admin login against the same User table as the main app."""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "").strip()
        password = form.get("password", "")

        if not username or not password:
            return False

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user or not user.hashed_password:
                return False
            if not verify_password(password, user.hashed_password):
                return False
            request.session.update({"admin_user_id": user.id})
            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin_user_id") is not None
