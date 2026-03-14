from contextlib import asynccontextmanager

from app.admin.auth import AdminAuth
from app.admin.views import register_views
from app.config import settings
from app.database import engine, get_db
from app.models.user import User as DBUser
from app.routes import auth_router
from app.scripts.create_test_user import ensure_test_user_exists
from app.utils.security import decode_access_token
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqladmin import Admin
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: ensure test user (coffee/coffee) exists for immediate testing."""
    ensure_test_user_exists()
    yield


app = FastAPI(title="Coffee Chat API", version="0.1.0", lifespan=lifespan)

# Session middleware required for SQLAdmin login (same secret as JWT)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes from the separate file
app.include_router(auth_router)

# SQLAdmin: protected by username/password (same User table as main app)
admin = Admin(
    app,
    engine,
    title="Coffee Chat Admin",
    base_url="/admin",
    authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
)
register_views(admin)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> DBUser:
    """
    Dependency that returns the currently authenticated user or raises 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    user = db.query(DBUser).filter(DBUser.username == sub).first()
    if user is None:
        raise credentials_exception

    return user


@app.get("/users/me", response_model=None)
async def read_me(current_user: DBUser = Depends(get_current_user)):
    return current_user
