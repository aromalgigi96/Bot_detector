import os
import logging
from datetime import datetime, timedelta

import lightgbm as lgb
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import SQLModel, select
from passlib.hash import bcrypt
import jwt

from app.database import engine, get_session
from app.models import User, LoginAttempt
from sqlmodel import Session

# --- FastAPI setup ---
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Bot Detector API", version="0.1.0")

# --- Ensure tables exist ---
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    logging.info("Database tables created/verified.")

# --- Load ML model (optional) ---
MODEL_PATH = os.getenv("MODEL_PATH", "/app/notebooks/final_lightgbm_tuned.txt")
try:
    booster = lgb.Booster(model_file=MODEL_PATH)
    logging.info(f"Loaded model from {MODEL_PATH}")
except Exception as e:
    booster = None
    logging.warning(f"Could not load LightGBM model ({e}), falling back to threshold.")

# --- JWT config ---
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    payload = verify_token(token)
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# --- Request schemas ---
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str
    uri: str
    client_ip: str
    timestamp: float
    time_to_submit: float


# --- Registration endpoint ---
@app.post("/register")
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")
    user = User(
        username=payload.username,
        password_hash=bcrypt.hash(payload.password)
    )
    session.add(user)
    session.commit()
    return {"message": "User registered successfully."}


# --- Login endpoint (issues JWT) ---
@app.post("/login")
def login(req: LoginRequest, session: Session = Depends(get_session)):
    # 1) Authenticate
    user = session.exec(select(User).where(User.username == req.username)).first()
    if not user or not bcrypt.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # 2) Bot-detection w/ fallback
    try:
        if booster:
            prob = float(booster.predict(pd.DataFrame([{"time_to_submit": req.time_to_submit}]))[0])
        else:
            raise ValueError("No model loaded")
    except Exception:
        prob = 0.99 if req.time_to_submit < 0.5 else 0.01
    label = "Attack" if prob >= 0.5 else "Benign"

    # 3) Log attempt
    attempt = LoginAttempt(
        user_id=user.id,
        username=req.username,
        ip=req.client_ip,
        uri=req.uri,
        timestamp=datetime.utcnow(),
        time_to_submit=req.time_to_submit,
        label=label,
        score=round(prob, 2)
    )
    session.add(attempt)
    session.commit()

    # 4) Block or issue JWT
    if label == "Attack":
        raise HTTPException(status_code=403, detail="Bot detected! Access denied.")

    token_data = {"user_id": user.id, "username": user.username}
    access_token = create_access_token(token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "balance": "$3,200.00",
        "account": "ACCT-1234"
    }


# --- Admin-only attack log endpoint ---
@app.get("/attacks")
def get_attacks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only the “admin” user can fetch this
    if current_user.username.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    stmt = select(LoginAttempt).order_by(LoginAttempt.timestamp.desc()).limit(100)
    attempts = session.exec(stmt).all()
    return [
        {
            "time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": a.ip,
            "username": a.username,
            "uri": a.uri,
            "result": a.label,
            "score": a.score
        }
        for a in attempts
    ]


# --- Public health check ---
@app.get("/health")
def health():
    return {"status": "ok"}
