import bcrypt
from jose import (
    jwt,
    JWTError,
    ExpiredSignatureError
)
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import (
    Request,
    HTTPException,
    Depends
)
from fastapi.security import OAuth2PasswordBearer
from models import User
from sqlalchemy.orm import Session
from database import get_db
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')

#-----Password Hashing-----
def hash_password(password: str) -> str:
    
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


#-----Password Verification-----
def check_password(password: str, hashed_password: str) ->bool:

    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )


#-----Access token generation-----
def create_access_token(data: dict, expires_minutes: int = 30):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)

    to_encode.update({
        "exp":expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


#-----Access token verificaton-----
def verify_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )
        return payload

    except JWTError:
        return None
    

#-----Verifying current user-----
def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):


    if token is None:
        raise HTTPException (   
            status_code=401,
            detail="Login required"
        )
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"{e}"
        )
    
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user