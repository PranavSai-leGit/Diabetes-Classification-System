from fastapi import (
    FastAPI,
    Request,
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
from sqlalchemy.orm import Session
from models import User


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


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
)


@app.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.get("/predict")
def predict_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="predict.html",
        context={}
    )

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

    token = create_access_token(data = {"sub": str(db_user.id)})

    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(input: PredictionInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    try:

        df = pd.DataFrame([input.model_dump()])

        result = make_prediction(df)

        save_prediction(db, current_user.id, result)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/history")
def history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    return get_predictions(db, current_user.id)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
