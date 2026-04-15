from fastapi import APIRouter
from services.feature_engineering import extract_features
from services.scoring_engine import compute_trust_score
from storage.memory_store import transaction_store

router = APIRouter()

@router.get("/report")
def get_report(user_id: str):

    transactions = transaction_store.load_transactions(user_id)

    if not transactions:
        return {"error": "No transactions found"}

    features = extract_features(transactions)

    score = compute_trust_score(features)

    report = {
        "trust_score": score,
        "income": features.get("avg_monthly_income", 0),
        "savings_rate": features.get("savings_ratio", 0),
        "bill_regularity": features.get("bill_regularity", 0),
        "signals": {
            "income_stability": features.get("income_stability", 0),
            "spending_consistency": features.get("spending_consistency", 0),
            "digital_payments": features.get("digital_payment_ratio", 0),
            "family_network": features.get("family_remittance_ratio", 0),
        },
        "positive_factors": [
            "Strong income stability",
            "Balanced spending"
        ],
        "negative_factors": [
            "Low savings activity"
        ]
    }

    return report