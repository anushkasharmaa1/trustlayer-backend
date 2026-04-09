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

from pathlib import Path
from models.response_model import FeatureBreakdown, TrustScoreResponse

MODEL_DIR   = Path(__file__).parent.parent / "models_ml"
_model      = None
_scaler     = None
_using_ml   = False

try:
    import joblib
    _model    = joblib.load(MODEL_DIR / "xgboost_model.pkl")
    _scaler   = joblib.load(MODEL_DIR / "scaler.pkl")
    _using_ml = True
    print("[TrustLayer] Loaded trained XGBoost model.")
except Exception as e:
    print(f"[TrustLayer] ML model not found ({e}). Using rule-based scoring.")

# ── Rule-based fallback ────────────────────────────────────────────────────
WEIGHT_INCOME_STABILITY      = 0.30
WEIGHT_SPENDING_CONSISTENCY  = 0.20
WEIGHT_SAVINGS_RATIO         = 0.30
WEIGHT_TRANSACTION_FREQUENCY = 0.20

def _income_stability_score(cv):
    if cv <= 0.1: return 1.0
    if cv >= 1.0: return 0.0
    return round(1.0 - (cv - 0.1) / 0.9, 4)

def _spending_consistency_score(cv):
    if cv <= 0.1: return 1.0
    if cv >= 1.0: return 0.0
    return round(1.0 - (cv - 0.1) / 0.9, 4)

def _savings_ratio_score(ratio):
    if ratio >= 0.40: return 1.0
    if ratio <= 0.0:  return 0.0
    return round(ratio / 0.40, 4)

def _frequency_score(freq):
    if freq >= 30.0: return 1.0
    if freq <= 1.0:  return 0.0
    return round((freq - 1.0) / 29.0, 4)

def _rule_based_score(features):
    composite = (
        _income_stability_score(features.income_stability)        * WEIGHT_INCOME_STABILITY      +
        _spending_consistency_score(features.spending_consistency) * WEIGHT_SPENDING_CONSISTENCY  +
        _savings_ratio_score(features.savings_ratio)               * WEIGHT_SAVINGS_RATIO         +
        _frequency_score(features.transaction_frequency)           * WEIGHT_TRANSACTION_FREQUENCY
    )
    return int(round(composite * 1000))

# ── ML scoring ────────────────────────────────────────────────────────────
def _ml_score(features):
    feature_vector = [[
        features.income_stability,
        features.spending_consistency,
        features.savings_ratio,
        features.transaction_frequency,
        features.avg_monthly_income,
        features.avg_monthly_spending,
    ]]
    scaled    = _scaler.transform(feature_vector)
    p_default = _model.predict_proba(scaled)[0][1]
    return max(0, min(1000, int(round((1 - p_default) * 1000))))

# ── Explanations + risk classification ───────────────────────────────────
def _build_explanations(features):
    explanations = []
    if features.income_stability > 0.5:
        explanations.append("High income volatility detected across months.")
    elif features.income_stability < 0.2:
        explanations.append("Stable and consistent monthly income.")
    else:
        explanations.append("Moderate income fluctuation observed.")

    if features.spending_consistency > 0.5:
        explanations.append("Irregular spending pattern with high month-to-month variance.")
    elif features.spending_consistency < 0.2:
        explanations.append("Consistent spending behavior across months.")
    else:
        explanations.append("Spending shows moderate variability.")

    if features.savings_ratio > 0.20:
        explanations.append("Consistent savings behavior — strong financial buffer.")
    elif features.savings_ratio < 0.05:
        explanations.append("Low or negative savings ratio — spending close to or above income.")
    else:
        explanations.append("Moderate savings rate relative to income.")

    if features.transaction_frequency < 5.0:
        explanations.append("Low transaction frequency — limited financial activity data.")
    else:
        explanations.append("Active transaction history provides strong scoring confidence.")

    if _using_ml:
        explanations.append("Score computed using trained XGBoost behavioral credit model.")
    else:
        explanations.append("Score computed using rule-based engine (train model for ML scoring).")

    return explanations

def _classify_risk(score):
    if score >= 700: return "low"
    if score >= 400: return "medium"
    return "high"

# ── Public API ────────────────────────────────────────────────────────────
def compute_trust_score(features: FeatureBreakdown) -> TrustScoreResponse:
    """Compute Trust Score using XGBoost (if trained) or rule-based fallback."""
    trust_score = _ml_score(features) if _using_ml else _rule_based_score(features)
    return TrustScoreResponse(
        trust_score = trust_score,
        risk_level  = _classify_risk(trust_score),
        features    = features,
        explanation = _build_explanations(features),
    )
