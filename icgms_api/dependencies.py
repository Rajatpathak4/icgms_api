from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from models import UserTable, Role, ActiveUser, MotorClaim, motor_claim_form_details, MotorCustomer, MotorProduct, WorkflowStep, FormDetails,  FormField, FormStep, MotorInsurer, FormValidation, FormOption
from database import Base, engine, get_db
from hashing import hash
from router import master




SECRET_KEY = "f388c51edeecf2d5dc5fe61e529c20cc286aa221a98c568d61d111e3d54ba0a1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()

class RoleDetailsResponse(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    role: str
    role_id: int
    no_of_role: int

class CreateUser(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role_id: int

class Token(BaseModel):
    access_token: str
    token_type: str




def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token decoding failed: {str(e)}")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token.credentials)
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current user: {str(e)}")
