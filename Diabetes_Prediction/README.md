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

## Project Structure

```text
diabetes_project/
│
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── main.py
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
