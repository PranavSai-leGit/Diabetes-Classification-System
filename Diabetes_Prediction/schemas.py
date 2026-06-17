from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict
)

class UserCreate(BaseModel):

    username:str = Field(
        min_length=3,
        max_length=100
    )

    email:EmailStr

    password:str = Field(
        min_length=8
    )

class UserLogin(BaseModel):

    email:EmailStr

    password:str = Field(
        min_length=8
    )

class UserResponse(BaseModel):

    id:int

    username:str

    email:EmailStr

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