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
│   ├── components/
│   │   └── sidebar.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── predict.html
│
├── static/
│   ├── css/
│   │   ├── auth.css
│   │   ├── predict.css
│   │   └── sidebar.html
│   │
│   ├── images/
│   │   ├── favicon.png
│   │   └── Login.jpg
│   │
│   └── js/
│       ├── login.js
│       ├── register.js
│       ├── predict.js
│       └── sidebar.html
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
