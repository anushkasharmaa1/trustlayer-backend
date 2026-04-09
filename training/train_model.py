import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv("datasets/trustlayer_training_data.csv")

X = df.drop(columns=["risk_label", "user_id"])
y = df["risk_label"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05
)

model.fit(X_train, y_train)

pred = model.predict_proba(X_test)[:,1]

print("AUC:", roc_auc_score(y_test, pred))

joblib.dump(model, "models_ml/xgboost_model.pkl")
joblib.dump(scaler, "models_ml/scaler.pkl")

# Save model metadata
import json
metadata = {
    "features": list(X.columns),
    "model_type": "XGBoost Classifier",
    "n_estimators": model.n_estimators,
    "max_depth": model.max_depth,
    "auc_score": roc_auc_score(y_test, pred)
}
with open("models_ml/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("Model trained successfully")