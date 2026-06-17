from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    declarative_base,
    relationship
)
from datetime import datetime
from database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key = True,
        index = True
    )
    username = Column(
        String(100),
        unique = True,
        nullable = False
    )
    email = Column(
        String(255),
        unique = True,
        nullable = False
    )
    password = Column(
        String(255),
        nullable = False
    )
    role = Column(
        String(20),
        default='user'
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    predictions = relationship(
    "Prediction",
    back_populates="user",
    cascade="all, delete"
    )  

class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    #gender = Column(String(20))

    #age = Column(Integer)

    #hypertension = Column(Integer)

    #heart_disease = Column(Integer)

    #smoking_history = Column(String(20))

    #bmi = Column(Float)

    #HbA1c_level = Column(Float)

    #blood_glucose_level = Column(Integer)

    prediction = Column(String(20))

    confidence = Column(Float)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    user = relationship(
    "User",
    back_populates="predictions"
    )