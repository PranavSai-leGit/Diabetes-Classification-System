
from preprocessing import load_data, preprocess_data
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, recall_score
import matplotlib.pyplot as plt
import numpy as np

df = load_data("Practice\diabetes_prediction_dataset.csv")
X, y = preprocess_data(df, 'Outcome')
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Handle imbalance
scale_pos_weight = (sum(y_train == 0)/sum(y_train == 1))

# Model
model = XGBClassifier(
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

# Probabilities
probs = model.predict_proba(X_test)[:, 1]

# Threshold tuning
best_threshold = 0.5
best_recall = 0

for threshold in np.arange(0.2, 0.8, 0.05):

    preds = (probs >= threshold).astype(int)
    recall = recall_score(y_test, preds)
    if recall > best_recall:
        best_recall = recall
        best_threshold = threshold

# Final prediction
y_pred = (probs >= best_threshold).astype(int)
print("Best Threshold:", best_threshold)
print(classification_report(y_test, y_pred))
print("accuracy:", accuracy_score(y_test, y_pred))
print(df["bmi"].describe())

plt.boxplot(df["bmi"])
plt.show()
