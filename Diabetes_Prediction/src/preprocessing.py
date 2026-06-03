from sklearn.preprocessing import LabelEncoder
from scipy.stats import zscore
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
os.system("cls")


# Load Data

def load_data(path: str):

    try:
        return pd.read_csv(path)

    except FileNotFoundError:
        print("Dataset not found")
        return None


# Run EDA

def run_eda(df, target_column):

    basic_analysis(df)

    target_analysis(df, target_column)

    correlation_analysis(df, target_column)

    df_fe = feature_engineering(df.copy())

    feature_engineering_analysis(df_fe, target_column)


# Basic Analysis

def basic_analysis(df):

    print("Dataset Shape :", df.shape)
    print('\n')
    print("First 5 Rows :\n", df.head())
    print('\n')
    print("Data Types :\n", df.dtypes)
    print('\n')
    print("Summary Statistics :\n", df.describe())
    print('\n')
    print("Missing Values :\n", df.isnull().sum())
    print('\n')
    print("Duplicates :", df.duplicated().sum())


# Target Analysis

def target_analysis(df, target_column):

    if target_column not in df.columns:
        return

    print("\nTarget Distribution:")
    print(df[target_column].value_counts())

    print("\nTarget Percentage:")
    print(df[target_column].value_counts(normalize=True)*100)


# Correlation Analysis

def correlation_analysis(df, target_column):

    numeric_df = df.select_dtypes(include=["int64", "float64"])

    corr = numeric_df.corr()[target_column]
    print(f"\nCorrelation With {target_column}: \n",
          corr.sort_values(ascending=False))


# Undersampling

def undersampling(df, target_column):

    majority = df[df[target_column] == 0]
    minority = df[df[target_column] == 1]

    majority_under = majority.sample(n=3*len(minority), random_state=42)
    balanced_df = pd.concat([majority_under, minority])

    return balanced_df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=true)


# Feature Engineering

def feature_engineering_analysis(df, target_column):

    if target_column not in df.columns:
        return

    print("\n\nFeature Engineering Analysis: \n")

    engineered_features = [
        "BMI_Glucose",
        "Age_BMI",
        "High_Glucose",
        "Obese",
        "Senior"
    ]

    for feature in engineered_features:

        if feature in df.columns:

            corr = df[[feature, target_column]].corr().iloc[0, 1]

            print(
                f"{feature} correlation "
                f"with {target_column}: "
                f"{corr:.4f}"
                "\n"
            )


# Undersampling

def undersampling(df, target_column):

    majority = df[df[target_column] == 0]
    minority = df[df[target_column] == 1]

    majority_downsampled = majority.sample(
        n=len(minority),
        random_state=42
    )

    balanced_df = pd.concat(
        [majority_downsampled, minority]
    )

    return balanced_df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)


# Handling missing values

def handle_missing_values(df):

    numeric_cols = df.select_dtypes(include=["number"]).columns

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    return df


# Removing duplicates

def remove_duplicates(df):

    return df.drop_duplicates()


# Handling Outliers

def handling_outliers(df):

    for col in ["age", "bmi"]:

        if col in df.columns:

            z = zscore(df[col])
            df = df[abs(z) <= 3]

    return df


# Encoding

def encode_features(df):
    if "gender" in df.columns:

        gender_encoder = LabelEncoder()
        df["gender"] = gender_encoder.fit_transform(df["gender"])

    if "smoking_history" in df.columns:

        smoking_encoder = LabelEncoder()
        df["smoking_history"] = smoking_encoder.fit_transform(
            df["smoking_history"])

    return df


# Feature Engineering

def feature_engineering(df):

    df["BMI_Glucose"] = df["bmi"] * df["blood_glucose_level"]

    df["Age_BMI"] = df["age"] * df["bmi"]

    df["High_Glucose"] = (df["blood_glucose_level"] > 140).astype(int)

    df["Obese"] = (df["bmi"] >= 30).astype(int)

    df["Senior"] = (df["age"] >= 50).astype(int)

    return df


# Feature / Target split

def split_features_target(df, target_column):

    X = df.drop(columns=[target_column])

    y = df[target_column]

    return X, y


# Saving Processed Data

def save_processed_data(df):

    os.makedirs("Data/Processed", exist_ok=True)

    df.to_csv("Data/Processed/processed_data.csv", index=False)


# Master Function

def preprocess_data(df, target_column):

    df = undersampling(df, target_column)
    df = handle_missing_values(df)

    df = remove_duplicates(df)

    df = handling_outliers(df)

    df = encode_features(df)

    df = feature_engineering(df)

    save_processed_data(df)

    X, y = split_features_target(df, target_column)

    return X, y


if __name__ == "__main__":
    df = load_data(
        'Diabetes_Prediction\data\Raw\diabetes_prediction_dataset.csv')
    run_eda(df, "Outcome")
    preprocess_data(df, "Outcome")
