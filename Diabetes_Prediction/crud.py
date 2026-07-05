from sqlalchemy.orm import Session
from models import User, Prediction
from security import hash_password
from schemas import filter_input
import math
from sqlalchemy import func

def create_user(db, user):

    password_hash = hash_password(user.password)
    new_user = User(
        username = user.username,
        email = user.email,
        password_hash = password_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user_by_email(db, email):

    return (
        db.query(User).filter(User.email == email).first()
    )

def save_prediction(db, user_id, result):

    pred = Prediction(
        user_id = user_id,
        gender = result['gender'],
        age = result['age'],
        hypertension = result['hypertension'],
        heart_disease = result['heart_disease'],
        smoking_history = result['smoking_history'],
        bmi = result['bmi'],
        HbA1c_level = result['HbA1c_level'],
        blood_glucose_level = result['blood_glucose_level'],
        prediction = result['prediction'],
        confidence = result['confidence']
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    return pred

def get_predictions(db, user_id, page: int = 1, limit: int = 7, status: filter_input = None):

    offset = (page-1)*limit

    query = db.query(Prediction).filter(Prediction.user_id == user_id)
    # Only for display in dashboard
    total_predictions = query.count()

    latest_prediction = (
        query
        .order_by(Prediction.id.desc())
        .first()
    )

    average_confidence = (
        db.query(func.avg(Prediction.confidence))
        .filter(Prediction.user_id == user_id)
        .scalar()
    )

    if(status) :
        query = query.filter(Prediction.prediction == status)
    
        
    total_items = query.count()

    predictions = (
        query
        .order_by(Prediction.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
        )
    total_pages = math.ceil(total_items/limit)

    return {
        "data": predictions,
        "meta": {
            "currentPage": page,
            "itemsPerPage": limit,
            "totalItems": total_items,
            "totalPages": total_pages,
            "total_predictions": total_predictions,
            "average_confidence": average_confidence,
            "latest_prediction": latest_prediction
        }
    }


def data_for_dashboard(db: Session, user_id: int):
    # Fetch all predictions for the user to aggregate
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.id.desc())
        .all()
    )

    total_predictions = len(predictions)

    if total_predictions == 0:
        return {"message": "No data available"}

    # Basic Stats
    total_positives = sum(1 for p in predictions if p.prediction in [
                          "Diabetic", "Positive", "1"])
    total_negatives = total_predictions - total_positives

    # FIX: Added 'or 0' in case confidence is None in the database
    avg_confidence = sum((p.confidence or 0) for p in predictions) / \
        total_predictions if total_predictions > 0 else 0

    latest = predictions[0]

    # Initialize aggregations
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    age_bins = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0}
    gender_counts = {"Male": 0, "Female": 0}
    bmi_bins = {"Normal": 0, "Overweight": 0, "Obese": 0}

    # Glucose by age group (Sum and Count for average)
    gluc_age_data = {
        "20-30": {"sum": 0, "count": 0},
        "31-40": {"sum": 0, "count": 0},
        "41-50": {"sum": 0, "count": 0},
        "51-60": {"sum": 0, "count": 0},
    }

    scatter_pos = []
    scatter_neg = []

    for p in predictions:
        # Risk Distribution Logic
        is_positive = p.prediction in ["Diabetic", "Positive", "1"]
        # FIX: Ensure confidence isn't None before comparing
        if is_positive and (p.confidence or 0) >= 0.8:
            risk_counts["high"] += 1
        elif is_positive:
            risk_counts["medium"] += 1
        else:
            risk_counts["low"] += 1

        # Age Group Distribution
        if p.age:
            if p.age <= 20:
                age_bins["0-20"] += 1
            elif p.age <= 40:
                age_bins["21-40"] += 1
            elif p.age <= 60:
                age_bins["41-60"] += 1
            else:
                age_bins["61-80"] += 1

        # Gender
        if str(p.gender).lower() in ["m", "male", "1"]:
            gender_counts["Male"] += 1
        else:
            gender_counts["Female"] += 1

        # BMI Distribution
        if p.bmi is not None:
            if p.bmi < 25:
                bmi_bins["Normal"] += 1
            elif p.bmi < 30:
                bmi_bins["Overweight"] += 1
            else:
                bmi_bins["Obese"] += 1

        # Glucose by Age (Avg)
        if p.blood_glucose_level is not None and p.age is not None:
            if 20 <= p.age <= 30:
                gluc_age_data["20-30"]["sum"] += p.blood_glucose_level
                gluc_age_data["20-30"]["count"] += 1
            elif 31 <= p.age <= 40:
                gluc_age_data["31-40"]["sum"] += p.blood_glucose_level
                gluc_age_data["31-40"]["count"] += 1
            elif 41 <= p.age <= 50:
                gluc_age_data["41-50"]["sum"] += p.blood_glucose_level
                gluc_age_data["41-50"]["count"] += 1
            elif 51 <= p.age <= 60:
                gluc_age_data["51-60"]["sum"] += p.blood_glucose_level
                gluc_age_data["51-60"]["count"] += 1

        # Scatter Plot Data
        if p.blood_glucose_level is not None:
            if is_positive:
                scatter_pos.append({"x": p.blood_glucose_level, "y": 1})
            else:
                scatter_neg.append({"x": p.blood_glucose_level, "y": 0})

    # Convert counts to percentages / averages for the frontend
    def to_pct(count): return round(
        (count / total_predictions) * 100) if total_predictions else 0

    def to_avg(data_dict): return round(
        data_dict["sum"] / data_dict["count"]) if data_dict["count"] > 0 else 0

    return {
        "stats": {
            "total_predictions": total_predictions,
            "average_confidence": round(avg_confidence * 100, 1),
            "total_positives": total_positives,
            "total_negatives": total_negatives
        },
        "latest_prediction": {
            "prediction": latest.prediction,
            "confidence": round((latest.confidence or 0) * 100, 1),
            "created_at": latest.created_at.isoformat() if hasattr(latest.created_at, 'isoformat') else str(latest.created_at)
        },
        "risk_scores": {
            "low": to_pct(risk_counts["low"]),
            "medium": to_pct(risk_counts["medium"]),
            "high": to_pct(risk_counts["high"])
        },
        "age_distribution": [
            to_pct(age_bins["0-20"]),
            to_pct(age_bins["21-40"]),
            to_pct(age_bins["41-60"]),
            to_pct(age_bins["61-80"])
        ],
        "gender_distribution": [
            gender_counts["Male"],
            gender_counts["Female"]
        ],
        "bmi_distribution": [
            to_pct(bmi_bins["Normal"]),
            to_pct(bmi_bins["Overweight"]),
            to_pct(bmi_bins["Obese"])
        ],
        "glucose_by_age": [
            to_avg(gluc_age_data["20-30"]),
            to_avg(gluc_age_data["31-40"]),
            to_avg(gluc_age_data["41-50"]),
            to_avg(gluc_age_data["51-60"])
        ],
        "scatter_data": {
            "positive": scatter_pos,
            "negative": scatter_neg
        },
        "recent_predictions": [
            {
                "age": p.age or 0,
                # FIX: Check for None before rounding
                "bmi": round(p.bmi, 1) if p.bmi is not None else 0,
                # FIX: Changed p.glucose to p.blood_glucose_level and checked for None
                "glucose": round(p.blood_glucose_level, 1) if p.blood_glucose_level is not None else 0,
                "result": "Positive" if p.prediction in ["Diabetic", "Positive", "1"] else "Negative"
            } for p in predictions[:5]
        ]
    }
