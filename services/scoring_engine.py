"""
scoring_engine.py
-----------------
Computes a deterministic Trust Score (0-1000) from behavioral features.

Model strategy:
  - Tries to load the trained XGBoost model from models_ml/xgboost_model.pkl
  - If the model file is not found (e.g. first run before training),
    falls back to the rule-based weighted scoring engine automatically.
  - This means the API works out of the box, and gets smarter after training.

Score derivation:
  XGBoost outputs a probability of default (0-1).
  We invert and scale: Trust Score = (1 - P(default)) * 1000
  This means a lower default probability = higher trust score.
"""
import json
import joblib
import numpy as np
from pathlib import Path
from services.feature_engineering import detect_anomalies
from models.response_model import TrustScoreResponse, FeatureBreakdown


MODEL_DIR   = Path(__file__).parent.parent / "models_ml"
_model      = None
_scaler     = None
_features   = None
_using_ml   = False

try:
    import joblib
    _model    = joblib.load(MODEL_DIR / "xgboost_model.pkl")
    _scaler   = joblib.load(MODEL_DIR / "scaler.pkl")
    with open(MODEL_DIR / "model_metadata.json") as f:
        _features = json.load(f)["features"]
    _using_ml = True
    print("[TrustLayer] Loaded trained XGBoost model.")
except Exception as e:
    print(f"[TrustLayer] ML model not found ({e}). Using rule-based scoring.")

# ── Rule-based fallback ────────────────────────────────────────────────────
WEIGHT_INCOME_REGULARITY      = 0.20
WEIGHT_INCOME_DIVERSITY       = 0.15
WEIGHT_ESSENTIAL_SPEND        = 0.15
WEIGHT_SAVINGS_FREQUENCY      = 0.20
WEIGHT_CASH_WITHDRAWAL        = -0.15  # Negative weight since higher is worse
WEIGHT_AVG_INCOME             = 0.15

def _income_regularity_score(variance):
    if variance <= 10: return 1.0  # Low variance = regular
    if variance >= 100: return 0.0
    return round(1.0 - (variance - 10) / 90, 4)

def _income_diversity_score(count):
    if count >= 5: return 1.0
    if count <= 1: return 0.0
    return round((count - 1) / 4, 4)

def _essential_spend_score(ratio):
    if ratio <= 0.3: return 1.0  # Low essential spend = flexible
    if ratio >= 0.8: return 0.0
    return round(1.0 - (ratio - 0.3) / 0.5, 4)

def _savings_frequency_score(freq):
    if freq >= 2.0: return 1.0
    if freq <= 0.0: return 0.0
    return round(freq / 2.0, 4)

def _cash_withdrawal_score(ratio):
    if ratio <= 0.1: return 1.0
    if ratio >= 0.5: return 0.0
    return round(1.0 - (ratio - 0.1) / 0.4, 4)

def _avg_income_score(income):
    if income >= 50000: return 1.0
    if income <= 10000: return 0.0
    return round((income - 10000) / 40000, 4)

def _rule_based_score(features):
    composite = (
        _income_regularity_score(features.income_regular_day_variance) * WEIGHT_INCOME_REGULARITY +
        _income_diversity_score(features.income_source_count) * WEIGHT_INCOME_DIVERSITY +
        _essential_spend_score(features.essential_spend_ratio) * WEIGHT_ESSENTIAL_SPEND +
        _savings_frequency_score(features.savings_transfer_frequency) * WEIGHT_SAVINGS_FREQUENCY +
        _cash_withdrawal_score(features.cash_withdrawal_ratio) * WEIGHT_CASH_WITHDRAWAL +
        _avg_income_score(features.avg_monthly_income) * WEIGHT_AVG_INCOME
    )
    return int(round(max(0, min(1, composite)) * 1000))

# ── ML scoring ────────────────────────────────────────────────────────────
def _ml_score(features):
    # Feature order must match the trained model's expectations from model_metadata.json
    feature_vector = [[
        features.transaction_frequency,      # 1. transaction_frequency
        features.income_source_count,        # 2. income_source_count
        features.avg_monthly_income,         # 3. avg_income
        features.income_regular_day_variance, # 4. income_variance
        features.essential_spend_ratio,      # 5. essential_spend_ratio
        features.cash_withdrawal_ratio,      # 6. cash_withdrawal_ratio
    ]]
    scaled    = _scaler.transform(feature_vector)
    p_default = _model.predict_proba(scaled)[0][1]
    trust_score = int(round((1 - p_default) * 1000))
    return max(0, min(1000, trust_score))

# ── Explanations + risk classification ───────────────────────────────────
def _build_signals(features):
    """Build positive and risk signals based on features."""
    positive = []
    risk = []
    
    if features.income_regular_day_variance < 50:
        positive.append("consistent weekly income")
    else:
        risk.append("irregular income timing")
    
    if features.income_source_count > 3:
        positive.append("multiple income sources")
    elif features.income_source_count == 1:
        risk.append("single income source")
    
    if features.essential_spend_ratio < 0.5:
        positive.append("balanced spending")
    else:
        risk.append("high essential spending")
    
    if features.savings_transfer_frequency > 1:
        positive.append("regular savings transfers")
    else:
        risk.append("infrequent savings")
    
    if features.cash_withdrawal_ratio > 0.2:
        risk.append("high cash withdrawals")
    
    if features.avg_monthly_income > 30000:
        positive.append("strong average income")
    
    return positive, risk

def _build_explanations(features, positive_signals, risk_signals):
    explanations = []
    
    if positive_signals:
        explanations.append(f"Positive factors: {', '.join(positive_signals)}")
    if risk_signals:
        explanations.append(f"Risk factors: {', '.join(risk_signals)}")
    
    if _using_ml:
        explanations.append("Score computed using trained XGBoost behavioral model.")
    else:
        explanations.append("Score computed using rule-based engine (train model for ML scoring).")
    
    return explanations

def _classify_risk(score):
    if score >= 750: return "Low Risk"
    elif score >= 600: return "Moderate Risk"
    elif score >= 450: return "High Risk"
    else: return "Very High Risk"

# ── Public API ────────────────────────────────────────────────────────────
def compute_trust_score(features: FeatureBreakdown, transactions: list[dict] | None = None) -> TrustScoreResponse:
    """Compute Trust Score using XGBoost (if trained) or rule-based fallback."""
    trust_score = _ml_score(features) if _using_ml else _rule_based_score(features)
    positive_signals, risk_signals = _build_signals(features)
    
    warnings = []
    if transactions:
        warnings = detect_anomalies(transactions)
    
    explanation = _build_explanations(features, positive_signals, risk_signals)
    if warnings:
        explanation.extend([f"Warning: {w}" for w in warnings])
    
    return TrustScoreResponse(
        trust_score = trust_score,
        risk_level  = _classify_risk(trust_score),
        top_positive_signals = positive_signals,
        risk_signals = risk_signals,
        features    = features,
        explanation = explanation,
    )
