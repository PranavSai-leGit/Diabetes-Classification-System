from models import User, Prediction
from security import hash_password

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
        prediction = result['prediction'],
        confidence = result['confidence']
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    return pred

def get_predictions(db, user_id):

    return (
        db.query(Prediction).filter(Prediction.user_id == user_id).all()
    )