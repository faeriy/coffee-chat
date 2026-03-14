import secrets
from urllib.parse import urlencode

import httpx
from app.config import settings
from app.database import get_db, save_and_refresh
from app.models.user import User as DBUser
from app.schemas.token import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from app.utils.security import create_access_token, get_password_hash, verify_password
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Google OAuth 2.0 endpoints (authorization code flow)
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google sign-in. Please use “Sign in with Google”.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)


@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(DBUser).filter(DBUser.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    if db.query(DBUser).filter(DBUser.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    hashed_password = get_password_hash(user.password)
    new_user = DBUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    return save_and_refresh(db, new_user)


# ---------- Google OAuth 2.0 ----------


def _google_oauth_configured() -> bool:
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


@router.get("/google")
async def google_login():
    """
    Redirect the user to Google's consent screen (OAuth 2.0 authorization code flow).
    After the user signs in with Google, Google redirects back to /auth/google/callback.
    """
    if not _google_oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured (missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET)",
        )
    # Build redirect_uri for the callback (must match the one configured in Google Cloud Console)
    redirect_uri = f"{settings.BACKEND_URL.rstrip('/')}/auth/google/callback"
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    response = RedirectResponse(url=url)
    # Store state in a cookie so we can verify it in the callback (CSRF protection)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Google redirects here after the user signs in. We exchange the `code` for tokens,
    fetch the user's email/name, then create or find a user and issue our own JWT.
    Finally we redirect to the frontend with the token.
    """
    if not _google_oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured",
        )
    if error:
        # User denied consent or other error from Google
        frontend_login = f"{settings.FRONTEND_URL}/login?error=access_denied"
        return RedirectResponse(url=frontend_login)
    # Optional: verify state to prevent CSRF (state was set in cookie in /auth/google)
    saved_state = request.cookies.get("oauth_state")
    if saved_state and state and saved_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code from Google",
        )

    redirect_uri = f"{settings.BACKEND_URL.rstrip('/')}/auth/google/callback"
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token",
        )
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access_token in Google response",
        )

    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if userinfo_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch user info from Google",
        )
    userinfo = userinfo_response.json()
    google_sub = userinfo.get("id")
    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("email", "").split("@")[0]
    if not google_sub or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return id or email",
        )

    # Find existing user by Google id or by email (link account if they signed up with password first)
    user = db.query(DBUser).filter(DBUser.google_id == google_sub).first()
    if not user:
        user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        # New user: create with a unique username derived from Google
        username = f"google_{google_sub}"
        if db.query(DBUser).filter(DBUser.username == username).first():
            username = f"google_{google_sub}_{secrets.token_hex(4)}"
        user = DBUser(
            username=username,
            email=email,
            hashed_password=None,
            google_id=google_sub,
        )
        user = save_and_refresh(db, user)
    else:
        # Link Google id to existing account if not already set
        if not user.google_id:
            user.google_id = google_sub
            db.commit()
            db.refresh(user)

    jwt_token = create_access_token(data={"sub": user.username})
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    redirect_to = f"{frontend_url}/login?token={jwt_token}"
    response = RedirectResponse(url=redirect_to)
    response.delete_cookie("oauth_state")
    return response
