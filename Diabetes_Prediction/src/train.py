
    if "smoking_history" in df.columns:
        smoking_encoder = LabelEncoder()
        df["smoking_history"] = smoking_encoder.fit_transform(df["smoking_history"])