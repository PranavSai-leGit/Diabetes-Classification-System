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
    UserResponse,
    RoleUpdateRequest,
    UserUpdate
)
from crud import (
    create_user,
    get_user_by_email,
    save_prediction,
    get_predictions,
    data_for_dashboard,
    data_for_admin_dashboard
)
from security import (
    check_password,
    create_access_token,
    get_current_user,
    get_current_admin,
    hash_password
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
from typing import Optional, List
from datetime import datetime, timedelta


app = FastAPI()

@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type", "").startswith("text/html"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


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

# Seed default admin if no users exist
db_session = Session(bind=engine)
try:
    if db_session.query(User).count() == 0:
        default_admin = User(
            username="admin",
            email="admin@gmail.com",
            password_hash=hash_password("Password123"),
            role="admin"
        )
        db_session.add(default_admin)
        db_session.commit()
        print("Default admin created successfully: admin@gmail.com / Password123")
except Exception as e:
    print("Error seeding database:", e)
finally:
    db_session.close()

@app.get("/", tags=["Auth"])
def landing_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="Login.html",
        context={}
    )


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
        new_user = create_user(db, user)
        log_entry = ActivityLog(
            user_id=new_user.id,
            action="register_user",
            entity_type="User",
            entity_id=new_user.id,
            details={"status":"Registered successfully"}
        )
        db.add(log_entry)
        db.commit()
        return new_user

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
        log_entry = ActivityLog(
            user_id=db_user.id,
            action="failed_login_attempt",
            entity_type="User",
            entity_id=db_user.id,
            details={"reason": "Incorrect password"}
        )
        db.add(log_entry)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail='Incorrect credentials'
        )

    db_user.last_login = datetime.utcnow()
    log_entry = ActivityLog(
        user_id=db_user.id,
        action=f"{db_user.role}_login",
        entity_type="User",
        entity_id=db_user.id
    )
    db.add(log_entry)
    db.commit()

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


@app.put("/profile", tags=["User"])
def update_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # 1. Update username if provided
    if body.username is not None and body.username != current_user.username:
        # Check if username is already taken
        existing = db.query(User).filter(User.username == body.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username is already taken")
        current_user.username = body.username

    # 2. Update email if provided
    if body.email is not None and body.email != current_user.email:
        # Validate email domains
        allowed_domains = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "icloud.com"]
        email_parts = body.email.split("@")
        if len(email_parts) != 2 or email_parts[1].lower() not in allowed_domains:
            raise HTTPException(
                status_code=400,
                detail="Please use a valid Gmail, Hotmail, Yahoo, icloud, or Outlook account."
            )
        # Check if email is already taken
        existing = db.query(User).filter(User.email == body.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email is already registered")
        current_user.email = body.email

    # 3. Update password if provided
    if body.password is not None:
        current_user.password_hash = hash_password(body.password)

    # Save updates and log activity
    db.commit()
    
    log_entry = ActivityLog(
        user_id=current_user.id,
        action="update_profile",
        entity_type="User",
        entity_id=current_user.id,
        details={"updated_fields": [k for k, v in body.model_dump(exclude_unset=True).items()]}
    )
    db.add(log_entry)
    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}


@app.delete("/profile", tags=["User"], status_code=204)
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's account.
    """
    # Prevent deleting the last remaining admin account
    if current_user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the only remaining admin account."
            )

    user_id = current_user.id
    username_to_log = current_user.username
    email_to_log = current_user.email

    # Delete referencing predictions and logs to satisfy foreign key constraints
    db.query(Prediction).filter(Prediction.user_id == user_id).delete()
    db.query(ActivityLog).filter(ActivityLog.user_id == user_id).delete()

    db.delete(current_user)
    db.commit()

    # Log self-deletion inside activity_logs table under an admin user ID to satisfy foreign key constraints
    system_admin = db.query(User).filter(User.role == "admin").first()
    if system_admin:
        log_entry = ActivityLog(
            user_id=system_admin.id,
            action="delete_user",
            entity_type="User",
            entity_id=user_id,
            details={
                "deleted_username": username_to_log,
                "deleted_email": email_to_log,
                "self_delete": True
            }
        )
        db.add(log_entry)
        db.commit()

    return


# Admin routes
@app.get("/admin/home", tags=["Admin"])
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/home.html",
        context={}
    )


@app.get("/admin/profile", tags=["Admin"])
def admin_profile_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/profile.html",
        context={}
    )


@app.get("/admin/users", tags=["Admin"])
def admin_profile_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/users.html",
        context={}
    )


@app.get("/users", tags=["Admin"])
def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1),
    status: Optional[str] = None, 
    search: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_admin: User = Depends(get_current_admin)
):

    query = db.query(User)
    
    # Filter by role
    if status and status != "All":
        query = query.filter(User.role == status.lower())
        
    # Search by username or email
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    users = (
        query.order_by(User.id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = []
    for u in users:
        total_predictions = db.query(Prediction).filter(Prediction.user_id == u.id).count()
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "created_at": u.created_at.isoformat() if u.created_at else "",
            "total_predictions": total_predictions
        })

    return {
        "data": data,
        "meta": {
            "currentPage": page,
            "totalPages": total_pages,
            "totalItems": total_items
        }
    }


@app.get("/users/{user_id}", tags=["Admin"], response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found")

    return user


@app.put("/users/{user_id}/role", tags=["Admin"])
def update_user_role(
    user_id: int,
    role_data: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    # 1. Validate the requested role
    if role_data.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Must be 'user' or 'admin'"
        )

    # 2. Prevent the admin from accidentally demoting themselves
    if user_id == current_admin.id and role_data.role != "admin":
        raise HTTPException(
            status_code=400,
            detail="You cannot demote your own admin account."
        )

    # 3. Find user and update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_role = user.role
    user.role = role_data.role
    log_entry = ActivityLog(
        user_id=current_admin.id,
        action="update_user_role",
        entity_type="User",
        entity_id=user.id,
        details={"old_role": old_role, "new_role": role_data.role}
    )
    db.add(log_entry)
    db.commit()
    db.refresh(user)

    return {"message": f"User role updated to {user.role} successfully"}


@app.delete("/users/{user_id}", tags=["Admin"], status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    # Prevent admin from deleting their own account via this endpoint
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own admin account."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    username_to_log = user.username
    email_to_log = user.email

    # Delete referencing predictions and logs to satisfy foreign key constraints
    db.query(Prediction).filter(Prediction.user_id == user_id).delete()
    db.query(ActivityLog).filter(ActivityLog.user_id == user_id).delete()

    log_entry = ActivityLog(
        user_id=current_admin.id,
        action="delete_user",
        entity_type="User",
        entity_id=user_id,
        details={"deleted_username": username_to_log, "deleted_email": email_to_log}
    )
    db.add(log_entry)
    db.delete(user)
    db.commit()

    return  # 204 No Content


@app.get("/admin/predict", tags=["Admin"])
def admin_predict_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/predict.html",
        context={}
    )

@app.get("/admin_predictions", tags=["Admin"])
def show_predictions(
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Fetch a paginated list of all system predictions, with resolved usernames.
    """
    query = db.query(Prediction).join(User, Prediction.user_id == User.id)
    
    if status and status != "All":
        query = query.filter(Prediction.prediction == status)

    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    predictions = (
        query.order_by(Prediction.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = []
    for p in predictions:
        data.append({
            "id": p.id,
            "username": p.user.username if p.user else "Unknown",
            "prediction": p.prediction,
            "confidence": p.confidence,
            "created_at": p.created_at.isoformat() if p.created_at else ""
        })

    return {
        "data": data,
        "meta": {
            "currentPage": page,
            "totalPages": total_pages,
            "totalItems": total_items
        }
    }


@app.get("/admin_predictions/{user_id}", tags=["Admin"])
def show_predictions_by_id(
    user_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1),
    status: Optional[str] = None,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Fetch a paginated list of predictions for a specific user, with resolved usernames.
    """
    query = db.query(Prediction).filter(Prediction.user_id == user_id)
    if status and status != "All":
        query = query.filter(Prediction.prediction == status)

    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    predictions = (
        query.order_by(Prediction.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = []
    for p in predictions:
        data.append({
            "id": p.id,
            "username": p.user.username if p.user else "Unknown",
            "prediction": p.prediction,
            "confidence": p.confidence,
            "created_at": p.created_at.isoformat() if p.created_at else ""
        })

    return {
        "data": data,
        "meta": {
            "currentPage": page,
            "totalPages": total_pages,
            "totalItems": total_items
        }
    }


@app.get("/admin/dashboard", tags=["Admin"])
def admin_dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={}
    )


@app.get("/admin/dashboard-data", tags=["Admin"])
def admin_dashboard_data(
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return data_for_admin_dashboard(db, current_admin)


@app.get("/admin/analytics", tags=["Admin"])
def admin_profile_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin/analytics.html",
        context={}
    )


@app.get("/admin_analytics", tags=["Admin"])
def user_analytics(
    days: int = Query(7, description="Number of days to look back"),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Provides time-series data and deeper analytics for charts/graphs.
    """
    signups_by_date = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        )
        .filter(User.created_at >= func.current_date() - days)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )

    # Format the SQLAlchemy result into a clean list of dicts for JSON serialization
    formatted_signups = [
        {"date": str(row.date), "count": row.count} for row in signups_by_date]

    # Example: Prediction success rate or distribution
    prediction_distribution = (
        db.query(Prediction.status, func.count(Prediction.id))
        .group_by(Prediction.status)
        .all()
    )

    formatted_distribution = {
        status: count for status, count in prediction_distribution}

    return {
        "time_period_days": days,
        "user_signups": formatted_signups,
        "prediction_status_distribution": formatted_distribution
    }


@app.get("/admin/home-summary", tags=["Admin"])
def get_admin_home_summary(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_predictions = db.query(Prediction).count()
    total_logs = db.query(ActivityLog).count()

    # Get recent 5 activities
    recent_logs = (
        db.query(ActivityLog)
        .order_by(ActivityLog.timestamp.desc())
        .limit(5)
        .all()
    )

    activities = []
    for log in recent_logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        username = user.username if user else "System"
        activities.append({
            "id": log.id,
            "username": username,
            "action": log.action.replace("_", " ").title(),
            "timestamp": log.timestamp.isoformat(),
            "details": log.details or {}
        })

    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "total_logs": total_logs,
        "recent_activities": activities
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
