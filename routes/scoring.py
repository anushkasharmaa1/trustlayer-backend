"""
routes/scoring.py
-----------------
GET /get-score?user_id=...
Returns the Trust Score, risk level, feature breakdown, and explanations
for a user based on their stored transaction history.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import verify_api_key
from app.database import load_transactions
from models.response_model import TrustScoreResponse
from services.feature_engineering import extract_features
from services.scoring_engine import compute_trust_score

router = APIRouter()


@router.get(
    "/get-score",
    response_model=TrustScoreResponse,
    summary="Compute Trust Score for a user",
)
async def get_score(
    user_id: str = Query(..., description="User ID to score."),
    _: str = Depends(verify_api_key),
):
    """
    Computes and returns a Trust Score for the specified user.

    - Loads stored transaction history.
    - Runs feature engineering and scoring pipeline.
    - Returns structured JSON with score, risk level, features, and explanations.
    """
    transactions = await load_transactions(user_id)

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No transaction history found for user '{user_id}'. "
                   "Upload transactions first via POST /upload-transactions.",
        )

    features = extract_features(transactions)
    result   = compute_trust_score(features)

    return result
