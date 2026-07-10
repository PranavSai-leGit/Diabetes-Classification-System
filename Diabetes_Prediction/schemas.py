from typing import Literal, Optional
from datetime import datetime
import re
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    field_validator
)

class UserCreate(BaseModel):

    username:str = Field(
        min_length=3,
        max_length=100
    )

    email:EmailStr

    password:str

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number.')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter.')
        return v

class UserLogin(BaseModel):

    email:EmailStr

    password:str = Field(
        min_length=8
    )

class UserResponse(BaseModel):

    id:int

    username:str

    email:EmailStr

    role:str

    last_login:Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PredictionInput(BaseModel):

    gender: Literal['Male','Female','Other']

    age: int = Field(
        gt=0,
        lt=120
    )

    hypertension: Literal[0,1]

    heart_disease: Literal[0,1]
    
    smoking_history: Literal[
        "never",
        "former",
        "current",
        "not current",
        "No Info",
        "ever"
    ]

    bmi: float = Field(
        gt=0,
        lt=100
    )

    HbA1c_level: float = Field(
        gt=0
    )

    blood_glucose_level: int = Field(
        gt=0
    )

class PredictionResponse(BaseModel):

    prediction: Literal['Diabetic','Non-Diabetic']

    confidence: float = Field(
        ge=0,
        le=1
    )

class filter_input(BaseModel):

    status: Literal['Diabetic', 'Non-Diabetic', 'None']

class RoleUpdateRequest(BaseModel):

    role: Literal['user', 'admin']

class UserUpdate(BaseModel):

    username: Optional[str] = Field(None, min_length=3, max_length=100)

    email: Optional[EmailStr] = None

    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number.')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter.')
        return v