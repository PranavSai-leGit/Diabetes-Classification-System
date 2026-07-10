# Diabetes-Classification-System
Diabetes Classification System using machine learning

A FastAPI-based machine learning application that predicts whether a person is diabetic based on health-related features.

## Features

- User input validation using Pydantic
- Diabetes prediction using a trained ML model
- FastAPI REST API
- PostgreSQL database integration
- Prediction history storage
- Swagger API documentation

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pandas
- Scikit-Learn
- Pydantic
- Uvicorn
- HTML
- CSS
- Javascript

## Project Structure

```text
diabetes_project/
│
├── main.py
├── schemas.py
├── database.py
├── models.py
├── crud.py
├── security.py
│
├── templates/
│   ├── admin/
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── predict.html
│   │   ├── profile.html
│   │   └── sidebar.html
│   ├── components/
│   │   └── sidebar.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── dashboard.html
│   ├── predict.html
│   ├── history.html
│   └── profile.html
│
├── static/
│   ├── css/
│   │   ├── admin/
│   │   │   ├── home.html
│   │   │   ├── dashboard.html
│   │   │   ├── users.html
│   │   │   ├── predict.html
│   │   │   ├── profile.html
│   │   │   └── sidebar.html
│   │   ├── auth.css
│   │   ├── home.css
│   │   ├── dashboard.css
│   │   ├── predict.css
│   │   ├── history.css
│   │   ├── profile.css
│   │   └── sidebar.html
│   │
│   ├── images/
│   │   ├── favicon.png
│   │   ├── Profile-icon.webp
│   │   └── Background.jpg
│   │
│   └── js/
│       ├── admin/
│       │   ├── auth-guard.js
│       │   ├── dashboard.js
│       │   ├── predictions.js
│       │   ├── users.js
│       │   ├── predict.js
│       │   ├── profile.js
│       │   └── sidebar.js
│       ├── login.js
│       ├── register.js
│       ├── dashboard.js
│       ├── predict.js
│       ├── history.js
│       ├── profile.js
│       ├── user-guard.js
│       └── sidebar.js
│   
├── src/
│   ├── predict.py
│   ├── utils.py
│   ├── train.py
│   ├── eda.py
│   └── preprocessing.py
│
├── models/
│   ├── diabetes_model.pkl
│   ├── encoder.pkl
│   └── feature_column.pkl
│
├── requirements.txt
└── README.md
```

## Author

Pranav Sai Pathipati
