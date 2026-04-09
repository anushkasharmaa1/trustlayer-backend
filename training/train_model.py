"""
train_model.py
--------------
Train TrustLayer XGBoost model using the Kaggle
"Give Me Some Credit" dataset.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix, average_precision_score

from xgboost import XGBClassifier

RANDOM_SEED = 42
DATA_PATH = Path("datasets/cs-training.csv")
MODEL_DIR = Path("models_ml")
MODEL_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("TrustLayer — XGBoost Credit Risk Model Training")
print("=" * 60)

# ------------------------------------------------
# 1. Load Kaggle dataset
# ------------------------------------------------
df = pd.read_csv(DATA_PATH)

# rename label column
df = df.rename(columns={"SeriousDlqin2yrs": "defaulted"})

print(f"\nLoaded {len(df):,} rows")

# ------------------------------------------------
# 2. Feature Engineering
# Convert Kaggle credit features into
# behavioral TrustLayer features
# ------------------------------------------------

df["avg_monthly_income"] = df["MonthlyIncome"].fillna(df["MonthlyIncome"].median())

df["avg_monthly_spending"] = df["DebtRatio"] * df["avg_monthly_income"]

df["savings_ratio"] = 1 - df["DebtRatio"]

df["transaction_frequency"] = df["NumberOfOpenCreditLinesAndLoans"]

df["income_stability"] = 1 / (1 + df["NumberOfTimes90DaysLate"])

df["spending_consistency"] = 1 - df["RevolvingUtilizationOfUnsecuredLines"]

FEATURES = [
    "income_stability",
    "spending_consistency",
    "savings_ratio",
    "transaction_frequency",
    "avg_monthly_income",
    "avg_monthly_spending",
]

X = df[FEATURES].values
y = df["defaulted"].values

print(f"Default rate: {y.mean()*100:.2f}%")

# ------------------------------------------------
# 3. Train/Test Split
# ------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=RANDOM_SEED,
    stratify=y,
)

print(f"Train samples: {len(X_train)}")
print(f"Test samples : {len(X_test)}")

# ------------------------------------------------
# 4. Feature Scaling
# ------------------------------------------------
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ------------------------------------------------
# 5. Handle Class Imbalance
# ------------------------------------------------
neg = (y_train == 0).sum()
pos = (y_train == 1).sum()

scale_pos_weight = neg / pos

print(f"\nClass imbalance ratio: {scale_pos_weight:.2f}")

# ------------------------------------------------
# 6. Train XGBoost
# ------------------------------------------------
model = XGBClassifier(
    n_estimators=400,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric="auc",
    random_state=RANDOM_SEED,
)

print("\nTraining XGBoost...")

model.fit(X_train, y_train)

# ------------------------------------------------
# 7. Evaluate Model
# ------------------------------------------------
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)
auc_pr = average_precision_score(y_test, y_prob)

print("\nAUC ROC:", round(auc, 4))
print("AUC PR :", round(auc_pr, 4))

print("\nClassification Report")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix")
print(confusion_matrix(y_test, y_pred))

# ------------------------------------------------
# 8. Cross Validation
# ------------------------------------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

cv_scores = cross_val_score(
    model,
    scaler.transform(X),
    y,
    cv=cv,
    scoring="roc_auc",
)

print("\nCV AUC:", cv_scores.mean())

# ------------------------------------------------
# 9. Feature Importance
# ------------------------------------------------
importances = dict(zip(FEATURES, model.feature_importances_))

print("\nFeature Importance:")
for k, v in sorted(importances.items(), key=lambda x: x[1], reverse=True):
    print(k, round(float(v), 4))

# ------------------------------------------------
# 10. Save Model
# ------------------------------------------------
joblib.dump(model, MODEL_DIR / "xgboost_model.pkl")
joblib.dump(scaler, MODEL_DIR / "scaler.pkl")

metadata = {
    "features": FEATURES,
    "auc": float(auc),
    "cv_auc": float(cv_scores.mean()),
}

with open(MODEL_DIR / "model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("\nModel saved to:", MODEL_DIR)
print("Training complete")