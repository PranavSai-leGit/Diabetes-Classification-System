import joblib
from imblearn.under_sampling import RandomUnderSampler

from sklearn.metrics import accuracy_score, classification_report, recall_score
from sklearn.model_selection import GridSearchCV, train_test_split

from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

from preprocessing import preprocess_data
from eda import run_eda
from utils import load_data

import os

os.system("cls" if os.name == "nt" else "clear")

# -----Loading Dataset-----

df = load_data(r"Diabetes_Prediction\data\Raw\diabetes_prediction_dataset.csv")


# -----Running analysis-----

run_eda(df, "Outcome")


# -----Preprocessing-----

X, y = preprocess_data(df, "Outcome")


# -----Train-Test split-----

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -----Dataset balancing-----

rus = RandomUnderSampler(
    sampling_strategy=0.33,
    random_state=42,
    replacement=False
)
X_rus, y_rus = rus.fit_resample(X_train, y_train)


# -----Defining models-----

rf = RandomForestClassifier(
    random_state=42
)
rf_params = {
    "n_estimators": [100, 200],
    "max_depth": [5, 10, None],
}

xgb = XGBClassifier(
    scale_pos_weight = 3,
    random_state=42,
    eval_metric="logloss"
)
xgb_params = {
    "n_estimators": [100, 200, 500],
    "max_depth": [3, 5, 7, 10],
    "learning_rate": [0.025, 0.05],
}

svc = SVC()
svc_params = {
    "C": [0.1, 1, 10],
    "kernel": ["linear", "rbf"],
    "gamma": ["scale", "auto"]
}


# -----Grid Search CV-----

def run_grid_search(model, params, X_train, y_train):
    grid = GridSearchCV(
        estimator=model,
        param_grid=params,
        cv=5,
        scoring="recall",
        n_jobs=-1,
        verbose=0
    )
    grid.fit(X_train, y_train)

    return grid.best_estimator_, grid.best_score_, grid.best_params_

results = []


# -----Running Grid Search CV-----

rf_best, rf_score, rf_params_best = run_grid_search(
    rf, rf_params, X_train, y_train
)

results.append(("RandomForest", rf_best, rf_score))

xgb_best, xgb_score, xgb_params_best = run_grid_search(
    xgb, xgb_params, X_train, y_train
)

results.append(("XGBoost", xgb_best, xgb_score))

svc_best, svc_score, svc_params_best = run_grid_search(
    svc, svc_params, X_train, y_train
)

results.append(("SVC", svc_best, svc_score))


# -----Testing best_model-----

print("\nMODEL COMPARISON (based on Recall):\n")

for name, model, score in results:
    print(name, "-> Recall:", score)

best_model = max(results, key=lambda x: x[2])[1]

y_pred = best_model.predict(X_test)

print("\nFINAL MODEL PERFORMANCE:\n")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred))
print(xgb_params_best)


# -----Saving best_model-----

joblib.dump(best_model, r'Diabetes_Prediction\models\diabetes_model.pkl')


