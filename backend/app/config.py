from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost/coffeechat"

    # JWT
    SECRET_KEY: str = "secretkeyforprod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google OAuth 2.0 (optional; leave empty to disable "Sign in with Google")
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    # Backend base URL (for OAuth redirect_uri); e.g. http://localhost:8000
    BACKEND_URL: str = "http://localhost:8000"
    # Where the frontend lives; used to redirect after Google login (e.g. http://localhost:5173)
    FRONTEND_URL: str = "http://localhost:5173"

    # S3 Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "eu-central-1"
    S3_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
