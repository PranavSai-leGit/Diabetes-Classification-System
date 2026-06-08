from utils import load_data

# Run EDA

def run_eda(df, target_column):

    basic_analysis(df)

    target_analysis(df, target_column)

    correlation_analysis(df, target_column)

    feature_engineering_analysis(df, target_column)


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
          corr.sort_values(ascending=True))


# Feature Engineering

def feature_engineering_analysis(df, target_column):
    
    df["BMI_Glucose"] = df["bmi"] * df["blood_glucose_level"]

    df["Age_BMI"] = df["age"] * df["bmi"]

    df["High_Glucose"] = (df["blood_glucose_level"] > 140).astype(int)

    df["Obese"] = (df["bmi"] >= 30).astype(int)

    df["Senior"] = (df["age"] >= 50).astype(int)

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
    return df

if __name__ == "__main__":
    df = load_data("diabetes_prediction_dataset.csv")
    run_eda(df,"Outcome")

