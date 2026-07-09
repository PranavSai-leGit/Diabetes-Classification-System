from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    backref
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
    password_hash = Column(
        String(255),
        nullable = False
    )
    role = Column(
        String(20),
        default='user'
    )
    last_login = Column(
        DateTime,
        nullable=True
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

    gender = Column(String(20))

    age = Column(Integer)

    hypertension = Column(Integer)

    heart_disease = Column(Integer)

    smoking_history = Column(String(20))

    bmi = Column(Float)

    HbA1c_level = Column(Float)

    blood_glucose_level = Column(Integer)

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

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who performed the action? (Could be a regular user, or an admin)
    user_id = Column(Integer, ForeignKey("users.id"),
                     nullable=False, index=True)

    # What did they do? (e.g., "user_login", "delete_prediction", "export_data")
    action = Column(String(50), nullable=False, index=True)

    # What did they affect? (e.g., "Prediction", "User")
    entity_type = Column(String(50), nullable=True)

    # The ID of the specific item they affected
    entity_id = Column(Integer, nullable=True)

    # Extra context (e.g., IP address, user-agent, or what fields were updated)
    details = Column(JSON, nullable=True)

    # When did it happen?
    timestamp = Column(DateTime(timezone=True),
                       server_default=func.now(), index=True)

    # Relationships (Optional, but helpful for ORM queries)
    user = relationship("User", backref=backref("activity_logs", cascade="all, delete-orphan"))
