from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    Query,
    Depends
)
from schemas import (
    PredictionInput,
    PredictionResponse,
    UserCreate,
    UserResponse
)
from crud import (
    create_user,
    get_user_by_email,
    save_prediction,
    get_predictions,
    data_for_dashboard
)
from security import (
    check_password,
    create_access_token,
    get_current_user
)
from database import (
    engine,
    Base,
    get_db
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from src.predict import predict as make_prediction
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import User, Prediction, ActivityLog
from typing import Optional


app = FastAPI()

# Jinja Template initiation (HTML)
templates = Jinja2Templates(
    directory="templates"
)

# Mounting Static file to jinja template (CSS, JS, Images)
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# Creating new table with metadata from basemodel
Base.metadata.create_all(bind=engine)



@app.get("/register", tags=["Auth"])
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


@app.post("/register", tags=["Auth"])
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


@app.get("/login", tags=["Auth"])
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.post("/login", tags=["Auth"])
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    db_user = get_user_by_email(db, user.username)

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    if not check_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail='Incorrect credentials'
        )

    token = create_access_token(data={
        "sub": str(db_user.id),
        "role": (db_user.role)
    })

    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@app.get("/home", tags=["User"])
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )


@app.get("/dashboard", tags=["User"])
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={}
    )


@app.get("/dashboard-data", tags=["User"])
def get_dashboard_data(db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    # Calls the data_for_dashboard function we built in crud.py
    data = data_for_dashboard(db, user_id=current_user.id)
    return data


@app.get("/predict", tags=["User"])
def predict_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="predict.html",
        context={}
    )


@app.post("/predict", tags=["User"], response_model=PredictionResponse)
def predict(input: PredictionInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    try:
        input_data = input.model_dump()

        df = pd.DataFrame([input_data])

        result = make_prediction(df)

        pred_df = {
            **input_data,
            **result
        }

        new_prediction = save_prediction(db, current_user.id, pred_df)
        log_entry = ActivityLog(
            user_id=current_user.id,
            action="create_prediction",
            entity_type="Prediction",
            entity_id=new_prediction.id,
        )

        db.add(log_entry)
        db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

@app.get("/history_page", tags=["User"])
def history_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={}
    )


@app.get("/history", tags=["User"])
def history(page: int = Query(1, ge=1), limit: int = Query(7, ge=1, le=7), status: Optional[str] = None,  current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    return get_predictions(db, current_user.id, page, limit, status)


@app.get("/profile_page", tags=["User"])
def profile_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={}
    )


@app.get("/profile", tags=["User"])
def profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    return current_user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
