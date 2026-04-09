"""
response_model.py
-----------------
Pydantic models that define the structured JSON shape of every API response.
All endpoints return one of these models — never raw dicts.
"""

from pydantic import BaseModel, Field
from typing import Literal


class FeatureBreakdown(BaseModel):
    """Computed behavioral features used to derive the Trust Score."""

    income_stability: float = Field(
        ..., description="Coefficient of variation of income (lower = more stable)."
    )
    spending_consistency: float = Field(
        ..., description="Coefficient of variation of spending (lower = more consistent)."
    )
    savings_ratio: float = Field(
        ..., description="Net savings as a fraction of total income (higher = better)."
    )
    transaction_frequency: float = Field(
        ..., description="Average number of transactions per month."
    )
    avg_monthly_income: float = Field(
        ..., description="Mean monthly credit (income) in INR."
    )
    avg_monthly_spending: float = Field(
        ..., description="Mean monthly debit (spending) in INR."
    )


class TrustScoreResponse(BaseModel):
    """Standard Trust Score response returned by /get-score and /simulate."""

    trust_score: int = Field(
        ..., ge=0, le=1000, description="Composite behavioral credit score (0-1000)."
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        ..., description="Derived risk classification based on trust_score."
    )
    features: FeatureBreakdown
    explanation: list[str] = Field(
        ..., description="Human-readable summary of factors driving the score."
    )


class UploadResponse(BaseModel):
    """Returned after a successful transaction upload."""

    message: str
    user_id: str
    transactions_stored: int


class SimulationResponse(TrustScoreResponse):
    """Extends TrustScoreResponse with simulation delta metadata."""

    original_score: int = Field(..., description="Score before applying hypothetical changes.")
    score_delta: int = Field(..., description="Difference: simulated_score - original_score.")
