from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)
from schemas import (
    PredictionInput,
    PredictionResponse,
    UserCreate,
    UserLogin
)
from crud import (
    create_user,
    get_user_by_email,
    save_prediction,
    get_predictions
)
import pandas as pd
from database import engine, Base, get_db
from src.predict import predict as make_prediction
from sqlalchemy.orm import Session
from models import User


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():

    return {'message': 'Diabetes Prediction System'}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already registered"
        )

    try:
        return create_user(db, user)

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    if user.password != db_user.password:
        raise HTTPException(
            status_code=401,
            detail='Incorrect credentials'
        )

    return {
        'message': 'Login Success',
        'user_id': db_user.id
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(input: PredictionInput, user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    try:

        df = pd.DataFrame([input.model_dump()])

        result = make_prediction(df)

        save_prediction(db, user_id, result)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/history/{user_id}")
def history(user_id: int, db: Session = Depends(get_db)):

    return get_predictions(db, user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
